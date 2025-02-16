from ultralytics import YOLO
import torch

YOLO_MODEL_PATH = "models/yolo/best_yolov8_model.pt"  # Relative to project root
YOLO_CONFIDENCE_THRESHOLD = 0.1  # Temporarily lowered for testing
YOLO_INPUT_SIZE = (352, 352)
yolo_model = None
# Add class names here, matching the order in your data.yaml
CLASS_NAMES = ['smoke']

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
    global yolo_model
    if yolo_model is None:
      yolo_model = load_yolo_model()
    if yolo_model is None:
        return []
    results = yolo_model(image_array, verbose=False)
    print(f"YOLO Results: {results}")  # Debug print
    detections = []
    for result in results:
        boxes = result.boxes.cpu().numpy()
        print(f"Boxes: {boxes}")  # Debug print
        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            conf = box.conf[0]
            cls = int(box.cls[0])
            print(f"  Box: xyxy={xyxy}, conf={conf}, cls={cls}")  # Debug print
            if conf >= YOLO_CONFIDENCE_THRESHOLD:
                # Use the class names here
                detections.append({'bbox': xyxy, 'confidence': float(conf), 'class': CLASS_NAMES[cls]})
    return detections