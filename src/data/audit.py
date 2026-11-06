"""Audit image files: dimensions, format, mode, bytes, SHA-256 and corrupt files."""
import argparse
import hashlib
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import pandas as pd
from src.data.common import load_config, resolve_path

def audit_dataset(dataset):
    rows = []
    for path in sorted(Path(dataset).rglob("*")):
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                mode, fmt = image.mode, image.format
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            label = path.parent.name
            rows.append({"path": str(path), "class": label, "file_size_bytes": path.stat().st_size,
                         "width": width, "height": height, "colour_mode": mode,
                         "format": fmt, "sha256": digest, "readable": True})
        except (UnidentifiedImageError, OSError, ValueError) as error:
            rows.append({"path": str(path), "class": path.parent.name, "file_size_bytes": path.stat().st_size,
                         "width": None, "height": None, "colour_mode": None,
                         "format": None, "sha256": None, "readable": False, "error": str(error)})
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None)
    args = parser.parse_args()
    config = load_config()
    dataset = args.dataset or config["data"]["root"]
    output = resolve_path("data/audit")
    output.mkdir(parents=True, exist_ok=True)
    frame = audit_dataset(resolve_path(dataset))
    frame.to_csv(output / "image_audit.csv", index=False)
    valid = frame[frame["readable"] == True]
    print("Class counts:\n", valid["class"].value_counts(dropna=False))
    for column in ["width", "height", "file_size_bytes"]:
        print(f"\n{column} min/median/max:\n", valid[column].agg(["min", "median", "max"]))
    print("\nUnreadable files:", int((~frame["readable"]).sum()))
    print("Exact duplicate files:", int(valid.duplicated("sha256").sum()))
    print("Audit saved to data/audit/image_audit.csv")

if __name__ == "__main__":
    main()
