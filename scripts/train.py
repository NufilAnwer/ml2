"""
Task 2.1-2.5 – VisionGuard Model Training
  - tf.data pipeline with augmentation
  - Baseline CNN from scratch
  - Transfer learning (MobileNetV2) with two-stage fine-tuning
  - Training discipline: seeds, callbacks
  - Full evaluation: accuracy, precision, recall, F1, ROC-AUC, confusion matrix
  - MLflow experiment tracking (manual + autolog)
"""

import os
import sys
import random
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["PYTHONHASHSEED"] = "42"
random.seed(42)
np.random.seed(42)

import tensorflow as tf
tf.random.set_seed(42)

from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
import mlflow
import mlflow.tensorflow
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────────────────────────────
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_HEAD = 20          # Stage 1: frozen backbone
EPOCHS_FINETUNE = 15      # Stage 2: unfreeze last block
EPOCHS_CNN = 25
THRESHOLD = 0.5
DATA_DIR = Path(os.getenv("DATA_DIR", "data/raw"))
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
SEED = 42
# ──────────────────────────────────────────────────────────────────────────────


# ─── 1. BUILD tf.data PIPELINE ───────────────────────────────────────────────
def make_dataset(split_file: str, training: bool = False) -> tf.data.Dataset:
    """
    Reads a split list (filepath TAB label), returns a tf.data.Dataset.
    Each record is (image_tensor, label).

    Image size: 224×224 chosen for MobileNetV2 compatibility and
    reasonable memory usage. Aspect ratio is distorted (simple resize);
    padding-then-resize would preserve it but adds complexity without
    clear accuracy gain on this task.

    Training: random flip, rotation, zoom, brightness jitter → regularise.
    Val/Test: only decode + resize.
    """
    filepaths, labels = [], []
    with open(split_file) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                filepaths.append(parts[0])
                labels.append(int(parts[1]))

    ds = tf.data.Dataset.from_tensor_slices((filepaths, labels))

    def load_image(path, label):
        raw = tf.io.read_file(path)
        img = tf.image.decode_image(raw, channels=3, expand_animations=False)
        img = tf.image.resize(img, IMG_SIZE)
        img = tf.cast(img, tf.float32) / 255.0
        return img, label

    def augment(img, label):
        img = tf.image.random_flip_left_right(img)
        img = tf.image.random_flip_up_down(img)
        img = tf.image.random_brightness(img, 0.15)
        img = tf.image.random_contrast(img, 0.8, 1.2)
        # Random rotation via keras layers
        img = tf.keras.layers.RandomRotation(0.05)(tf.expand_dims(img, 0))[0]
        img = tf.keras.layers.RandomZoom(0.1)(tf.expand_dims(img, 0))[0]
        img = tf.clip_by_value(img, 0.0, 1.0)
        return img, label

    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(1000, seed=SEED).map(augment, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def build_split_files(data_dir: Path, out_dir: Path = Path("data/splits")):
    """
    Walk data_dir (class sub-folders), split 70/15/15,
    write train.txt, val.txt, test.txt with 'filepath\\tlabel'.
    Returns paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
    assert len(classes) == 2, f"Expected 2 classes, got {classes}"
    label_map = {cls: i for i, cls in enumerate(classes)}

    all_items = []
    for cls in classes:
        for img_path in sorted((data_dir / cls).rglob("*")):
            if img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                all_items.append((str(img_path), label_map[cls]))

    random.shuffle(all_items)
    n = len(all_items)
    train_end = int(0.70 * n)
    val_end = int(0.85 * n)
    splits = {
        "train": all_items[:train_end],
        "val": all_items[train_end:val_end],
        "test": all_items[val_end:],
    }

    for split, items in splits.items():
        fp = out_dir / f"{split}.txt"
        with open(fp, "w") as f:
            for path, label in items:
                f.write(f"{path}\t{label}\n")
        print(f"Wrote {len(items)} items to {fp}")

    # Save label map
    with open(out_dir / "label_map.json", "w") as f:
        json.dump(label_map, f)

    return splits, label_map, str(out_dir / "train.txt"), str(out_dir / "val.txt"), str(out_dir / "test.txt")


# ─── 2. BASELINE CNN ─────────────────────────────────────────────────────────
def build_baseline_cnn(input_shape=(224, 224, 3)) -> tf.keras.Model:
    """
    Small CNN from scratch. Architecture rationale:
      Conv2D 32 → captures low-level edges
      BatchNorm → speeds convergence, normalises activations
      MaxPool → spatial downsampling, translation invariance
      (repeat × 3 with growing filters 64, 128)
      GlobalAveragePool → compact representation, fewer params than Flatten
      Dense 256 + Dropout(0.5) → classification head, prevents overfitting
      Dense 1 sigmoid → binary probability output

    Loss: binary_crossentropy — standard for binary classification.
    Optimizer: Adam with lr=1e-3 — adaptive, robust default.
    Metrics: accuracy + AUC (threshold-independent).
    """
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs

    for filters in [32, 64, 128]:
        x = tf.keras.layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.MaxPooling2D(2)(x)
        x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs, outputs, name="VisionGuard_CNN")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


# ─── 3. TRANSFER LEARNING ────────────────────────────────────────────────────
def build_mobilenet_model(input_shape=(224, 224, 3), trainable_layers=0) -> tf.keras.Model:
    """
    MobileNetV2 pretrained on ImageNet, with custom classification head.
    MobileNetV2 expects inputs preprocessed via
    tf.keras.applications.mobilenet_v2.preprocess_input (scales to [-1, 1]).
    We include this as a Lambda layer so the model is self-contained for serving.
    """
    base = tf.keras.applications.MobileNetV2(
        input_shape=input_shape, include_top=False, weights="imagenet"
    )
    base.trainable = False  # Stage 1: freeze all

    if trainable_layers > 0:
        for layer in base.layers[-trainable_layers:]:
            if not isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = True

    inputs = tf.keras.Input(shape=input_shape)
    # MobileNetV2 preprocessing
    x = tf.keras.layers.Lambda(
        tf.keras.applications.mobilenet_v2.preprocess_input,
        name="mobilenet_preprocess"
    )(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs, outputs, name=f"VisionGuard_MobileNetV2_ft{trainable_layers}")
    return model


def get_callbacks(checkpoint_path: str, patience: int = 5) -> list:
    return [
        tf.keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=patience,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]


# ─── 4. EVALUATION ───────────────────────────────────────────────────────────
def evaluate_model(model, test_ds, threshold=0.5, label="Model", out_dir="eval_output"):
    """
    Full evaluation: accuracy, precision, recall, F1, ROC-AUC,
    confusion matrix, ROC curve. Saves all figures.
    Returns dict of metrics.
    """
    os.makedirs(out_dir, exist_ok=True)

    y_true, y_prob = [], []
    for x_batch, y_batch in test_ds:
        probs = model.predict(x_batch, verbose=0).ravel()
        y_prob.extend(probs.tolist())
        y_true.extend(y_batch.numpy().tolist())

    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    y_pred = (y_prob >= threshold).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob),
    }

    print(f"\n{'='*50}")
    print(f"Evaluation: {label}")
    for k, v in metrics.items():
        print(f"  {k:12s}: {v:.4f}")
    print(f"{'='*50}\n")

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["Real", "AI-Gen"], yticklabels=["Real", "AI-Gen"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix – {label}")
    cm_path = os.path.join(out_dir, f"confusion_matrix_{label.replace(' ', '_')}.png")
    fig.savefig(cm_path, bbox_inches="tight", dpi=100)
    plt.close(fig)

    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(fpr, tpr, label=f"AUC = {metrics['roc_auc']:.4f}", color="steelblue")
    ax.plot([0, 1], [0, 1], "k--")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title(f"ROC Curve – {label}")
    ax.legend()
    roc_path = os.path.join(out_dir, f"roc_curve_{label.replace(' ', '_')}.png")
    fig.savefig(roc_path, bbox_inches="tight", dpi=100)
    plt.close(fig)

    return metrics, cm_path, roc_path, y_true, y_prob


def plot_training_curves(history, label="Model", best_epoch=None, out_dir="eval_output"):
    os.makedirs(out_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for ax, metric in zip(axes, ["loss", "accuracy"]):
        ax.plot(history.history[metric], label=f"Train {metric}")
        ax.plot(history.history[f"val_{metric}"], label=f"Val {metric}")
        if best_epoch is not None:
            ax.axvline(best_epoch, color="red", linestyle="--", label=f"Best epoch {best_epoch+1}")
        ax.set_xlabel("Epoch")
        ax.set_ylabel(metric.capitalize())
        ax.set_title(f"{label} – {metric.capitalize()}")
        ax.legend()

    fig.suptitle(f"Training Curves – {label}")
    path = os.path.join(out_dir, f"training_curves_{label.replace(' ', '_')}.png")
    fig.savefig(path, bbox_inches="tight", dpi=100)
    plt.close(fig)
    return path


def show_misclassified(model, test_ds, threshold=0.5, n=10, out_dir="eval_output"):
    """Plot n misclassified images."""
    os.makedirs(out_dir, exist_ok=True)
    wrong_imgs, wrong_true, wrong_pred, wrong_prob = [], [], [], []

    for x_batch, y_batch in test_ds:
        probs = model.predict(x_batch, verbose=0).ravel()
        preds = (probs >= threshold).astype(int)
        y_np = y_batch.numpy()
        for i, (yt, yp, prob, img) in enumerate(zip(y_np, preds, probs, x_batch.numpy())):
            if yt != yp and len(wrong_imgs) < n:
                wrong_imgs.append(img)
                wrong_true.append(int(yt))
                wrong_pred.append(int(yp))
                wrong_prob.append(float(prob))
        if len(wrong_imgs) >= n:
            break

    if not wrong_imgs:
        print("No misclassified images found.")
        return

    cols = 5
    rows = (len(wrong_imgs) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    axes = axes.ravel()
    label_names = {0: "Real", 1: "AI-Gen"}

    for i, (img, yt, yp, prob) in enumerate(zip(wrong_imgs, wrong_true, wrong_pred, wrong_prob)):
        axes[i].imshow(np.clip(img, 0, 1))
        axes[i].set_title(f"True:{label_names[yt]}\nPred:{label_names[yp]} ({prob:.2f})", fontsize=7)
        axes[i].axis("off")
    for j in range(len(wrong_imgs), len(axes)):
        axes[j].axis("off")

    fig.suptitle("Misclassified Test Images", fontsize=12)
    path = os.path.join(out_dir, "misclassified.png")
    fig.savefig(path, bbox_inches="tight", dpi=100)
    plt.close(fig)
    print(f"Saved misclassified grid: {path}")
    return path


# ─── 5. MAIN TRAINING LOOP ───────────────────────────────────────────────────
def train_cnn(train_ds, val_ds, test_ds, mlflow_run_name="baseline_cnn"):
    """Train the scratch CNN and log to MLflow."""
    model = build_baseline_cnn()
    model.summary()

    with mlflow.start_run(run_name=mlflow_run_name) as run:
        mlflow.log_params({
            "model_type": "baseline_cnn",
            "img_size": str(IMG_SIZE),
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS_CNN,
            "optimizer": "adam",
            "learning_rate": 1e-3,
            "seed": SEED,
        })

        callbacks = get_callbacks(str(MODELS_DIR / "cnn_best.keras"))
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=EPOCHS_CNN,
            callbacks=callbacks,
        )

        best_epoch = np.argmin(history.history["val_loss"])
        curve_path = plot_training_curves(history, "Baseline_CNN", best_epoch)

        metrics, cm_path, roc_path, y_true, y_prob = evaluate_model(
            model, test_ds, THRESHOLD, "Baseline_CNN"
        )

        for k, v in metrics.items():
            mlflow.log_metric(f"test_{k}", v)
        mlflow.log_artifact(curve_path)
        mlflow.log_artifact(cm_path)
        mlflow.log_artifact(roc_path)
        mlflow.tensorflow.log_model(model, "baseline_cnn_model")

        return model, history, metrics, run.info.run_id


def train_mobilenet(train_ds, val_ds, test_ds):
    """Two-stage fine-tuning of MobileNetV2 and log to MLflow."""

    # Stage 1: frozen backbone
    with mlflow.start_run(run_name="mobilenet_stage1_frozen") as run:
        model = build_mobilenet_model()
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-3),
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
        )
        mlflow.log_params({
            "model_type": "MobileNetV2",
            "stage": "frozen_backbone",
            "img_size": str(IMG_SIZE),
            "batch_size": BATCH_SIZE,
            "epochs_stage1": EPOCHS_HEAD,
            "lr_stage1": 1e-3,
            "seed": SEED,
        })

        callbacks = get_callbacks(str(MODELS_DIR / "mobilenet_stage1.keras"), patience=6)
        hist1 = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_HEAD, callbacks=callbacks)

        best_ep1 = np.argmin(hist1.history["val_loss"])
        curve1 = plot_training_curves(hist1, "MobileNetV2_Stage1", best_ep1)
        mlflow.log_artifact(curve1)
        mlflow.log_params({"best_epoch_stage1": best_ep1 + 1})

    # Stage 2: unfreeze last 30 layers (last block of MobileNetV2)
    with mlflow.start_run(run_name="mobilenet_stage2_finetune") as run:
        model_ft = build_mobilenet_model(trainable_layers=30)
        model_ft.set_weights(model.get_weights())   # carry over head weights

        model_ft.compile(
            optimizer=tf.keras.optimizers.Adam(1e-5),   # much smaller lr
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
        )

        trainable_names = [l.name for l in model_ft.layers if l.trainable]
        mlflow.log_params({
            "model_type": "MobileNetV2",
            "stage": "finetune_last30",
            "lr_stage2": 1e-5,
            "trainable_layers_count": len(trainable_names),
            "seed": SEED,
        })
        mlflow.log_text(str(trainable_names), "trainable_layers.txt")

        callbacks_ft = get_callbacks(str(MODELS_DIR / "mobilenet_champion.keras"), patience=5)
        hist2 = model_ft.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_FINETUNE, callbacks=callbacks_ft)

        best_ep2 = np.argmin(hist2.history["val_loss"])
        curve2 = plot_training_curves(hist2, "MobileNetV2_Stage2", best_ep2)

        metrics, cm_path, roc_path, y_true, y_prob = evaluate_model(
            model_ft, test_ds, THRESHOLD, "MobileNetV2_Champion"
        )
        miss_path = show_misclassified(model_ft, test_ds, THRESHOLD)

        for k, v in metrics.items():
            mlflow.log_metric(f"test_{k}", v)
        for art in [curve2, cm_path, roc_path, miss_path]:
            if art:
                mlflow.log_artifact(art)
        mlflow.tensorflow.log_model(model_ft, "mobilenet_champion_model")

        # Save champion
        model_ft.save(str(MODELS_DIR / "champion_model.keras"))
        print("Champion model saved.")

        return model_ft, hist2, metrics, run.info.run_id


def main():
    # Setup MLflow
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("VisionGuard_23L-0501_A2_Ops")

    # Build splits
    splits, label_map, train_file, val_file, test_file = build_split_files(DATA_DIR)
    print(f"Label map: {label_map}")

    train_ds = make_dataset(train_file, training=True)
    val_ds = make_dataset(val_file, training=False)
    test_ds = make_dataset(test_file, training=False)

    print("\n--- Training Baseline CNN ---")
    cnn_model, cnn_hist, cnn_metrics, cnn_run_id = train_cnn(train_ds, val_ds, test_ds)

    print("\n--- Training MobileNetV2 (Transfer Learning) ---")
    mn_model, mn_hist, mn_metrics, mn_run_id = train_mobilenet(train_ds, val_ds, test_ds)

    print("\nAll training complete.")
    print(f"CNN test metrics: {cnn_metrics}")
    print(f"MobileNetV2 test metrics: {mn_metrics}")


if __name__ == "__main__":
    main()

