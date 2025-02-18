# app/api.py
from flask import Blueprint, request, jsonify, send_file, current_app
import time
import base64
import io
import os
import uuid
import logging
import json
from datetime import datetime

from PIL import Image, ImageDraw
from config import Config  # Assuming you have a Config class
from app.db import get_db_connection, close_db_connection  # Import from db.py
from models.yolo import predict_with_yolo, load_yolo_model
from models.cnn import predict_with_cnn, load_cnn_model, preprocess_image_for_cnn
from preprocessing import preprocess_image_for_yolo


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bp = Blueprint('api', __name__)

# --- Helper Functions (Defined *within* api.py) ---
def save_image(image_bytes, upload_folder, filename):
    """Saves an image to the specified folder and sets correct permissions."""

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)  # Ensure directory exists

    image_path = os.path.join(upload_folder, filename)

    try:
        with open(image_path, 'wb') as f:  # Open in binary write mode
            f.write(image_bytes)

        # Set permissions AFTER saving the file (THIS IS THE KEY FIX)
        os.chmod(image_path, 0o644)  # Set permissions to rw-r--r-- (644 in octal)

        return image_path

    except Exception as e:
        print(f"Error in save_image: {e}")  # More specific error logging
        raise  # Re-raise the exception to be caught in the calling function

# --- Routes ---

# Load models globally, but handle potential failures
yolo_model = load_yolo_model()  # Ensure these functions exist and handle loading
cnn_model = load_cnn_model()

