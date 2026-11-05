"""
Task 3.6 – Model Registry Script
Registers the best model, creates versions, sets alias 'champion',
then loads it by alias to classify one image.

Usage:
  python scripts/model_registry.py --image path/to/test.jpg
"""

import os
import sys
import argparse
import numpy as np
import mlflow
import mlflow.tensorflow
from mlflow import MlflowClient
import tensorflow as tf
from PIL import Image
from dotenv import load_dotenv

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
load_dotenv()

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = "VisionGuard_Champion_23L-0501"
IMG_SIZE = (224, 224)
THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.5"))


def register_model(run_id: str, artifact_path: str = "mobilenet_champion_model"):
    """Register model from an existing MLflow run."""
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()

    model_uri = f"runs:/{run_id}/{artifact_path}"
    result = mlflow.register_model(model_uri, MODEL_NAME)
    version = result.version
    print(f"Registered model '{MODEL_NAME}' version {version}")

    # Transition to Production and set alias 'champion'
    client.set_registered_model_alias(MODEL_NAME, "champion", version)
    print(f"Alias 'champion' set to version {version}")
    return version


def load_by_alias_and_predict(image_path: str):
    """Load champion model by alias and classify an image."""
    mlflow.set_tracking_uri(TRACKING_URI)
    model_uri = f"models:/{MODEL_NAME}@champion"

    print(f"Loading model from: {model_uri}")
    model = mlflow.tensorflow.load_model(model_uri)
    print("Model loaded successfully.")

    # Preprocess
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    prob = float(model.predict(arr, verbose=0)[0][0])
    label = "AI-Generated" if prob >= THRESHOLD else "Real"
    confidence = prob if prob >= THRESHOLD else 1.0 - prob

    print(f"\n--- Prediction ---")
    print(f"Image:      {image_path}")
    print(f"Label:      {label}")
    print(f"Confidence: {confidence:.4f} ({prob:.4f} raw sigmoid)")
    return label, confidence


def list_versions():
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()
    try:
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        print(f"\nModel '{MODEL_NAME}' versions:")
        for v in versions:
            print(f"  Version {v.version} | Aliases: {v.aliases} | Status: {v.status}")
    except Exception as e:
        print(f"Could not list versions: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", help="MLflow run ID to register model from")
    parser.add_argument("--image", help="Image path to classify using champion model")
    parser.add_argument("--list", action="store_true", help="List registered versions")
    args = parser.parse_args()

    if args.run_id:
        register_model(args.run_id)
    if args.list:
        list_versions()
    if args.image:
        load_by_alias_and_predict(args.image)
    if not any([args.run_id, args.image, args.list]):
        print("Usage: python model_registry.py --run-id <id> OR --image <path> OR --list")

