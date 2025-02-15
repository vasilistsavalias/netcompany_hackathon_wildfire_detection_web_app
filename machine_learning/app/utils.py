import os
import io
from PIL import Image, ImageDraw
import uuid

def save_image(image_bytes, folder, filename):
    """Saves an image to the specified folder."""
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