from flask import Flask
from pathlib import Path


def create_app():
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    app.config["UPLOAD_ROOT"] = Path(app.root_path).parent / "uploads"

    app.config["UPLOAD_ROOT"].mkdir(parents=True, exist_ok=True)

    from app.routes.main import main
    app.register_blueprint(main)

    return app
