"""
Task 4.1 – Inference Module
Loads the champion Keras model once at startup.
Returns (label, confidence) for any uploaded image.

Design decisions:
  - Model loaded at module import time (singleton) → one-time GPU/CPU
    warm-up cost paid at startup, NOT on every request (which would be
    10-50x slower and cause timeout errors under load).
  - Preprocessing is IDENTICAL to training: resize to 224×224, divide by 255,
    expand dims for batch axis. Mismatch would silently degrade accuracy.
  - MobileNetV2's preprocess_input (scales to [-1,1]) is baked into the
    saved Keras model as a Lambda layer, so we do NOT call it again here.
"""

import os
import io
import logging
from pathlib import Path

import numpy as np
from PIL import Image
import tensorflow as tf

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

logger = logging.getLogger(__name__)

IMG_SIZE = (224, 224)
THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.5"))
MODEL_PATH = os.getenv("MODEL_PATH", "models/champion_model.keras")

# Singleton model - loaded once at startup
_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model

    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        logger.warning(f"Model not found at {MODEL_PATH}. Inference will fail.")
        return None

    logger.info(f"Loading model from {MODEL_PATH} ...")
    _model = tf.keras.models.load_model(str(model_path))
    logger.info("Model loaded successfully.")
    return _model


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Convert raw bytes → (1, 224, 224, 3) float32 tensor [0, 1].
    Resize via PIL LANCZOS for high quality.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def predict(image_bytes: bytes) -> dict:
    """
    Returns:
      {
        "label": "AI-Generated" | "Real",
        "confidence": float [0, 1],
        "raw_score": float,
        "threshold": float,
        "model_path": str,
      }
    Raises RuntimeError if model is not loaded.
    """
    model = _load_model()
    if model is None:
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Train and save the model first.")

    arr = preprocess_image(image_bytes)
    raw_score = float(model.predict(arr, verbose=0)[0][0])

    is_ai = raw_score >= THRESHOLD
    label = "AI-Generated" if is_ai else "Real"
    confidence = raw_score if is_ai else (1.0 - raw_score)

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "raw_score": round(raw_score, 4),
        "threshold": THRESHOLD,
        "model_path": MODEL_PATH,
    }


# Pre-warm model at import time
_load_model()

