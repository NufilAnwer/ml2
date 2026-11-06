"""Load the registered champion alias and classify one image."""
import argparse
import mlflow.pyfunc
from PIL import Image
import numpy as np
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--model-name", default="VisionGuard")
    args = parser.parse_args()
    load_dotenv()
    model = mlflow.pyfunc.load_model(f"models:/{args.model_name}@champion")
    with Image.open(args.image) as image:
        array = np.asarray(image.convert("RGB").resize((224, 224)), dtype=np.float32) / 255.0
    prediction = model.predict(np.expand_dims(array, axis=0))
    print("Raw model output:", prediction)

if __name__ == "__main__":
    main()
