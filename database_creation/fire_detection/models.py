from datetime import datetime
from app import db
import json  # Import the json module


class ImageResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
    processed_image_path = db.Column(db.String(255))
    yolo_detections = db.Column(db.Text)  # Use Text for JSON
    cnn_probability = db.Column(db.Float)
    processing_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    model_type = db.Column(db.String(50))  # 'cnn' or 'yolo'

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