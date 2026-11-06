"""One-shot test evaluation, ROC/CM plots and ten misclassified examples."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from PIL import Image
from src.data.common import load_config, resolve_path
from src.data.pipeline import make_dataset

def main():
    cfg = load_config()
    model_path = resolve_path("models/champion.keras")
    if not model_path.exists():
        raise FileNotFoundError("Copy the chosen registered champion model to models/champion.keras first.")
    model = tf.keras.models.load_model(model_path)
    test_ds = make_dataset("test", model_name="mobilenet" if "mobilenet" in model.name else "cnn")
    y_true = np.concatenate([labels.numpy() for _, labels in test_ds]).astype(int)
    probabilities = model.predict(test_ds, verbose=1).reshape(-1)
    val_ds = make_dataset("validation", model_name="mobilenet" if "mobilenet" in model.name else "cnn")
    val_y = np.concatenate([labels.numpy() for _, labels in val_ds]).astype(int)
    val_p = model.predict(val_ds, verbose=0).reshape(-1)
    # Select threshold by maximum validation F1; test data is not used for threshold selection.
    thresholds = np.linspace(0.1, 0.9, 81)
    threshold = max(thresholds, key=lambda t: f1_score(val_y, (val_p >= t).astype(int), zero_division=0))
    predictions = (probabilities >= threshold).astype(int)
    metrics = {"threshold": float(threshold), "accuracy": float(accuracy_score(y_true, predictions)),
               "precision": float(precision_score(y_true, predictions, zero_division=0)),
               "recall": float(recall_score(y_true, predictions, zero_division=0)),
               "f1": float(f1_score(y_true, predictions, zero_division=0)),
               "roc_auc": float(roc_auc_score(y_true, probabilities))}
    out = resolve_path("reports/evaluation")
    out.mkdir(parents=True, exist_ok=True)
    (resolve_path("metrics.json")).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    cm = confusion_matrix(y_true, predictions)
    plt.figure(figsize=(5, 4)); sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["real", "AI-generated"], yticklabels=["real", "AI-generated"])
    plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.tight_layout()
    plt.savefig(out / "confusion_matrix.png", dpi=160); plt.close()
    fpr, tpr, _ = roc_curve(y_true, probabilities)
    plt.figure(figsize=(5, 4)); plt.plot(fpr, tpr, label=f"AUC={metrics['roc_auc']:.3f}")
    plt.plot([0, 1], [0, 1], "--"); plt.xlabel("False positive rate"); plt.ylabel("True positive rate")
    plt.legend(); plt.tight_layout(); plt.savefig(out / "roc_curve.png", dpi=160); plt.close()
    manifest = pd.read_csv(resolve_path("data/splits/test.csv"))
    wrong = np.where(predictions != y_true)[0][:10]
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    for ax, index in zip(axes.flat, wrong):
        ax.imshow(Image.open(manifest.iloc[index]["path"]).convert("RGB"))
        ax.set_title(f"True {y_true[index]} / Pred {predictions[index]}\nP(AI)={probabilities[index]:.2f}")
        ax.axis("off")
    for ax in list(axes.flat)[len(wrong):]:
        ax.axis("off")
    plt.tight_layout(); plt.savefig(out / "misclassified_10.png", dpi=160); plt.close()
    print(json.dumps(metrics, indent=2))
    print("Figures:", out)

if __name__ == "__main__":
    main()
