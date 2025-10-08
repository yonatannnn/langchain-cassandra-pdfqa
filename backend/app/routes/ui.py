import os
from flask import Blueprint, send_from_directory

ui_bp = Blueprint("ui", __name__)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend"))


@ui_bp.get("/ui")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@ui_bp.get("/static/<path:filename>")
def static_files(filename: str):
    return send_from_directory(FRONTEND_DIR, filename)
