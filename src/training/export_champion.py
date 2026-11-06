import argparse
from pathlib import Path
import mlflow.tensorflow
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', default='VisionGuard')
    parser.add_argument('--output', default='models/champion.keras')
    args = parser.parse_args()
    load_dotenv()
    model = mlflow.tensorflow.load_model(f'models:/{args.model_name}@champion')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    model.save(output)
    print('Champion model exported to', output)

if __name__ == '__main__':
    main()
