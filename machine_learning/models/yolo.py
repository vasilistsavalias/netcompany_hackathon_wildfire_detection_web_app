from ultralytics import YOLO
import torch

YOLO_MODEL_PATH = "models/yolo/best_yolov8_model.pt"  # Relative to project root (machine_learning)
YOLO_CONFIDENCE_THRESHOLD = 0.5
YOLO_INPUT_SIZE = (352, 352)
yolo_model = None

def load_yolo_model():
    """Loads the YOLOv8 model."""
    global yolo_model
    try:
        yolo_model = YOLO(YOLO_MODEL_PATH)
        yolo_model.to('cuda' if torch.cuda.is_available() else 'cpu')
        return yolo_model
    except Exception as e:
        print(f"Error loading YOLOv8 model: {e}")
        return None

def predict_with_yolo(image_array):
    """Performs inference with YOLOv8."""
    if yolo_model is None:
        load_yolo_model()
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