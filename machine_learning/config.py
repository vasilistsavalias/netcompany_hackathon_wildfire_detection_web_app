import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key'  # Use a strong secret key!
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'processed_images'
    YOLO_CONFIDENCE_THRESHOLD = 0.5
    CNN_CONFIDENCE_THRESHOLD = 0.5
    # Database URL - default to SQLite if not set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Add production-specific settings here (e.g., database URL)

# You can add other configurations (TestingConfig, etc.) as needed.