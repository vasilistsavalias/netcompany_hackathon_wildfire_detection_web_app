import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from pathlib import Path
from PIL import Image
import numpy as np
import io

# Constants
# __file__ is in machine_learning/models, so BASE_DIR is that folder.
BASE_DIR = Path(__file__).resolve().parent
# Our model is stored in machine_learning/models/cnn/best_model.pth
CNN_MODEL_PATH = BASE_DIR / "cnn" / "best_model.pth"
CNN_INPUT_SIZE = (224, 224)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Global model variable
cnn_model = None

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

def initialize_cnn_model():
    """Initializes a ConvNeXt model with the correct classifier."""
    model = models.convnext_large(pretrained=True)
    num_features = model.classifier[2].in_features

    # Modify the classifier for binary classification
    model.classifier[2] = nn.Sequential(
        nn.Linear(num_features, 1),
        nn.Sigmoid()
    )

    return model

def load_cnn_model():
    """Loads the CNN model from the saved file or uses the default pretrained model if not found."""
    global cnn_model
    try:
        # Initialize model (this already gets a pretrained model)
        model = initialize_cnn_model()

        # Load the model weights (if the file exists)
        if CNN_MODEL_PATH.exists():
            model.load_state_dict(torch.load(CNN_MODEL_PATH, map_location=device))
            print("✅ PyTorch CNN model loaded successfully.")
        else:
            print(f"⚠️ No model found at '{CNN_MODEL_PATH}'. Using default pretrained model.")
            # save_cnn_model(model)  # Do NOT save here. Only save after training.

        model.to(device)  # Move to device (CPU or CUDA)
        model.eval()      # Set to evaluation mode
        cnn_model = model # Set the global variable

    except Exception as e:
        print(f"❌ Error loading PyTorch CNN model: {e}")
        import traceback
        traceback.print_exc()
        cnn_model = None

    return cnn_model

def save_cnn_model(model):
    """Saves the pretrained CNN model state dictionary."""
    CNN_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), CNN_MODEL_PATH)
    print(f"✅ Model saved at '{CNN_MODEL_PATH}'.")

def predict_with_cnn(input_tensor): # Changed the argument
    """Performs inference using the CNN model and returns the fire probability."""
    global cnn_model
    if cnn_model is None:
        cnn_model = load_cnn_model()
    if cnn_model is None:
        return -1.0  # Model failed to load

    try:
        # No preprocessing here!  input_tensor is *already* preprocessed.
        with torch.no_grad():
            prediction = cnn_model(input_tensor).item()

        return float(prediction)

    except Exception as e:
        print(f"❌ Error during CNN prediction: {e}")
        return -1.0

def main():
    """Main function to test the CNN model with an image."""
    # Read test image as bytes
    image_path = "machine_learning/test_images/test_cnn_fire.jpg"  # Default test image path
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return

    # Load the CNN model
    model = load_cnn_model()
    if model is None:
        print("❌ Model failed to load.")
        return

    # Preprocess image
    input_tensor = preprocess_image_for_cnn(image_bytes) # Preprocess outside
    if input_tensor is None:
        print("❌ Image preprocessing failed.")
        return

    # Run prediction
    prediction = predict_with_cnn(input_tensor) # Pass the tensor
    if prediction != -1.0:
        print(f"🔥 Fire Probability: {prediction:.4f}")
    else:
        print("❌ Error during prediction.")

if __name__ == "__main__":
    main()