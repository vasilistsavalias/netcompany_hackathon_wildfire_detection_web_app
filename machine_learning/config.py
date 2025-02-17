import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    # Check if the key exists (either in environment or in .txt file)
    if 'SECRET_KEY' not in os.environ:
        #If not there check if the txt file exists with the key.
        if not os.path.exists('flask_secret_key.txt'):
            import secrets

            secret_key = secrets.token_hex(32)
            with open('flask_secret_key.txt', 'w') as f:
                f.write(secret_key)
            os.chmod('flask_secret_key.txt', 0o600) #Make key secure

            # Set the environment variable for current python process as now you have persisted it.
            os.environ['SECRET_KEY'] = secret_key
            print ("Generated and persisted the SECRET_KEY.")

    # Now load key and crash in case that it's not set.
    SECRET_KEY = os.environ['SECRET_KEY']
    DATABASE_URL = os.environ['DATABASE_URL']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'processed_images'
    YOLO_CONFIDENCE_THRESHOLD = 0.1
    CNN_CONFIDENCE_THRESHOLD = 0.5


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    # Add production-specific settings here (e.g., a real database URL)