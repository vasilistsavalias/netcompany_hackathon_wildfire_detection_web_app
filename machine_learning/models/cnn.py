import tensorflow as tf

CNN_MODEL_PATH = "models/cnn/best_model.keras"  # Relative to project root (machine_learning)
CNN_INPUT_SIZE = (224, 224)
cnn_model = None  # Initialize to None

def load_cnn_model():
    """Loads the CNN model."""
    global cnn_model  # Use the global variable
    try:
        cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)
        return cnn_model
    except Exception as e:
        print(f"Error loading CNN model: {e}")
        return None

def predict_with_cnn(image_array):
    """Performs inference with the CNN."""
    if cnn_model is None:
        load_cnn_model() # Try loading if it hasn't been loaded.
    if cnn_model is None: # If still none, return error
        return -1.0
    prediction = cnn_model.predict(image_array, verbose=0)[0][0]
    return float(prediction)