@bp.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    current_app.logger.info("Received /predict request")

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image provided'}), 400

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in image_file.filename or image_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid image format'}), 400

    image_bytes = image_file.read()
    original_filename = image_file.filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]

    try:
        image_path = save_image(image_bytes, Config.UPLOAD_FOLDER, unique_filename)
        current_app.logger.info(f"Image saved to: {image_path}")
    except Exception as e:
        current_app.logger.error(f"Error saving image: {e}")
        print(image_path)
        return jsonify({'error': 'Failed to save image'}), 500


    model_type = request.form.get('model_type')
    if not model_type:
        return jsonify({'error': 'model_type is required'}), 400

    if model_type == 'cnn':
        # CNN Prediction
        input_tensor = preprocess_image_for_cnn(image_bytes) # preprocess here
        if input_tensor is None:
            return jsonify({'error': 'Failed to preprocess image for CNN'}), 500
        try:
            cnn_probability = predict_with_cnn(input_tensor) # Pass the tensor
        except Exception as e:
            current_app.logger.error(f"Error during CNN prediction: {str(e)}")
            return jsonify({'error': 'Error during CNN prediction'}), 500
        if cnn_probability == -1.0:
            return jsonify({'error': 'CNN model not loaded'}), 500
        yolo_detections = []  # No YOLO detections for CNN
        processed_image_path = None

    elif model_type == 'yolo':
        # YOLOv8 Prediction
        yolo_image = preprocess_image_for_yolo(image_bytes)
        if yolo_image is None:
            return jsonify({'error': 'Failed to preprocess image for YOLOv8'}), 500
        try:
            yolo_detections = predict_with_yolo(yolo_image)
        except Exception as e:
            current_app.logger.error(f"Error during YOLO prediction: {e}")
            return jsonify({'error': 'Error during YOLO prediction'}), 500
        cnn_probability = -1.0

        processed_image_path = None
        if yolo_detections:
            # Inline box drawing (previously in draw_boxes_on_image function)
            try:
                # Open the image from bytes
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                draw = ImageDraw.Draw(image)

                # Draw each detection
                for detection in yolo_detections:
                    bbox = detection['bbox']
                    confidence = detection['confidence']
                    class_name = detection['class']

                    # Draw rectangle (convert coordinates to integers)
                    draw.rectangle(
                        [(int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3]))],
                        outline='red',
                        width=3
                    )

                    # Draw label with background
                    label = f"{class_name} {confidence:.2f}"
                    text_position = (int(bbox[0]), int(bbox[1]) - 15)
                    text_bbox = draw.textbbox(text_position, label)
                    draw.rectangle(text_bbox, fill='red')
                    draw.text(text_position, label, fill='white')

                # Save to bytes buffer
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG')  # Or PNG, depending on your needs
                processed_image_bytes = output_buffer.getvalue()
            except Exception as e:
                current_app.logger.error(f"Error drawing boxes: {e}")
                # Return original image if drawing fails
                processed_image_bytes = image_bytes

            processed_filename = "processed_" + unique_filename
            processed_image_path = save_image(processed_image_bytes, Config.PROCESSED_FOLDER, processed_filename)
        # Always save as processed image
        else:
            processed_filename = "processed_" + unique_filename
            processed_image_path = save_image(image_bytes, Config.PROCESSED_FOLDER, processed_filename)
    else:
        return jsonify({'error': 'Invalid model_type'}), 400

    processing_time = time.time() - start_time

    # Database interaction using psycopg2 connection pool
    conn = None  # Initialize connection
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to database'}), 500
        cur = conn.cursor()

        # Prepare data for insertion
        yolo_detections_json = json.dumps(yolo_detections) if yolo_detections else '[]'

        cur.execute(
            "INSERT INTO image_result (original_filename, image_path, processed_image_path, yolo_detections, cnn_probability, processing_time, timestamp, model_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (original_filename, image_path, processed_image_path, yolo_detections_json, cnn_probability,
             processing_time, datetime.utcnow(), model_type)
        )

        result_id = cur.fetchone()[0]
        conn.commit()
        current_app.logger.info(f"Successfully inserted result with ID: {result_id}")

    except Exception as e:
        current_app.logger.error(f"Error saving to database: {e}")
        if conn:  # Check if conn is not None before rolling back
            conn.rollback()
        return jsonify({'error': 'Failed to save results to database'}), 500,

    finally:
        if conn:  # Ensure connection is closed even if errors occur
            close_db_connection(conn)  # Use the close_db_connection function

    response_data = {
        'id': result_id,
        'yolo_detections': yolo_detections,
        'cnn_probability': cnn_probability,
        'processing_time': processing_time,
    }

    # Always return the processed image (with or without boxes)
    if processed_image_path:
        with open(processed_image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            response_data['image_with_boxes'] = img_base64
    else:
        # This should never happen now, but include as a fallback
        with open(image_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            response_data['image_with_boxes'] = img_base64

    return jsonify(response_data), 200


@bp.route('/results/<int:image_id>')
def get_result(image_id):
    """Retrieves results for a specific image ID."""
    conn = None  # Initialize connection
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to database'}), 500
        cur = conn.cursor()

        # Fetch data from the database
        cur.execute("SELECT * FROM image_result WHERE id = %s", (image_id,))
        result = cur.fetchone()

        if result is None:
            return jsonify({'error': 'Image result not found'}), 404

        # Assuming your columns are in this order: id, original_filename, ..., yolo_detections, ...
        # Adjust the indices in the following line if your column order is different
        result_data = {
            'id': result[0],
            'original_filename': result[1],
            'image_path': result[2],
            'processed_image_path': result[3],
            'yolo_detections': json.loads(result[4]) if result[4] else [],  # Load JSON
            'cnn_probability': result[5],
            'processing_time': result[6],
            'timestamp': result[7].isoformat(),  # Format timestamp
            'model_type': result[8]
        }
        # Always return the processed image (with or without boxes)
        if result_data['processed_image_path'] and os.path.exists(result_data['processed_image_path']):
            with open(result_data['processed_image_path'], "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                result_data['image_with_boxes'] = img_base64
        else:
            # This should never happen now, but include as a fallback
            with open(result_data['image_path'], 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                result_data['image_with_boxes'] = img_base64
        return jsonify(result_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching result from database: {e}")
        return jsonify({'error': 'Failed to fetch results from database'}), 500

    finally:
        if conn:
            close_db_connection(conn)  # Use the close_db_connection function

@bp.route('/get_image/<int:image_id>')
def get_image(image_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to the database'}), 500
        cur = conn.cursor()

        cur.execute("SELECT processed_image_path, image_path FROM image_result WHERE id = %s", (image_id,))
        result = cur.fetchone()

        if result is None:
            return jsonify({'error': 'Image result not found'}), 404

        processed_image_path, image_path = result

        if processed_image_path and os.path.exists(processed_image_path):
            return send_file(processed_image_path, mimetype='image/jpeg')
        elif os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return jsonify({'error':"image not found"}), 404

    except Exception as e:
        current_app.logger.error(f"Error retrieving image: {e}")
        return jsonify({'error': 'Failed to retrieve image'}), 500

    finally:
        if conn:
            close_db_connection(conn)

# Health check route
@bp.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200