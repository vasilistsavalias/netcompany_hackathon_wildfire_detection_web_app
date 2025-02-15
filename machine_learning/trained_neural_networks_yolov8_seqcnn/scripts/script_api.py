import io
import os
import time
import uuid
import base64
import json
from datetime import datetime

import cv2
import numpy as np
import torch
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw
from ultralytics import YOLO
from flask_sqlalchemy import SQLAlchemy
from tensorflow.python.keras.models import load_model

app = Flask(__name__)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@host/database'  # Replace with your database credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress a warning
db = SQLAlchemy(app)

# --- File Storage Configuration ---
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the directories if they don't exist
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- Model Paths (Adjust these if your paths are different) ---
YOLO_MODEL_PATH = "models/yolo/best_yolov8_model.pt"
CNN_MODEL_PATH = "models/cnn/best_model.keras"

# --- Image Sizes ---
YOLO_INPUT_SIZE = (352, 352)
CNN_INPUT_SIZE = (224, 224)

# --- Confidence Thresholds ---
YOLO_CONFIDENCE_THRESHOLD = 0.5
CNN_CONFIDENCE_THRESHOLD = 0.5

# --- Database Model ---
class ImageResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
    processed_image_path = db.Column(db.String(255))
    yolo_detections = db.Column(db.JSON)  # Store as JSON
    cnn_probability = db.Column(db.Float)
    processing_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ImageResult {self.id}>'

# --- Model Loading ---
# (Same as before - load_yolo_model() and load_cnn_model())
def load_yolo_model():
    """Loads the YOLOv8 model."""
    try:
        model = YOLO(YOLO_MODEL_PATH)
        model.to('cuda' if torch.cuda.is_available() else 'cpu')
        return model
    except Exception as e:
        print(f"Error loading YOLOv8 model: {e}")
        return None

def load_cnn_model():
    """Loads the CNN model."""
    try:
        model = load_model(CNN_MODEL_PATH)
        return model
    except Exception as e:
        print(f"Error loading CNN model: {e}")
        return None

yolo_model = load_yolo_model()
cnn_model = load_cnn_model()

# --- Preprocessing Functions ---
# (Same as before - preprocess_image_for_yolo() and preprocess_image_for_cnn())
def preprocess_image_for_yolo(image_bytes):
    """Preprocesses an image for YOLOv8."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize(YOLO_INPUT_SIZE)
        img_array = np.array(image)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image for YOLO: {e}")
        return None

def preprocess_image_for_cnn(image_bytes):
    """Preprocesses an image for the CNN."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize(CNN_INPUT_SIZE)
        img_array = np.array(image)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image for CNN: {e}")
        return None

# --- Inference Functions ---
# (Same as before - predict_with_yolo() and predict_with_cnn())
def predict_with_yolo(image_array):
    """Performs inference with YOLOv8."""
    if yolo_model is None:
        return []
    results = yolo_model(image_array, verbose=False)
    detections = []
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            conf = box.conf[0]
            cls = int(box.cls[0])
            if conf >= YOLO_CONFIDENCE_THRESHOLD:
                detections.append({'bbox': xyxy, 'confidence': float(conf), 'class': cls})
    return detections

def predict_with_cnn(image_array):
    """Performs inference with the CNN."""
    if cnn_model is None:
        return -1.0
    prediction = cnn_model.predict(image_array, verbose=0)[0][0]
    return float(prediction)

# --- Utility Functions ---

def save_image(image_bytes, folder, filename):
    """Saves an image to the specified folder.

    Args:
        image_bytes (bytes): The image data as bytes.
        folder (str): The directory to save the image in.
        filename (str): The filename to use.

    Returns:
        str: The full path to the saved image.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image_path = os.path.join(folder, filename)
    image.save(image_path)
    return image_path

def draw_boxes_on_image(image_bytes, detections):
    """Draws bounding boxes on the image and saves it."""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)

    for detection in detections:
        bbox = detection['bbox']
        conf = detection['confidence']
        draw.rectangle(bbox, outline="red", width=3)
        label = f"Smoke: {conf:.2f}"
        draw.text((bbox[0], bbox[1] - 10), label, fill="red")

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')  # Use JPEG format
    return img_byte_arr.getvalue()

# --- API Endpoints ---

@app.route('/predict', methods=['POST'])
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
    image_path = save_image(image_bytes, UPLOAD_FOLDER, unique_filename)

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
    if cnn_probability == -1.0:
        return jsonify({'error': 'CNN model not loaded'}), 500

    processing_time = time.time() - start_time

    # Save processed image (optional)
    processed_image_path = None
    if yolo_detections:
        processed_image_bytes = draw_boxes_on_image(image_bytes, yolo_detections)
        processed_filename = "processed_" + unique_filename
        processed_image_path = save_image(processed_image_bytes, PROCESSED_FOLDER, processed_filename)

    # Store results in the database
    result = ImageResult(
        original_filename=original_filename,
        image_path=image_path,
        processed_image_path=processed_image_path,
        yolo_detections=json.dumps(yolo_detections),  # Convert to JSON string
        cnn_probability=cnn_probability,
        processing_time=processing_time
    )
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
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            response_data['image_with_boxes'] = img_base64

    return jsonify(response_data), 200

@app.route('/results/<int:image_id>')
def get_result(image_id):
    """Retrieves results for a specific image ID."""
    result = ImageResult.query.get(image_id)
    if result is None:
        return jsonify({'error': 'Image result not found'}), 404

    # Convert the JSON string back to a Python object
    yolo_detections = json.loads(result.yolo_detections)

    response_data = {
        'id': result.id,
        'original_filename': result.original_filename,
        'yolo_detections': yolo_detections,
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

@app.route('/get_image/<int:image_id>')
def get_image(image_id):
    result = ImageResult.query.get(image_id)
    if result is None:
        return jsonify({'error': 'Image result not found'}), 404
    # Convert the JSON string back to a Python object
    yolo_detections = json.loads(result.yolo_detections)

    if result.processed_image_path and os.path.exists(result.processed_image_path):
        return send_file(result.processed_image_path, mimetype='image/jpeg')
    elif os.path.exists(result.image_path):
        return send_file(result.image_path, mimetype='image/jpeg')
    else:
        return jsonify({'error':"image not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))