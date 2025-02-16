import tensorflow as tf
from tensorflow import keras
import os

CNN_MODEL_PATH = os.path.join("models", "cnn", "best_model.keras")
CNN_INPUT_SIZE = (224, 224)
cnn_model = None

def load_cnn_model():
    """Loads the CNN model."""
    global cnn_model
    try:
        # Load the original model
        cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)
        print("Original CNN model loaded successfully.")

        # Save the model WITHOUT the optimizer
        tf.keras.models.save_model(cnn_model, CNN_MODEL_PATH, include_optimizer=False)
        print(f"Model re-saved without optimizer to {CNN_MODEL_PATH}")

        # Reload the model (to ensure the changes take effect)
        cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)

    except Exception as e:
        print(f"Error loading or saving CNN model: {e}")
        return None  # Return None if loading fails

    return cnn_model

def predict_with_cnn(image_array):
    """Performs inference with the CNN."""
    global cnn_model
    if cnn_model is None:
        cnn_model = load_cnn_model()
    if cnn_model is None:
        return -1.0

    try:
        prediction = cnn_model.predict(image_array, verbose=0)[0][0]
        return float(prediction)
    except Exception as e:
        print(f"Error during CNN prediction: {e}")
        return -1.0