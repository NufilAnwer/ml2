"""
Generate a lightweight champion MobileNetV2 model stub for VisionGuard
so the web application, tests, and Docker container can execute end-to-end immediately.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf

def build_and_save_champion():
    print("Building lightweight MobileNet champion model stub...")
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_tensor")
    
    # Built-in Rescaling layer matching MobileNet [-1, 1] preprocessing
    x = tf.keras.layers.Rescaling(
        scale=1.0 / 127.5,
        offset=-1.0,
        name="mobilenet_preprocess"
    )(inputs)
    
    # Depthwise Separable Convolution blocks (MobileNet architecture)
    x = tf.keras.layers.Conv2D(32, kernel_size=3, strides=2, padding="same", activation="relu", name="conv1")(x)
    x = tf.keras.layers.BatchNormalization(name="bn1")(x)
    x = tf.keras.layers.DepthwiseConv2D(kernel_size=3, padding="same", activation="relu", name="dw_conv1")(x)
    x = tf.keras.layers.Conv2D(64, kernel_size=1, activation="relu", name="pw_conv1")(x)
    x = tf.keras.layers.BatchNormalization(name="bn2")(x)
    
    x = tf.keras.layers.DepthwiseConv2D(kernel_size=3, strides=2, padding="same", activation="relu", name="dw_conv2")(x)
    x = tf.keras.layers.Conv2D(128, kernel_size=1, activation="relu", name="pw_conv2")(x)
    x = tf.keras.layers.BatchNormalization(name="bn3")(x)
    
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = tf.keras.layers.Dense(64, activation="relu", name="dense_head")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout_head")(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="output_classification")(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="VisionGuard_MobileNetV2_Champion")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    
    os.makedirs("models", exist_ok=True)
    out_path = "models/champion_model.keras"
    model.save(out_path)
    print(f"Model saved successfully to {out_path}")
    model.summary()

if __name__ == "__main__":
    build_and_save_champion()
