import io
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms

CNN_INPUT_SIZE = (224, 224)
YOLO_INPUT_SIZE = (352, 352)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def preprocess_image_for_yolo(image_bytes):
    """Preprocesses an image for YOLOv8."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize(YOLO_INPUT_SIZE, Image.BILINEAR)  # Use explicit size and antialiasing
        img_array = np.array(image)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image for YOLO: {e}")
        return None

def preprocess_image_for_cnn(image_bytes):
    """Preprocesses an image for the CNN (using torchvision.transforms)."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        transform = transforms.Compose([
            transforms.Resize(CNN_INPUT_SIZE, antialias=True),
            transforms.ToTensor(),  # Converts to tensor AND changes order to (C, H, W)
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        input_tensor = transform(image)  # Apply transformations
        input_tensor = input_tensor.unsqueeze(0).to(device)  # Add batch dimension and move to device

        return input_tensor

    except Exception as e:
        print(f"Error in preprocess_image_for_cnn: {e}")
        return None