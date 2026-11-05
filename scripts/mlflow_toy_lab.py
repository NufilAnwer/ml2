"""
Task 3.1 – MLflow Local Toy Lab
Trains a tiny Keras model on Fashion-MNIST, logs two runs with
different learning rates, then compares them in MLflow UI.

Usage:
  python scripts/mlflow_toy_lab.py
  mlflow ui   # then open http://127.0.0.1:5000
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tensorflow as tf
import mlflow
import mlflow.tensorflow

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ─── MLflow Terminology ───────────────────────────────────────────────────────
# experiment: a named group of related runs (e.g., "FashionMNIST_toy")
# run:        one execution inside an experiment; records params+metrics+artifacts
# parameter:  an input setting you choose before training (lr, batch_size)
# metric:     a measured number during/after training (val_accuracy, loss)
# artifact:   any file saved to a run (plot, model, CSV)
# tag:        free-form string key-value metadata (git commit, data version)
# ─────────────────────────────────────────────────────────────────────────────

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("FashionMNIST_toy_23L-0501")


def build_model(lr: float, units: int = 128) -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(units, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


class MLflowCallback(tf.keras.callbacks.Callback):
    """Manual per-epoch metric logging to MLflow."""
    def on_epoch_end(self, epoch, logs=None):
        for key, val in (logs or {}).items():
            mlflow.log_metric(key, val, step=epoch)


def run_experiment(lr: float, units: int = 128, epochs: int = 10):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    with mlflow.start_run(run_name=f"lr_{lr}_units_{units}") as run:
        # Tag the run
        mlflow.set_tags({
            "dataset": "fashion_mnist",
            "framework": "keras",
            "purpose": "toy_lab_3.1",
        })

        # Log params
        mlflow.log_params({
            "learning_rate": lr,
            "units": units,
            "epochs": epochs,
            "optimizer": "adam",
            "dropout": 0.3,
        })

        model = build_model(lr, units)
        history = model.fit(
            x_train, y_train,
            validation_split=0.15,
            epochs=epochs,
            batch_size=64,
            callbacks=[MLflowCallback()],
            verbose=1,
        )

        # Final test metrics
        test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
        mlflow.log_metric("test_accuracy", test_acc)
        mlflow.log_metric("test_loss", test_loss)

        # Save and log a plot artifact
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, metric in zip(axes, ["accuracy", "loss"]):
            ax.plot(history.history[metric], label="train")
            ax.plot(history.history[f"val_{metric}"], label="val")
            ax.set_title(f"{metric} (lr={lr})")
            ax.legend()
        plot_path = f"training_curves_lr{lr}.png"
        fig.savefig(plot_path, bbox_inches="tight")
        plt.close(fig)
        mlflow.log_artifact(plot_path)

        # Log model
        mlflow.tensorflow.log_model(model, "toy_model")

        print(f"Run {run.info.run_id}: test_acc={test_acc:.4f}, test_loss={test_loss:.4f}")
        return run.info.run_id


if __name__ == "__main__":
    print("=== MLflow Toy Lab: Run 1 (lr=0.001) ===")
    run_experiment(lr=0.001, units=128, epochs=10)

    print("\n=== MLflow Toy Lab: Run 2 (lr=0.0001) ===")
    run_experiment(lr=0.0001, units=256, epochs=10)

    print(f"\nOpen MLflow UI: mlflow ui --backend-store-uri {MLFLOW_URI}")
    print("Compare runs at http://127.0.0.1:5000")

