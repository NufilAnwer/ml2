"""Create sample grids and per-class width, height and file-size histograms."""
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from src.data.common import load_config, resolve_path
from src.data.audit import audit_dataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None)
    args = parser.parse_args()
    config = load_config()
    dataset = resolve_path(args.dataset or config["data"]["root"])
    output = resolve_path("data/eda")
    output.mkdir(parents=True, exist_ok=True)
    audit_path = resolve_path("data/audit/image_audit.csv")
    frame = pd.read_csv(audit_path) if audit_path.exists() else audit_dataset(dataset)
    valid = frame[frame["readable"] == True].copy()
    classes = sorted(valid["class"].dropna().unique())
    fig, axes = plt.subplots(max(1, len(classes)), 5, figsize=(15, 3 * max(1, len(classes))))
    if len(classes) == 1:
        axes = [axes]
    for row, label in enumerate(classes):
        samples = valid[valid["class"] == label].head(5)
        for col, (_, record) in enumerate(samples.iterrows()):
            with Image.open(record["path"]) as image:
                axes[row][col].imshow(image.convert("RGB"))
            axes[row][col].set_title(label)
            axes[row][col].axis("off")
    fig.tight_layout()
    fig.savefig(output / "sample_grid.png", dpi=160)
    plt.close(fig)
    for column in ["width", "height", "file_size_bytes"]:
        plt.figure(figsize=(8, 5))
        for label in classes:
            values = valid.loc[valid["class"] == label, column].dropna()
            plt.hist(values, bins=30, alpha=0.5, label=label)
        plt.xlabel(column)
        plt.ylabel("Image count")
        plt.title(f"{column} distribution by class")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output / f"{column}_histogram.png", dpi=160)
        plt.close()
    print(f"EDA figures saved under {output}")

if __name__ == "__main__":
    main()
