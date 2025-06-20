from flask import Flask
from .routes import bp as main_bp
import os

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_path = os.path.join(base_dir, '..', 'templates')
    static_path = os.path.join(base_dir, '..', 'static')

    app = Flask(
        __name__,
        template_folder=templates_path,
        static_folder=static_path
    )
    app.secret_key = os.urandom(24)

    app.register_blueprint(main_bp)
    return app