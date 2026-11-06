"""Create reproducible stratified train/validation/test CSV split manifests."""
import pandas as pd
from sklearn.model_selection import train_test_split
from src.data.common import load_config, resolve_path, label_from_path, set_seed

def create_splits():
    config = load_config()
    set_seed(config["project"]["seed"])
    root = resolve_path(config["data"]["root"])
    extensions = set(config["data"]["extensions"])
    paths = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
    records = [{"path": str(p.resolve()), "label": label_from_path(p)} for p in paths]
    if not records:
        raise FileNotFoundError(f"No supported images found under {root}. Place the Kaggle class folders there.")
    frame = pd.DataFrame(records).drop_duplicates("path")
    train_fraction = 1 - config["data"]["validation_fraction"] - config["data"]["test_fraction"]
    if train_fraction <= 0:
        raise ValueError("Validation and test fractions must sum to less than 1.")
    train, temp = train_test_split(frame, test_size=1-train_fraction, random_state=config["project"]["seed"], stratify=frame["label"])
    relative_test = config["data"]["test_fraction"] / (config["data"]["validation_fraction"] + config["data"]["test_fraction"])
    validation, test = train_test_split(temp, test_size=relative_test, random_state=config["project"]["seed"], stratify=temp["label"])
    out = resolve_path(config["data"]["splits_dir"])
    out.mkdir(parents=True, exist_ok=True)
    for name, subset in [("train", train), ("validation", validation), ("test", test)]:
        subset.to_csv(out / f"{name}.csv", index=False)
        print(f"{name}: {len(subset)} images | {subset['label'].value_counts().to_dict()}")
    print(f"Split manifests saved to {out}")

if __name__ == "__main__":
    create_splits()
