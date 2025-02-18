import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists - for local development)
load_dotenv()

class Config:
    """Base configuration."""
    # Get SECRET_KEY from environment variable.  Generate a temporary one
    # *only* if it's not set.  This is for convenience, NOT security.
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if SECRET_KEY is None:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print("WARNING: FLASK_SECRET_KEY environment variable not set. Using a temporary random key.")
        # Do not attempt to write to a file
    DATABASE_URL = os.environ['DATABASE_URL']  # MUST be set in the environment
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'processed_images'
    YOLO_CONFIDENCE_THRESHOLD = 0.01
    CNN_CONFIDENCE_THRESHOLD = 0.5


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False