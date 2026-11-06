# VisionGuard — AI-Generated vs Real Image Classifier

> Required project identifier: `<ROLL_NUMBER>_A2_Ops`. Replace the placeholder with your assigned roll number before submission.

VisionGuard predicts whether an uploaded image is **AI-generated** or **real**. The implementation covers dataset auditing/EDA, a custom CNN and MobileNetV2 transfer learning, MLflow tracking on DagsHub, a Flask upload/history UI, database logging, Docker Compose, CI, and a separately deployable inference API.

## Structure
- `src/data/`: image audit, split manifests, EDA and tf.data pipeline.
- `src/models/`: custom CNN and MobileNetV2 builders.
- `src/training/`: model training, evaluation, Keras Tuner and MLflow registry utilities.
- `src/serving/`: one-time model loading and inference preprocessing.
- `web/`: Flask UI, templates, CSS and database trail.
- `api/`: authenticated FastAPI inference endpoint for cloud deployment.
- `Dockerfile`, `Dockerfile.api`, `docker-compose.yml`: containers.
- `.github/workflows/ci.yml`: CI checks and image build.
- `reports/REPORT_TEMPLATE.md`: report structure.

## Dataset setup
Download the Kaggle dataset [AI Generated Images vs Real Images](https://www.kaggle.com/datasets/cashbowman/ai-generated-images-vs-real-images). Extract the two class folders under `data/dataset/`. Class folder names must include `real` for real photos and `ai`, `fake` or `generated` for generated images. Raw data is ignored by Git and must be tracked with DVC.

## Local setup
Python 3.10/3.11 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the DagsHub MLflow URI and credentials. Do not commit `.env`, tokens, Kaggle credentials or cloud secrets.

## Run data and training steps
```bash
python -m src.data.audit --dataset data/dataset
python -m src.data.eda --dataset data/dataset
python -m src.data.split
python -m src.training.train --model cnn
python -m src.training.train --model mobilenet --stage head
python -m src.training.train --model mobilenet --stage fine_tune
python -m src.training.tune --max-trials 8
```

For manual callback logging use the default `--logging manual`; compare with `--logging autolog`. The toy MLflow lab is `python -m src.training.mlflow_toy --learning-rate 0.001`; run it again with a different learning rate. Set `MLFLOW_TRACKING_URI` and DagsHub credentials in environment variables to send runs to DagsHub, or leave the URI blank for local MLflow.

Choose the best model using validation results, copy its file to `models/champion.keras`, and set `MODEL_FAMILY=cnn` or `mobilenet`. Then run `python -m src.training.evaluate` for the held-out test report. Threshold selection is based on validation data, not the test set.

## DVC
Initialize DVC in the Git repository, configure a DagsHub or local remote, add the dataset folder, and push it. See `docs/DVC_SETUP.md` for a safe command sequence. DVC credentials and local config must not be committed.

## Flask and database
The Compose stack runs Flask plus PostgreSQL. PostgreSQL is not published to the host; Flask reaches it by service name.

```bash
# Add POSTGRES_PASSWORD to .env and configure MODEL_API_URL/API_KEY
docker compose up --build
```

Open `http://localhost:5000`. Flask sends image bytes to the separate inference API and stores each successful prediction in PostgreSQL.

## Cloud inference API
Build `Dockerfile.api` and deploy it to a cloud container service. Provide the champion model artifact and configure `MODEL_PATH`, `MODEL_FAMILY`, `MODEL_THRESHOLD`, and `API_KEY` as cloud environment variables. The API exposes `GET /health` and authenticated `POST /predict`. Set the resulting public URL in Flask's `MODEL_API_URL`. A live URL is not claimed until a real deployment is completed and tested externally.

## Tests
```bash
pip install -r requirements-web.txt pytest
pytest -q
```

## Submission evidence
The assignment requires genuine screenshots of environment/GPU versions, audit/EDA, DVC toy and dataset operations, model summaries/curves/evaluation/error analysis, Keras Tuner trials, local and DagsHub MLflow runs/registry, Flask upload/history/validation/health, Docker operations and image sizes, CI red/green runs, cloud deployment, Postman tests, and Flask-to-API integration. These must be captured from your own actual runs; the repository does not invent results or deployment URLs.
