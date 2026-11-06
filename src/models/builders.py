"""Keras model definitions: custom CNN and MobileNetV2 transfer learning."""
import tensorflow as tf
from src.data.common import load_config

def build_cnn(input_shape):
    cfg = load_config()["models"]["cnn"]
    inputs = tf.keras.Input(shape=input_shape, name="image")
    x = inputs
    for index, filters in enumerate(cfg["filters"]):
        x = tf.keras.layers.Conv2D(filters, 3, padding="same", activation="relu", name=f"conv_{index+1}")(x)
        x = tf.keras.layers.BatchNormalization(name=f"bn_{index+1}")(x)
        x = tf.keras.layers.MaxPooling2D(name=f"pool_{index+1}")(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(cfg["dense_units"], activation="relu")(x)
    x = tf.keras.layers.Dropout(load_config()["training"]["dropout"])(x)
    output = tf.keras.layers.Dense(1, activation="sigmoid", name="real_vs_ai")(x)
    return tf.keras.Model(inputs, output, name="visionguard_custom_cnn")

def build_mobilenet(input_shape, train_base=False, unfreeze_last_layers=20):
    base = tf.keras.applications.MobileNetV2(include_top=False, weights="imagenet", input_shape=input_shape)
    base.trainable = train_base
    if train_base:
        for layer in base.layers[:-unfreeze_last_layers]:
            layer.trainable = False
        for layer in base.layers:
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False
    inputs = tf.keras.Input(shape=input_shape, name="image")
    x = base(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(load_config()["training"]["dropout"])(x)
    output = tf.keras.layers.Dense(1, activation="sigmoid", name="real_vs_ai")(x)
    return tf.keras.Model(inputs, output, name="visionguard_mobilenetv2")
