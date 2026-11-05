"""
Task 1.2 – Dataset Audit Script
Walks dataset directory, records class, file size, dimensions,
colour mode, format, SHA-256 hash. Detects corrupt files and duplicates.
"""

import os
import hashlib
import csv
import sys
from pathlib import Path
from collections import defaultdict
import statistics

from PIL import Image, UnidentifiedImageError


def sha256_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_dataset(dataset_root: str, output_csv: str = "dataset_audit.csv") -> dict:
    """
    Walk dataset_root (expects sub-folders = class names).
    Returns summary dict and writes per-image CSV.
    """
    dataset_path = Path(dataset_root)
    if not dataset_path.exists():
        print(f"[ERROR] Dataset path not found: {dataset_root}")
        sys.exit(1)

    rows = []
    hashes = defaultdict(list)   # hash -> list of paths (duplicates)
    corrupt = []
    class_stats = defaultdict(lambda: {"count": 0, "widths": [], "heights": [], "sizes": []})

    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

    for class_dir in sorted(dataset_path.iterdir()):
        if not class_dir.is_dir():
            continue
        class_name = class_dir.name

        for img_path in sorted(class_dir.rglob("*")):
            if img_path.suffix.lower() not in image_exts:
                continue

            file_size = img_path.stat().st_size
            content_hash = sha256_hash(str(img_path))
            hashes[content_hash].append(str(img_path))

            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                    mode = img.mode
                    fmt = img.format or img_path.suffix.lstrip(".")
                    readable = True
            except UnidentifiedImageError:
                width = height = 0
                mode = fmt = "UNREADABLE"
                readable = False
                corrupt.append(str(img_path))
            except Exception as e:
                width = height = 0
                mode = "ERROR"
                fmt = str(e)[:50]
                readable = False
                corrupt.append(str(img_path))

            row = {
                "class": class_name,
                "filename": img_path.name,
                "filepath": str(img_path),
                "file_size_bytes": file_size,
                "width": width,
                "height": height,
                "color_mode": mode,
                "format": fmt,
                "sha256": content_hash,
                "readable": readable,
            }
            rows.append(row)

            if readable:
                cs = class_stats[class_name]
                cs["count"] += 1
                cs["widths"].append(width)
                cs["heights"].append(height)
                cs["sizes"].append(file_size)

    # Write CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    # Duplicates = hashes pointing to > 1 file
    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}

    # Print summary
    print("\n" + "=" * 60)
    print("DATASET AUDIT SUMMARY")
    print("=" * 60)
    for cls, stats in class_stats.items():
        w, h, s = stats["widths"], stats["heights"], stats["sizes"]
        print(f"\nClass: {cls}  |  Count: {stats['count']}")
        if w:
            print(f"  Width  — min:{min(w)}  median:{statistics.median(w):.0f}  max:{max(w)}")
            print(f"  Height — min:{min(h)}  median:{statistics.median(h):.0f}  max:{max(h)}")
            print(f"  Size(B)— min:{min(s)}  median:{statistics.median(s):.0f}  max:{max(s)}")

    print(f"\nCorrupt / unreadable files : {len(corrupt)}")
    if corrupt:
        for c in corrupt[:10]:
            print(f"  {c}")

    print(f"\nExact duplicates (hash groups): {len(duplicates)}")
    total_dup_files = sum(len(v) for v in duplicates.values())
    print(f"Total files involved in duplicates: {total_dup_files}")

    print(f"\nFull audit saved to: {output_csv}")
    print("=" * 60)

    return {
        "class_stats": class_stats,
        "corrupt": corrupt,
        "duplicates": duplicates,
        "total_images": len(rows),
    }


if __name__ == "__main__":
    # Adjust this path to where your dataset lives
    DATASET_ROOT = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    audit_dataset(DATASET_ROOT, output_csv="dataset_audit.csv")

