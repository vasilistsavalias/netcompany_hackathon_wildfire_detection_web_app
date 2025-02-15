import io
import numpy as np
from PIL import Image

def preprocess_image_for_yolo(image_bytes):
    """Preprocesses an image for YOLOv8."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize((352, 352))  # Use explicit size
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
        image = image.resize((224, 224))  # Use explicit size
        img_array = np.array(image)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image for CNN: {e}")
        return None