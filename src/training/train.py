"""Train CNN or MobileNetV2; logs manual callback metrics and MLflow artifacts."""
import argparse
import os
import subprocess
from pathlib import Path
import mlflow
import mlflow.tensorflow
import tensorflow as tf
from dotenv import load_dotenv
from src.data.common import load_config, resolve_path, set_seed
from src.data.pipeline import make_dataset
from src.models.builders import build_cnn, build_mobilenet

class MLflowEpochLogger(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        for key, value in (logs or {}).items():
            mlflow.log_metric(f"epoch_{key}", float(value), step=epoch)

def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def setup_mlflow():
    load_dotenv()
    uri = os.getenv("MLFLOW_TRACKING_URI", "").strip()
    if uri:
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("VisionGuard")
    return bool(uri)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["cnn", "mobilenet"], required=True)
    parser.add_argument("--stage", choices=["head", "fine_tune"], default="head")
    parser.add_argument("--logging", choices=["manual", "autolog"], default="manual")
    args = parser.parse_args()
    cfg = load_config()
    seed = int(cfg["project"]["seed"])
    set_seed(seed)
    size = tuple(cfg["data"]["image_size"])
    input_shape = (*size, 3)
    train_ds = make_dataset("train", training=True, model_name=args.model)
    val_ds = make_dataset("validation", model_name=args.model)
    learning_rate = cfg["training"]["learning_rate"]
    if args.model == "mobilenet" and args.stage == "fine_tune":
        learning_rate = cfg["training"]["fine_tune_learning_rate"]
        model = build_mobilenet(input_shape, train_base=True,
                                unfreeze_last_layers=cfg["training"]["unfreeze_last_layers"])
    elif args.model == "mobilenet":
        model = build_mobilenet(input_shape, train_base=False)
    else:
        model = build_cnn(input_shape)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                  loss="binary_crossentropy",
                  metrics=["accuracy", tf.keras.metrics.Precision(name="precision"),
                           tf.keras.metrics.Recall(name="recall"), tf.keras.metrics.AUC(name="auc")])
    model.summary()
    output_dir = resolve_path("models/checkpoints")
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / f"{args.model}_{args.stage}.keras"
    setup_mlflow()
    mlflow.tensorflow.autolog(log_models=False, log_datasets=False) if args.logging == "autolog" else None
    params = {"model": args.model, "stage": args.stage, "learning_rate": learning_rate,
              "image_size": str(size), "batch_size": cfg["data"]["batch_size"],
              "epochs": cfg["training"]["epochs"], "dropout": cfg["training"]["dropout"],
              "seed": seed, "augmentation": True, "unfrozen_layers": cfg["training"]["unfreeze_last_layers"] if args.stage == "fine_tune" else 0}
    with mlflow.start_run(run_name=f"{args.model}_{args.stage}_{args.logging}") as run:
        mlflow.log_params(params)
        mlflow.set_tags({"git_commit": git_commit(), "dvc_data_version": os.getenv("DVC_DATA_VERSION", "not-set"),
                         "seed": str(seed), "logging_mode": args.logging})
        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=cfg["training"]["patience"], restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(str(checkpoint), monitor="val_loss", save_best_only=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=1e-7),
        ]
        if args.logging == "manual":
            callbacks.append(MLflowEpochLogger())
        history = model.fit(train_ds, validation_data=val_ds, epochs=cfg["training"]["epochs"], callbacks=callbacks)
        best_epoch = int(min(range(len(history.history["val_loss"])), key=lambda i: history.history["val_loss"][i]) + 1)
        model = tf.keras.models.load_model(checkpoint) if checkpoint.exists() else model
        validation_metrics = model.evaluate(val_ds, return_dict=True, verbose=1)
        mlflow.log_metrics({f"final_validation_{key}": float(value) for key, value in validation_metrics.items()})
        mlflow.log_param("best_epoch", best_epoch)
        Path("models").mkdir(exist_ok=True)
        final_path = resolve_path(f"models/{args.model}_{args.stage}.keras")
        model.save(final_path)
        mlflow.tensorflow.log_model(model, artifact_path="model_files")
        mlflow.log_artifact(str(final_path), artifact_path="model_files")
        mlflow.log_artifact(str(resolve_path("data/splits/train.csv")), artifact_path="split_lists")
        mlflow.log_artifact(str(resolve_path("data/splits/validation.csv")), artifact_path="split_lists")
        mlflow.log_artifact(str(resolve_path("data/splits/test.csv")), artifact_path="split_lists")
        mlflow.log_artifact("requirements.txt", artifact_path="environment")
        mlflow.log_metric("best_epoch", best_epoch)
        print("Run ID:", run.info.run_id)
        print("Best epoch:", best_epoch)
        print("Final validation metrics:", validation_metrics)
        print("Saved:", final_path)

if __name__ == "__main__":
    main()
