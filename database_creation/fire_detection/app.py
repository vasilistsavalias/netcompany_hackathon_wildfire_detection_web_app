from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from models import db, ImageResult  # Import db and ImageResult from models.py

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Database URL from .env
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with the app
db.init_app(app)

with app.app_context():
    db.create_all()  # This will create the database tables based on the model

    print("Database tables created!")

if __name__ == '__main__':
    app.run(debug=True)
