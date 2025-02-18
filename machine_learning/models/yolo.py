from ultralytics import YOLO
import torch
import os
from PIL import Image, ImageDraw
import numpy as np
import io

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Points to models/yolo/

# Define paths relative to the script's location
YOLO_MODEL_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "best_yolov8_model.pt"))
HARD_CODED_IMAGE_PATH = os.path.abspath(os.path.join(
    SCRIPT_DIR, "..", "..", "test_images", "test_yolo_smoke_1.jpg"  # Goes up to machine_learning/test_images/
))
YOLO_CONFIDENCE_THRESHOLD = 0.1
CLASS_NAMES = ["smoke"]

yolo_model = None
from ultralytics import YOLO
import torch
import os
from PIL import Image, ImageDraw
import numpy as np
import io

# Relative paths from project root (machine_learning/)
YOLO_MODEL_PATH = "models/yolo/best_yolov8_model.pt"
HARD_CODED_IMAGE_PATH = "test_images/test_yolo_smoke_1.jpg"
OUTPUT_IMAGE_PATH = "models/processed_images/detected_test.jpg"

YOLO_CONFIDENCE_THRESHOLD = 0.1
CLASS_NAMES = ["smoke"]

yolo_model = None

def load_yolo_model():
    """Loads the YOLOv8 model using relative path"""
    try:
        if not os.path.exists(YOLO_MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {YOLO_MODEL_PATH}")

        model = YOLO(YOLO_MODEL_PATH)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        return model
    except Exception as e:
        print("Current directory:", os.getcwd())
        print(f"Model exists in Docker? {os.path.exists(YOLO_MODEL_PATH)}")
        print(f"Image exists in Docker? {os.path.exists(HARD_CODED_IMAGE_PATH)}")
        print(f"Error loading YOLOv8 model: {e}")
        return None

def ensure_model_loaded():
    global yolo_model
    if yolo_model is None:
        yolo_model = load_yolo_model()
    return yolo_model is not None



def predict_with_yolo(image_array):
    """Performs inference with YOLOv8."""
    if not ensure_model_loaded():
        print("Failed to load YOLO model")
        return []

    try:
        # Inference
        results = yolo_model(image_array, verbose=False)
        detections = []

        for result in results:
            # Each 'result.boxes' is a Boxes object with .xyxy, .conf, and .cls
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                xyxy = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                if conf >= YOLO_CONFIDENCE_THRESHOLD:
                    detections.append({
                        'bbox': xyxy,
                        'confidence': conf,
                        'class': CLASS_NAMES[cls]
                    })
        return detections
    except Exception as e:
        print(f"Error during YOLO prediction: {e}")
        return []

def draw_boxes_on_image(image_bytes, detections):
    """Draws bounding boxes on the image."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(image)

        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class']

            # Draw the bounding box
            draw.rectangle(bbox, outline='red', width=2)
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            draw.text((bbox[0], bbox[1] - 10), label, fill='red')

        # Return image as bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG')
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Error drawing boxes: {e}")
        return image_bytes

