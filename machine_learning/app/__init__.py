from flask import Flask
from flask_cors import CORS
from config import Config  # Corrected import

# db = SQLAlchemy()  # REMOVED - No SQLAlchemy, no db instance needed here

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # db.init_app(app)  # REMOVED - No SQLAlchemy

    # Enable CORS for all routes and origins
    CORS(app)

    # Import blueprints (routes)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app