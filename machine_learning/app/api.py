from flask import Blueprint, request, jsonify, send_file
import time
import base64
from app import db
from app.models import ImageResult
from app.utils import save_image, draw_boxes_on_image
from models.yolo import predict_with_yolo, YOLO_INPUT_SIZE  # Correct import
from models.cnn import predict_with_cnn, CNN_INPUT_SIZE  # Correct import
from preprocessing import preprocess_image_for_yolo, preprocess_image_for_cnn
from PIL import Image
import io
import os
import uuid
from config import Config

bp = Blueprint('api', __name__)

@bp.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()

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
    # Generate a unique filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]

    # Save the original image
    image_path = save_image(image_bytes, Config.UPLOAD_FOLDER, unique_filename)

    # YOLOv8 Prediction
    yolo_image = preprocess_image_for_yolo(image_bytes)
    if yolo_image is None:
        return jsonify({'error': 'Failed to preprocess image for YOLOv8'}), 500
    yolo_detections = predict_with_yolo(yolo_image)

    # CNN Prediction
    cnn_image = preprocess_image_for_cnn(image_bytes)
    if cnn_image is None:
        return jsonify({'error': 'Failed to preprocess image for CNN'}), 500
    cnn_probability = predict_with_cnn(cnn_image)


    processing_time = time.time() - start_time

    # Save processed image (optional)
    processed_image_path = None
    if yolo_detections:
        processed_image_bytes = draw_boxes_on_image(image_bytes, yolo_detections)
        processed_filename = "processed_" + unique_filename
        processed_image_path = save_image(processed_image_bytes, Config.PROCESSED_FOLDER, processed_filename)

    # Store results in the database
    result = ImageResult(
        original_filename=original_filename,
        image_path=image_path,
        processed_image_path=processed_image_path,
        cnn_probability=cnn_probability,
        processing_time=processing_time
    )
    result.set_yolo_detections(yolo_detections)  # Use the setter method
    db.session.add(result)
    db.session.commit()

    # Prepare the response
    response_data = {
        'id': result.id,  # Return the database ID
        'yolo_detections': yolo_detections,
        'cnn_probability': cnn_probability,
        'processing_time': processing_time,
    }

    # Optional: Include base64 image if requested
    include_image = request.args.get('include_image', 'false').lower() == 'true'
    if include_image:
        if processed_image_path:  # If we have a processed image, use it
            with open(processed_image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                response_data['image_with_boxes'] = img_base64
        else:  # Otherwise, use the original image
            with open(image_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                response_data['image_with_boxes'] = img_base64

    return jsonify(response_data), 200

@bp.route('/results/<int:image_id>')
def get_result(image_id):
    """Retrieves results for a specific image ID."""
    result = ImageResult.query.get(image_id)
    if result is None:
        return jsonify({'error': 'Image result not found'}), 404

    response_data = {
        'id': result.id,
        'original_filename': result.original_filename,
        'yolo_detections': result.get_yolo_detections(),  # Use the getter method
        'cnn_probability': result.cnn_probability,
        'processing_time': result.processing_time,
        'timestamp': result.timestamp.isoformat()  # Format the timestamp
    }

    # Optional: Include image paths or base64 encoded images
    include_image = request.args.get('include_image', 'false').lower() == 'true'
    if include_image:
        if result.processed_image_path and os.path.exists(result.processed_image_path):
            with open(result.processed_image_path, "rb") as img_file:
                response_data['processed_image'] = base64.b64encode(img_file.read()).decode('utf-8')
        elif os.path.exists(result.image_path): #if there is no processed image, we will use the original
            with open(result.image_path, "rb") as img_file:
                response_data['original_image'] = base64.b64encode(img_file.read()).decode('utf-8')
        #else we return nothing

    return jsonify(response_data), 200

@bp.route('/get_image/<int:image_id>')
def get_image(image_id):
    result = ImageResult.query.get(image_id)
    if result is None:
        return jsonify({'error': 'Image result not found'}), 404

    if result.processed_image_path and os.path.exists(result.processed_image_path):
        return send_file(result.processed_image_path, mimetype='image/jpeg')
    elif os.path.exists(result.image_path):
        return send_file(result.image_path, mimetype='image/jpeg')
    else:
        return jsonify({'error':"image not found"}), 404