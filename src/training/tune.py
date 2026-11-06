"""Keras Tuner search for learning rate, dropout and MobileNet unfrozen depth."""
import argparse
import keras_tuner as kt
import tensorflow as tf
from src.data.common import load_config, set_seed
from src.data.pipeline import make_dataset
from src.models.builders import build_mobilenet

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-trials", type=int, default=8)
    args = parser.parse_args()
    cfg = load_config()
    set_seed(cfg["project"]["seed"])
    train_ds = make_dataset("train", training=True, model_name="mobilenet")
    val_ds = make_dataset("validation", model_name="mobilenet")
    shape = (*cfg["data"]["image_size"], 3)
    def model_builder(hp):
        learning_rate = hp.Choice("learning_rate", [1e-3, 3e-4, 1e-4, 3e-5])
        dropout = hp.Float("dropout", 0.2, 0.6, step=0.1)
        unfrozen = hp.Choice("unfrozen_layers", [0, 10, 20, 30])
        model = build_mobilenet(shape, train_base=unfrozen > 0, unfreeze_last_layers=max(1, unfrozen))
        model.layers[-2].rate = dropout
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate),
                      loss="binary_crossentropy", metrics=["accuracy", tf.keras.metrics.AUC(name="auc")])
        return model
    tuner = kt.RandomSearch(model_builder, objective="val_auc", max_trials=max(8, args.max_trials),
                            directory="tuner_results", project_name="visionguard")
    tuner.search(train_ds, validation_data=val_ds, epochs=4,
                 callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=2)])
    print("Best hyperparameters:")
    for hp in tuner.get_best_hyperparameters(1):
        print(hp.values)
    tuner.results_summary()

if __name__ == "__main__":
    main()
