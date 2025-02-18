from datetime import datetime
import json  # Import the json module


class ImageResult: # Not a db.Model anymore
    def __init__(self, id, original_filename, image_path, processed_image_path, yolo_detections, cnn_probability, processing_time, timestamp, model_type):
        self.id = id
        self.original_filename = original_filename
        self.image_path = image_path
        self.processed_image_path = processed_image_path
        self.yolo_detections = yolo_detections
        self.cnn_probability = cnn_probability
        self.processing_time = processing_time
        self.timestamp = timestamp
        self.model_type = model_type


    def __repr__(self):
        return f'<ImageResult {self.id}>'

    def set_yolo_detections(self, detections):
        """Sets the YOLO detections, converting the list to a JSON string."""
        self.yolo_detections = json.dumps(detections)

    def get_yolo_detections(self):
        """Gets the YOLO detections, converting the JSON string back to a list."""
        if self.yolo_detections:
            return json.loads(self.yolo_detections)
        else:
            return []  # Return empty list if no detections