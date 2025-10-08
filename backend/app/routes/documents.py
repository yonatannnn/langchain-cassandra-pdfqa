import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..services.ingest import ingest_pdf_to_vectorstore
from ..services.mongo import mongo_db

ALLOWED_EXTENSIONS = {"pdf"}

documents_bp = Blueprint("documents", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.post("/upload")
def upload_document():
    device_id = request.form.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"error": "No file uploaded"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    upload_dir = current_app.config["UPLOAD_DIR"]
    os.makedirs(upload_dir, exist_ok=True)

    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}_{filename}"
    file_path = os.path.join(upload_dir, stored_filename)
    file.save(file_path)

    documents = mongo_db().get_collection("documents")
    now = datetime.utcnow()
    doc_record = {
        "_id": doc_id,
        "device_id": device_id,
        "filename": filename,
        "stored_filename": stored_filename,
        "path": file_path,
        "created_at": now,
        "updated_at": now,
        "deleted": False,
        "mime_type": "application/pdf",
        "size": os.path.getsize(file_path),
    }
    documents.insert_one(doc_record)

    try:
        chunks_count = ingest_pdf_to_vectorstore(
            file_path=file_path,
            device_id=device_id,
            document_id=doc_id,
        )
    except Exception as e:
        return jsonify({"error": "Failed to ingest document", "detail": str(e)}), 500

    return jsonify({"doc_id": doc_id, "chunks_indexed": chunks_count}), 201


@documents_bp.get("")
def list_documents():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    documents = mongo_db().get_collection("documents")
    docs = list(
        documents.find({"device_id": device_id, "deleted": False}, {"path": 0})
    )
    for d in docs:
        d["_id"] = str(d["_id"])  # normalize to string
    return jsonify({"documents": docs})


@documents_bp.delete("/<doc_id>")
def delete_document(doc_id: str):
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    documents = mongo_db().get_collection("documents")
    res = documents.update_one(
        {"_id": doc_id, "device_id": device_id},
        {"$set": {"deleted": True, "updated_at": datetime.utcnow()}},
    )
    if res.matched_count == 0:
        return jsonify({"error": "Document not found"}), 404

    return jsonify({"ok": True})
