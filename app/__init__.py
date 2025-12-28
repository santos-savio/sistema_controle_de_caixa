from flask import Flask
from .db import db


def create_app(config_object: str = "config.Config") -> Flask:
    """Application factory creating the Flask app and initializing extensions.

    Args:
        config_object: import string for configuration (optional)
    Returns:
        Flask app instance
    """
    app = Flask(__name__, instance_relative_config=False, template_folder='../templates')
    app.config.from_object(config_object)

    # initialize extensions
    db.init_app(app)

    # register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
