"""Small local/DagsHub MLflow lab using built-in Fashion-MNIST."""
import argparse
import os
import mlflow
import mlflow.tensorflow
import tensorflow as tf
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--autolog", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if uri:
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("VisionGuard-MLflow-Toy")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
    x_train = x_train[:12000].astype("float32") / 255.0
    y_train = y_train[:12000]
    x_test = x_test[:2000].astype("float32") / 255.0
    y_test = y_test[:2000]
    model = tf.keras.Sequential([tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(64, activation="relu"), tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation="softmax")])
    model.compile(optimizer=tf.keras.optimizers.Adam(args.learning_rate),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    with mlflow.start_run(run_name=f"fashion_mnist_lr_{args.learning_rate}") as run:
        mlflow.log_param("learning_rate", args.learning_rate)
        mlflow.log_param("dataset", "Fashion-MNIST sample")
        if args.autolog:
            mlflow.tensorflow.autolog(log_models=True)
        history = model.fit(x_train, y_train, validation_split=0.2, epochs=2, batch_size=64, verbose=1)
        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        mlflow.log_metric("test_loss", float(loss))
        mlflow.log_metric("test_accuracy", float(accuracy))
        mlflow.log_metric("final_train_accuracy", float(history.history["accuracy"][-1]))
        mlflow.log_metric("final_val_accuracy", float(history.history["val_accuracy"][-1]))
        mlflow.log_dict({"test_loss": float(loss), "test_accuracy": float(accuracy)}, "toy_metrics.json")
        print("MLflow run:", run.info.run_id, "test accuracy:", accuracy)

if __name__ == "__main__":
    main()
