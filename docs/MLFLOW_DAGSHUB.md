# MLflow and DagsHub workflow

## Credentials

Connect the DagsHub project to this GitHub repository. Copy its MLflow tracking URI and create an access token. Put these values in the ignored local .env file only:

MLFLOW_TRACKING_URI=YOUR_DAGSHUB_TRACKING_URI
MLFLOW_TRACKING_USERNAME=YOUR_DAGSHUB_USERNAME
MLFLOW_TRACKING_PASSWORD=YOUR_DAGSHUB_TOKEN

The values are account-specific. Never hardcode tokens in Python or commit them.

## Local toy lab

Run the toy model twice with different learning rates:

python -m src.training.mlflow_toy --learning-rate 0.001
python -m src.training.mlflow_toy --learning-rate 0.0001
mlflow ui

Open the local MLflow interface and compare the runs. To send runs to DagsHub, configure the environment variables first.

## VisionGuard runs

Run the custom CNN, MobileNetV2 frozen-head stage, and MobileNetV2 fine-tuning stage. Compare manual callback logging with TensorFlow autologging:

python -m src.training.train --model cnn --logging manual
python -m src.training.train --model cnn --logging autolog
python -m src.training.train --model mobilenet --stage head --logging manual
python -m src.training.train --model mobilenet --stage fine_tune --logging manual
python -m src.training.train --model mobilenet --stage fine_tune --logging autolog
python -m src.training.tune --max-trials 8

Add more controlled runs until there are at least six comparable experiments, changing one meaningful setting at a time. Training runs record hyperparameters, seed, Git commit, DVC version tag, epoch metrics, validation metrics, split lists, environment requirements and a Keras model artifact.

## Register the champion

Choose the model using validation metrics, not test metrics. Register two run artifacts as two model versions:

python -m src.training.register_model --model-name VisionGuard --run-id-v1 RUN_ID_ONE --run-id-v2 RUN_ID_TWO

The helper assigns the champion alias to the newest version. If another version is the one you actually selected, change the alias in the MLflow/DagsHub registry interface. Export the alias locally:

python -m src.training.export_champion --model-name VisionGuard

Set MODEL_FAMILY to cnn or mobilenet as appropriate. Then run the final held-out test evaluation once:

python -m src.training.evaluate

Set MLFLOW_SELECTED_RUN_ID to the selected run ID if final test metrics and evaluation figures should be attached to that run. The decision threshold is selected using validation data only.
