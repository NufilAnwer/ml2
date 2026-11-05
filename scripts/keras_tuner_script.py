"""
Task 2.7 – Keras Tuner
Toy: Fashion-MNIST with random search / Hyperband
Apply: tune learning rate, dropout, unfrozen layers for VisionGuard
"""

import os
import sys
import numpy as np
import tensorflow as tf
import keras_tuner as kt
import mlflow
from dotenv import load_dotenv

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
load_dotenv()


# ─────────────────────────────────────────────────────────────────
# TOY: Fashion-MNIST tuning
# ─────────────────────────────────────────────────────────────────
def toy_fashion_mnist_tuning(output_dir: str = "kt_toy_fashion"):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    def build_toy_model(hp):
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(
                hp.Int("units", min_value=64, max_value=512, step=64),
                activation="relu"
            ),
            tf.keras.layers.Dropout(hp.Float("dropout", 0.2, 0.5, step=0.1)),
            tf.keras.layers.Dense(10, activation="softmax"),
        ])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(
                hp.Choice("lr", [1e-2, 1e-3, 5e-4, 1e-4])
            ),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        return model

    tuner = kt.RandomSearch(
        build_toy_model,
        objective="val_accuracy",
        max_trials=8,
        directory=output_dir,
        project_name="fashion_mnist_toy",
        overwrite=True,
    )

    tuner.search(
        x_train[:5000], y_train[:5000],
        validation_split=0.2,
        epochs=5,
        batch_size=64,
        verbose=1,
    )

    best_hp = tuner.get_best_hyperparameters(num_trials=1)[0]
    print("\n=== Toy Best Hyperparameters ===")
    print(f"  units:   {best_hp.get('units')}")
    print(f"  dropout: {best_hp.get('dropout')}")
    print(f"  lr:      {best_hp.get('lr')}")

    results = tuner.results_summary()
    return best_hp


# ─────────────────────────────────────────────────────────────────
# APPLY: Tune VisionGuard MobileNetV2
# ─────────────────────────────────────────────────────────────────
def visionguard_tuning(train_ds, val_ds, output_dir: str = "kt_visionguard"):
    IMG_SIZE = (224, 224, 3)

    def build_vg_model(hp):
        lr = hp.Choice("learning_rate", [1e-4, 5e-5, 1e-5, 5e-6])
        dropout = hp.Float("dropout", 0.2, 0.6, step=0.1)
        unfreeze = hp.Int("unfreeze_layers", 0, 60, step=15)

        base = tf.keras.applications.MobileNetV2(
            input_shape=IMG_SIZE, include_top=False, weights="imagenet"
        )
        base.trainable = False
        if unfreeze > 0:
            for layer in base.layers[-unfreeze:]:
                if not isinstance(layer, tf.keras.layers.BatchNormalization):
                    layer.trainable = True

        inputs = tf.keras.Input(shape=IMG_SIZE)
        x = tf.keras.layers.Lambda(
            tf.keras.applications.mobilenet_v2.preprocess_input
        )(inputs)
        x = base(x, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(256, activation="relu")(x)
        x = tf.keras.layers.Dropout(dropout)(x)
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

        model = tf.keras.Model(inputs, outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(lr),
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
        )
        return model

    tuner = kt.Hyperband(
        build_vg_model,
        objective=kt.Objective("val_auc", direction="max"),
        max_epochs=10,
        factor=3,
        directory=output_dir,
        project_name="visionguard_tuning",
        overwrite=True,
    )

    stop_early = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3)
    tuner.search(train_ds, validation_data=val_ds, callbacks=[stop_early], verbose=1)

    best_hp = tuner.get_best_hyperparameters(num_trials=1)[0]
    print("\n=== VisionGuard Best Hyperparameters ===")
    for key in ["learning_rate", "dropout", "unfreeze_layers"]:
        print(f"  {key}: {best_hp.get(key)}")

    tuner.results_summary()

    # Log best to MLflow
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("VisionGuard_23L-0501_A2_Ops")
    with mlflow.start_run(run_name="keras_tuner_best"):
        mlflow.log_params({
            "best_lr": best_hp.get("learning_rate"),
            "best_dropout": best_hp.get("dropout"),
            "best_unfreeze_layers": best_hp.get("unfreeze_layers"),
            "tuner": "Hyperband",
            "trials": 8,
        })

    return best_hp


if __name__ == "__main__":
    print("Running TOY Keras Tuner (Fashion-MNIST)...")
    toy_fashion_mnist_tuning()
    print("\nToy tuning done. Run visionguard_tuning() after loading datasets.")

