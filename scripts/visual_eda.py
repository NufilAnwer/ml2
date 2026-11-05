"""
Task 1.3 – Visual EDA
Generates:
  - Grid of sample images per class
  - Histograms of width, height, file-size per class
Run after dataset_audit.py has produced dataset_audit.csv
"""

import csv
import sys
import os
import random
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def load_audit(csv_path: str = "dataset_audit.csv") -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sample_grid(rows: list[dict], n_per_class: int = 8, out_path: str = "eda_sample_grid.png"):
    """Plot a grid of sample images for each class."""
    classes = sorted(set(r["class"] for r in rows))
    n_classes = len(classes)
    fig, axes = plt.subplots(n_classes, n_per_class, figsize=(2.5 * n_per_class, 2.8 * n_classes))

    if n_classes == 1:
        axes = [axes]

    for row_i, cls in enumerate(classes):
        cls_rows = [r for r in rows if r["class"] == cls and r["readable"] == "True"]
        sample = random.sample(cls_rows, min(n_per_class, len(cls_rows)))

        for col_i in range(n_per_class):
            ax = axes[row_i][col_i]
            ax.axis("off")
            if col_i < len(sample):
                try:
                    img = Image.open(sample[col_i]["filepath"]).convert("RGB")
                    ax.imshow(img)
                    ax.set_title(cls, fontsize=7)
                except Exception:
                    pass

    plt.suptitle("Sample Images per Class", fontsize=14, y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", dpi=100)
    plt.close()
    print(f"Saved: {out_path}")


def histograms(rows: list[dict], out_path: str = "eda_histograms.png"):
    """Width, height, file-size histograms per class."""
    classes = sorted(set(r["class"] for r in rows))
    readable = [r for r in rows if r["readable"] == "True"]

    fig, axes = plt.subplots(3, len(classes), figsize=(6 * len(classes), 12))
    if len(classes) == 1:
        axes = [[axes[0]], [axes[1]], [axes[2]]]

    metrics = [
        ("width", "Width (px)", "steelblue"),
        ("height", "Height (px)", "seagreen"),
        ("file_size_bytes", "File Size (bytes)", "tomato"),
    ]

    for col_i, cls in enumerate(classes):
        cls_rows = [r for r in readable if r["class"] == cls]
        for row_i, (field, label, color) in enumerate(metrics):
            vals = [int(r[field]) for r in cls_rows]
            axes[row_i][col_i].hist(vals, bins=40, color=color, edgecolor="white", alpha=0.85)
            axes[row_i][col_i].set_title(f"{cls} – {label}", fontsize=10)
            axes[row_i][col_i].set_xlabel(label, fontsize=8)
            axes[row_i][col_i].set_ylabel("Count", fontsize=8)

    plt.suptitle("Distribution of Width, Height and File Size per Class", fontsize=14, y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", dpi=100)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "dataset_audit.csv"
    rows = load_audit(csv_path)
    os.makedirs("eda_output", exist_ok=True)
    sample_grid(rows, out_path="eda_output/eda_sample_grid.png")
    histograms(rows, out_path="eda_output/eda_histograms.png")
    print("EDA complete.")

