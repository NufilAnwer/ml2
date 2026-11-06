"""tf.data input pipeline shared by CNN and transfer-learning experiments."""
import pandas as pd
import tensorflow as tf
from src.data.common import load_config, resolve_path

AUTOTUNE = tf.data.AUTOTUNE

def decode_image(path, label, image_size, training=False, preprocess=None):
    raw = tf.io.read_file(path)
    image = tf.io.decode_image(raw, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, image_size)
    image = tf.cast(image, tf.float32)
    if preprocess is not None:
        image = preprocess(image)
    else:
        image = image / 255.0
    if training:
        image = tf.image.random_flip_left_right(image)
        image = tf.image.random_brightness(image, max_delta=0.08)
        image = tf.image.random_contrast(image, lower=0.9, upper=1.1)
    return image, tf.cast(label, tf.float32)

def make_dataset(split, training=False, model_name="cnn"):
    config = load_config()
    manifest = resolve_path(config["data"]["splits_dir"]) / f"{split}.csv"
    frame = pd.read_csv(manifest)
    size = tuple(config["data"]["image_size"])
    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input if model_name == "mobilenet" else None
    paths = frame["path"].astype(str).values
    labels = frame["label"].map({"real": 0, "ai_generated": 1}).astype("float32").values
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        dataset = dataset.shuffle(len(frame), seed=config["project"]["seed"], reshuffle_each_iteration=True)
    dataset = dataset.map(lambda p, y: decode_image(p, y, size, training, preprocess),
                          num_parallel_calls=AUTOTUNE)
    return dataset.batch(config["data"]["batch_size"]).prefetch(AUTOTUNE)
