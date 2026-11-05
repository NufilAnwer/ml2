"""
VisionGuard – Flask Application
Tasks 4 (web app), 5 (database), 8 (cloud API integration)

Routes:
  GET  /             → upload page
  POST /predict      → run inference, log to DB, show result
  GET  /history      → paginated prediction history from DB
  GET  /health       → health check (JSON)
  GET  /api/predict  → JSON API endpoint (for cloud/postman)
"""

import os
import io
import logging
import hashlib
import re
from datetime import datetime, timezone

from flask import (
    Flask, request, render_template, redirect, url_for,
    jsonify, flash, abort, make_response
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

# ─── App configuration ───────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10 MB
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp", "gif"}
MODEL_VERSION = os.getenv("MODEL_PATH", "models/champion_model.keras")
CLOUD_API_URL = os.getenv("CLOUD_API_URL", "")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET", "")

# ─── Lazy imports (avoid loading TF if model not needed) ─────────
def _get_inference():
    from app.inference import predict as local_predict
    return local_predict

def _get_db():
    from app.database import init_db, SessionLocal, log_prediction, PredictionLog
    return init_db, SessionLocal, log_prediction, PredictionLog

# Initialize DB
try:
    init_db_fn, _, _, _ = _get_db()
    init_db_fn()
    logger.info("Database initialized.")
except Exception as e:
    logger.warning(f"DB init failed: {e}")


# ─── Helpers ─────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Secure filename: strip path traversal, limit length, alphanumeric+dot+dash."""
    name = secure_filename(filename)
    # Keep only safe characters
    name = re.sub(r"[^a-zA-Z0-9_.\-]", "_", name)
    return name[:200] or "upload"


def validate_image_bytes(data: bytes) -> bool:
    """Verify the bytes actually decode as an image (not just magic bytes)."""
    from PIL import Image, UnidentifiedImageError
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        return True
    except (UnidentifiedImageError, Exception):
        return False


def _call_cloud_api(image_bytes: bytes, filename: str) -> dict:
    """
    Forward the image to the cloud/Vercel model API.
    Returns prediction dict on success, raises on failure.
    """
    import requests as req
    headers = {}
    if CLOUD_API_SECRET:
        headers["X-API-Secret"] = CLOUD_API_SECRET
    resp = req.post(
        f"{CLOUD_API_URL}/predict",
        files={"file": (filename, image_bytes, "image/jpeg")},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ─── Routes ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Upload + inference route.
    Validates file type, size, and content, runs inference,
    logs to DB, discards uploaded bytes from memory.
    """
    _, SessionLocal, log_prediction_fn, _ = _get_db()

    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", "error")
        return render_template("error.html", message="Invalid file type. Please upload an image."), 400

    safe_name = sanitize_filename(file.filename)
    image_bytes = file.read()
    file_size = len(image_bytes)

    # Content validation
    if not validate_image_bytes(image_bytes):
        flash("File looks like an image but could not be decoded.", "error")
        return render_template("error.html", message="Corrupted or invalid image file."), 422

    client_ip = request.remote_addr
    result = None
    error_msg = None

    try:
        # Prefer cloud API if configured; fall back to local
        if CLOUD_API_URL:
            result = _call_cloud_api(image_bytes, safe_name)
        else:
            predict_fn = _get_inference()
            result = predict_fn(image_bytes)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Inference error: {e}")
        result = {
            "label": "ERROR",
            "confidence": 0.0,
            "raw_score": 0.0,
            "threshold": float(os.getenv("DECISION_THRESHOLD", "0.5")),
            "model_path": MODEL_VERSION,
        }

    # Log to database
    db = SessionLocal()
    try:
        record = log_prediction_fn(db, safe_name, result, file_size, client_ip, error_msg)
        record_id = record.id
    except Exception as db_err:
        logger.error(f"DB logging error: {db_err}")
        record_id = None
    finally:
        db.close()

    # Discard bytes — do NOT save to disk
    del image_bytes

    if error_msg:
        return render_template(
            "result.html",
            error=error_msg,
            filename=safe_name,
            result=None,
        ), 500

    return render_template(
        "result.html",
        filename=safe_name,
        result=result,
        record_id=record_id,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


@app.route("/history")
def history():
    """Show paginated prediction history from database."""
    _, SessionLocal, _, PredictionLog = _get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 20
    db = SessionLocal()
    try:
        total = db.query(PredictionLog).count()
        records = (
            db.query(PredictionLog)
            .order_by(PredictionLog.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        records_dicts = [r.to_dict() for r in records]
    finally:
        db.close()

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "history.html",
        records=records_dicts,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route("/health")
def health():
    """Health check endpoint for Docker Compose and load balancers."""
    db_ok = False
    model_ok = os.path.exists(MODEL_VERSION)
    try:
        _, SessionLocal, _, PredictionLog = _get_db()
        db = SessionLocal()
        db.query(PredictionLog).count()
        db.close()
        db_ok = True
    except Exception as e:
        logger.warning(f"Health check DB error: {e}")

    status = "healthy" if (db_ok and model_ok) else "degraded"
    return jsonify({
        "status": status,
        "database": "ok" if db_ok else "error",
        "model": "ok" if model_ok else "not_found",
        "model_path": MODEL_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200 if status == "healthy" else 503


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    JSON API endpoint for Postman / cloud integration (Task 7, 8).
    Expects multipart/form-data with field 'file'.
    Returns JSON prediction result.
    """
    _, SessionLocal, log_prediction_fn, _ = _get_db()

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not allowed_file(file.filename or ""):
        return jsonify({"error": "Invalid file type"}), 400

    safe_name = sanitize_filename(file.filename or "image.jpg")
    image_bytes = file.read()

    if not validate_image_bytes(image_bytes):
        return jsonify({"error": "Corrupt or invalid image"}), 422

    try:
        predict_fn = _get_inference()
        result = predict_fn(image_bytes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    client_ip = request.remote_addr
    db = SessionLocal()
    try:
        log_prediction_fn(db, safe_name, result, len(image_bytes), client_ip)
    finally:
        db.close()

    del image_bytes
    return jsonify(result), 200


@app.errorhandler(413)
def file_too_large(e):
    return render_template("error.html", message="File too large. Maximum size is 10 MB."), 413


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Internal server error. Please try again."), 500


if __name__ == "__main__":
    # Run with Waitress (production WSGI) instead of Flask dev server
    from waitress import serve
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting VisionGuard on port {port} (production mode)")
    serve(app, host="0.0.0.0", port=port)

