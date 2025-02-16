from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ImageResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    processed_image_path = db.Column(db.String(255))
    yolo_detections = db.Column(db.JSON)
    cnn_probability = db.Column(db.Float)
    processing_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ImageResult {self.id} - {self.original_filename}>"
