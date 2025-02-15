import requests
import os
import json  # Import the json module

# --- Configuration ---
BASE_URL = 'http://127.0.0.1:8080'  # Base URL of your Flask app - USE HTTP
PREDICT_ENDPOINT = f'{BASE_URL}/predict'
TEST_IMAGE_DIR = 'test_images'  # Directory containing test images

# --- Image Paths ---
CNN_TEST_IMAGE = os.path.join(TEST_IMAGE_DIR, 'test_cnn_fire.jpg')
YOLO_TEST_IMAGE = os.path.join(TEST_IMAGE_DIR, 'test_yolo.jpg')

def test_image(image_path, endpoint_url):
    """Sends a test image to the specified endpoint and prints the results."""

    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(endpoint_url, files=files)

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        result = response.json()
        print(f"Results for {image_path}:")
        print(json.dumps(result, indent=2))  # Pretty-print the JSON
        print("-" * 20)

    except requests.exceptions.RequestException as e:
        print(f"Error sending request for {image_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {image_path}: {e}")

if __name__ == '__main__':
    print("Testing CNN classification...")
    test_image(CNN_TEST_IMAGE, PREDICT_ENDPOINT)

    print("Testing YOLO object detection...")
    test_image(YOLO_TEST_IMAGE, PREDICT_ENDPOINT)