"""Flask upload/history UI. Inference is delegated to the remote model API."""
import os
from io import BytesIO
from pathlib import Path
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from sqlalchemy import text
from web.database import db, Prediction

load_dotenv()
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "local-development-only")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///visionguard.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/predict")
    def predict():
        upload = request.files.get("file")
        if not upload or not upload.filename:
            flash("Choose an image first.", "error")
            return redirect(url_for("index"))
        safe_name = secure_filename(upload.filename)[:255] or "uploaded-image"
        if upload.mimetype not in ALLOWED_TYPES:
            flash("Unsupported file type. Use JPEG, PNG, WEBP or BMP.", "error")
            return redirect(url_for("index"))
        payload = upload.read()
        try:
            with Image.open(BytesIO(payload)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            flash("The uploaded file is not a readable image.", "error")
            return redirect(url_for("index"))
        api_url = os.getenv("MODEL_API_URL", "").rstrip("/")
        if not api_url:
            flash("MODEL_API_URL is not configured.", "error")
            return redirect(url_for("index"))
        try:
            response = requests.post(f"{api_url}/predict",
                headers={"X-API-Key": os.getenv("MODEL_API_KEY", "")},
                files={"file": (safe_name, payload, upload.mimetype)}, timeout=90)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException:
            flash("The inference service is unavailable. Please try again later.", "error")
            return redirect(url_for("index"))
        record = Prediction(filename=safe_name, label=result["label"],
            confidence=float(result["confidence"]), model_name=result["model"],
            ai_probability=float(result["ai_probability"]))
        db.session.add(record)
        db.session.commit()
        return render_template("result.html", result=result, filename=safe_name)

    @app.get("/history")
    def history():
        rows = Prediction.query.order_by(Prediction.created_at.desc()).limit(200).all()
        return render_template("history.html", rows=rows)

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}, 200
        except Exception:
            return {"status": "degraded", "database": "unavailable"}, 503

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("error.html", message="Image exceeds the upload size limit."), 413

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
