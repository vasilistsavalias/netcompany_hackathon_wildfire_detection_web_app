import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import CORS
from flask_migrate import Migrate
# from dotenv import load_dotenv  # Import load_dotenv
from PIL import Image  # To attempt image loading/validation
import io
# from models import db, ImageModel  # Import db and ImageModel from models.py

# --- Load Environment Variables ---

# load_dotenv()  # Load environment variables from .env file

# --- Configuration ---
app = Flask(__name__, static_folder="frontend/build", static_url_path="/") # Static folder configuration

# Enable CORS for all origins (for development - restrict in production!)
# Restrict origins in production for security! e.g., CORS(app, origins=["http://localhost:3000"])
CORS(app)  # Enable CORS

# Get database URL from environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///./app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
db.init_app(app)  # Initialize SQLAlchemy with the Flask app
migrate = Migrate(app, db) # Initialize Migrate

# --- API Endpoints ---

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handles image uploads. Expects a POST request with a file named 'image'."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image part in the request'}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        # --- Image Validation ---
        filename = image_file.filename
        if not allowed_file(filename):
            return jsonify({'error': 'Invalid file type. Only png, jpg, jpeg allowed.'}), 400

        try:
            img = Image.open(image_file)
            img.verify()
            img.close()
            image_file.seek(0)  # Reset file pointer after PIL operations

        except Exception as e:
            print(f"Image validation error: {e}")
            return jsonify({'error': f'Invalid image file. Cannot open or corrupted. {e}'}), 400

        # --- Store Image in Database (as BLOB) ---
        image_data = image_file.read()
        new_image = ImageModel(filename=filename, data=image_data)

        #  --- Alternative: Save to File System  ---
        #  image_path = os.path.join('uploads', filename)  # Make sure 'uploads' directory exists!
        #  image_file.save(image_path)
        #  new_image = ImageModel(filename=filename, filepath=image_path) #Storing filepath

        db.session.add(new_image)
        db.session.commit()

        # --- AI Model Integration (Placeholder) ---
        # TODO: Replace this with your actual AI model integration logic
        ai_results = call_ai_model(image_data) # Pass binary data

        # Update the image entry with AI model results
        new_image.ai_model_results = ai_results
        db.session.commit()

        return jsonify({'message': 'Image uploaded successfully', 'image_id': new_image.id, 'ai_results': ai_results}), 201

    except Exception as e:
        print(f"Error uploading image: {e}")
        db.session.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500


# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_ai_model(image_data):  # Replace with your AI Model function
    """
    Placeholder function for calling the AI model.
    Replace this with your actual AI model integration.
    """
    # Simulate AI processing
    print("Simulating AI model processing...")
    # In a real implementation, you would pass the image_data to your AI model
    # and return the results.
    return {"prediction": "Simulated AI prediction", "confidence": 0.95}


# --- Flask Shell Context (for debugging) ---
@app.shell_context_processor
def make_shell_context():
    """Automatically import db and models when running `flask shell`."""
    return {'db': db, 'ImageModel': ImageModel}

# --- Serve React App ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# --- Main ---
if __name__ == '__main__':
    # Create 'uploads' directory if it doesn't exist (for filepath storage)
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # --- Create the database tables within the app context ---
    with app.app_context():
         db.create_all()

    app.run(debug=True)  # Don't use debug mode in production