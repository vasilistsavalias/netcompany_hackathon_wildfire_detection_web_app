from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def draw_boxes_on_image(image_bytes, detections):
    """
    Draws bounding boxes and class labels on an image.

    Parameters:
      image_bytes (bytes): The raw image data.
      detections (list): List of detection dictionaries, each with keys:
                         'bbox' (list of [x1, y1, x2, y2]),
                         'confidence' (float),
                         'class' (str).

    Returns:
      bytes: Processed image data in JPEG format.
    """
    # Load the image from bytes
    image = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    # Optional: Load a font (fallback to default if unavailable)
    try:
        font = ImageFont.truetype("arial.ttf", size=16)
    except IOError:
        font = ImageFont.load_default()

    # Loop through all detections and draw boxes
    for detection in detections:
        bbox = detection['bbox']
        label = detection.get('class', 'object')
        confidence = detection.get('confidence', 0)
        
        # Draw rectangle: bbox = [x1, y1, x2, y2]
        draw.rectangle(bbox, outline="red", width=3)
        
        # Prepare text: e.g., "smoke: 0.95"
        text = f"{label}: {confidence:.2f}"
        
        # Calculate text size and position
        text_size = draw.textsize(text, font=font)
        text_location = (bbox[0], bbox[1] - text_size[1] if bbox[1] - text_size[1] > 0 else bbox[1])
        
        # Draw text background for readability
        draw.rectangle([text_location, (text_location[0] + text_size[0], text_location[1] + text_size[1])], fill="red")
        # Draw the text
        draw.text(text_location, text, fill="white", font=font)

    # Save the modified image to a bytes buffer
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def main():
    # Path to your test image
    test_image_path = os.path.join("machine_learning", "test_images", "test_cnn_fire.jpg")
    
    # Read the image as bytes
    try:
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"Test image not found at: {test_image_path}")
        return

    # Convert bytes to a numpy array for YOLO prediction using PIL
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
    except Exception as e:
        print(f"Error processing the image: {e}")
        return

    # Run YOLO inference to get detections
    detections = predict_with_yolo(image_array)
    print("Detections:", detections)
    
    # Draw boxes on the original image bytes
    processed_image_bytes = draw_boxes_on_image(image_bytes, detections)
    
    # Save the processed image to disk
    output_path = "processed_test_image.jpg"
    try:
        with open(output_path, "wb") as f:
            f.write(processed_image_bytes)
        print(f"Processed image saved to: {output_path}")
    except Exception as e:
        print(f"Error saving the processed image: {e}")

if __name__ == '__main__':
    main()