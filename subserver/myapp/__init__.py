from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from myapp.config import Config
from myapp.database import db

socket = SocketIO()
cors = CORS()


def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    socket.init_app(app, cors_allowed_origins="*")
    cors.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    from .views import views
    app.register_blueprint(views)


def create_app():
    """Create Flask app and initialize extensions."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    with app.app_context():
        try:
            # Create database tables if they don't exist
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")

        # Register blueprints
        register_blueprints(app)

    return app, socket
