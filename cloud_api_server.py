"""
Cloud API Server (Task 7)
Runs the model as a standalone REST API on a cloud VM (Oracle/GCP/AWS).
Flask runs locally; this server is called remotely.

Deploy this file on your cloud VM and run:
  python cloud_api_server.py

Flask (local) calls: POST {CLOUD_API_URL}/predict with multipart image.
"""

import os
import io
import logging
from pathlib import Path

import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import tensorflow as tf
from dotenv import load_dotenv

load_dotenv()
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud_api")

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.getenv("MODEL_PATH", "models/champion_model.keras")
THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.5"))
API_SECRET = os.getenv("CLOUD_API_SECRET", "")
IMG_SIZE = (224, 224)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

_model = None


def load_model():
    global _model
    if _model is not None:
        return _model
    p = Path(MODEL_PATH)
    if not p.exists():
        logger.error(f"Model not found: {MODEL_PATH}")
        return None
    logger.info(f"Loading model: {MODEL_PATH}")
    _model = tf.keras.models.load_model(str(p))
    logger.info("Model ready.")
    return _model


load_model()


def check_secret():
    """Validate API secret header if configured."""
    if not API_SECRET:
        return True
    return request.headers.get("X-API-Secret", "") == API_SECRET


@app.route("/health", methods=["GET"])
def health():
    model_ok = _model is not None
    return jsonify({
        "status": "healthy" if model_ok else "model_not_loaded",
        "model": MODEL_PATH,
    }), 200 if model_ok else 503


@app.route("/predict", methods=["POST"])
def predict():
    if not check_secret():
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Invalid file type"}), 400

    image_bytes = file.read()
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)
    except Exception as e:
        return jsonify({"error": f"Image decode failed: {e}"}), 422

    model = load_model()
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    raw_score = float(model.predict(arr, verbose=0)[0][0])
    is_ai = raw_score >= THRESHOLD
    label = "AI-Generated" if is_ai else "Real"
    confidence = raw_score if is_ai else (1.0 - raw_score)

    return jsonify({
        "label": label,
        "confidence": round(confidence, 4),
        "raw_score": round(raw_score, 4),
        "threshold": THRESHOLD,
        "model_path": MODEL_PATH,
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    logger.info(f"Cloud API running on port {port}")
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)

