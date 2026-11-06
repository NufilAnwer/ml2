"""Standalone authenticated inference API for cloud deployment."""
import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.serving.predictor import Predictor

load_dotenv()
app = FastAPI(title="VisionGuard Inference API", version="1.0.0")
predictor = None

@app.on_event("startup")
def load_champion():
    global predictor
    model_path = os.getenv("MODEL_PATH", "models/champion.keras")
    if os.path.exists(model_path):
        predictor = Predictor(model_path=model_path)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": predictor is not None}

@app.post("/predict")
async def predict(file: UploadFile = File(...), x_api_key: str = Header(default="")):
    expected = os.getenv("API_KEY", "")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/bmp"}:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, WEBP or BMP image")
    payload = await file.read()
    if len(payload) > int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds upload limit")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Champion model is not available")
    try:
        return predictor.predict(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="File could not be decoded as an image")
