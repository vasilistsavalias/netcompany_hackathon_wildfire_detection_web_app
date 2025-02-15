from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOADED_IMAGES_DEST']):
    os.makedirs(app.config['UPLOADED_IMAGES_DEST'])

# Import routes after initializing app
from routes import *

if __name__ == '__main__':
    app.run(debug=True)