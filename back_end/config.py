import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration (SQLite for simplicity; replace with PostgreSQL in production)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///images.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_IMAGES_DEST = os.getenv('UPLOADS_FOLDER', 'uploads')