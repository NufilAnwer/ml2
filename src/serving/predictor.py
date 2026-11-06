"""Load a model once and apply the same resize/scale used during training."""
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO

class Predictor:
    def __init__(self, model_path=None, threshold=None, image_size=None, model_family=None):
        model_path = model_path or os.getenv("MODEL_PATH", "models/champion.keras")
        self.threshold = float(threshold if threshold is not None else os.getenv("MODEL_THRESHOLD", "0.5"))
        self.image_size = image_size or (int(os.getenv("IMAGE_HEIGHT", "224")), int(os.getenv("IMAGE_WIDTH", "224")))
        self.model_family = model_family or os.getenv("MODEL_FAMILY", "cnn")
        self.model = tf.keras.models.load_model(model_path)

    def prepare(self, image_bytes):
        with Image.open(BytesIO(image_bytes)) as image:
            image = image.convert("RGB").resize((self.image_size[1], self.image_size[0]))
            array = np.asarray(image, dtype=np.float32)
        if self.model_family == "mobilenet":
            array = tf.keras.applications.mobilenet_v2.preprocess_input(array)
        else:
            array = array / 255.0
        return np.expand_dims(array, axis=0)

    def predict(self, image_bytes):
        probability = float(self.model.predict(self.prepare(image_bytes), verbose=0).reshape(-1)[0])
        label = "AI-generated" if probability >= self.threshold else "Real"
        confidence = probability if probability >= self.threshold else 1.0 - probability
        return {"label": label, "confidence": confidence, "ai_probability": probability,
                "threshold": self.threshold, "model": self.model.name,
                "caveat": "This is a model estimate, not proof of an image's origin."}
