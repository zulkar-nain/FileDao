import os

from flask import Flask
from flask_socketio import SocketIO

from .config import Config

socketio = SocketIO(cors_allowed_origins='*', async_mode='eventlet')


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    socketio.init_app(app)
    from . import sockets  # noqa: F401

    return app
