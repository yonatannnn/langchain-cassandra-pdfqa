from flask import Flask
from flask_cors import CORS
import os


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["UPLOAD_DIR"] = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    from .errors import register_error_handlers
    register_error_handlers(app)

    from .routes.health import health_bp
    from .routes.documents import documents_bp
    from .routes.qa import qa_bp
    from .routes.ui import ui_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp, url_prefix="/documents")
    app.register_blueprint(qa_bp, url_prefix="/qa")
    app.register_blueprint(ui_bp)

    return app
