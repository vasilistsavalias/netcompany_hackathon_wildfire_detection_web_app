from flask import Flask
from config import Config  # Import your Config class
from flask_cors import CORS

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)


    return app