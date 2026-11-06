"""Shared dataset utilities for VisionGuard."""
from pathlib import Path
import os
import random
import yaml
import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[2]

def load_config():
    with (ROOT / "config.yaml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def resolve_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path

def set_seed(seed):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.keras.utils.set_random_seed(seed)

def label_from_path(path):
    name = Path(path).parent.name.lower()
    if "real" in name:
        return "real"
    if "ai" in name or "fake" in name or "generated" in name:
        return "ai_generated"
    raise ValueError(f"Cannot infer class from folder name: {name}")
