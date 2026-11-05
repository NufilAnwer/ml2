"""
Task 1.1 Environment Setup & Library Verification
Logs system platform, Python executable, and exact installed versions
of all core libraries, plus checks TensorFlow GPU availability.
"""

import sys
import platform
import importlib.metadata

print("=" * 65)
print("VisionGuard Environment & Library Verification")
print("=" * 65)

print(f"OS Platform       : {platform.system()} {platform.release()} ({platform.architecture()[0]})")
print(f"Python Version    : {platform.python_version()}")
print(f"Python Executable : {sys.executable}")
print("-" * 65)

packages = [
    ("TensorFlow", "tensorflow"),
    ("Keras", "keras"),
    ("Keras Tuner", "keras-tuner"),
    ("MLflow", "mlflow"),
    ("DagsHub", "dagshub"),
    ("DVC", "dvc"),
    ("Scikit-Learn", "scikit-learn"),
    ("Pandas", "pandas"),
    ("NumPy", "numpy"),
    ("Pillow", "pillow"),
    ("Matplotlib", "matplotlib"),
    ("Seaborn", "seaborn"),
    ("Flask", "flask"),
    ("Requests", "requests"),
    ("Python-Dotenv", "python-dotenv"),
    ("SQLAlchemy", "sqlalchemy"),
]

for label, pkg_name in packages:
    try:
        ver = importlib.metadata.version(pkg_name)
        print(f"{label:<18}: {ver}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{label:<18}: NOT INSTALLED")

print("-" * 65)
try:
    import os
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    import tensorflow as tf
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        print(f"Available GPUs    : {gpus}")
    else:
        print("Available GPUs    : None detected (Running in CPU mode)")
except Exception as e:
    print(f"Available GPUs    : None detected (Running in CPU mode - {e})")
print("=" * 65)
