
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

class Config:
     SECRET_KEY = os.environ.get('SECRET_KEY')
     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
     SQLALCHEMY_TRACK_MODIFICATIONS = False  # Suppress a warning
     MODEL_STORAGE_PATH = os.environ.get('MODEL_STORAGE_PATH')
