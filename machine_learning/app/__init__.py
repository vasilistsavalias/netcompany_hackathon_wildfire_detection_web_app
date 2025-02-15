from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import configuration

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Import blueprints (routes)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app