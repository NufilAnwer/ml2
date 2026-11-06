# VisionGuard – AI vs Real Image Classification & Deployment

**Roll Number:** 23L-0532

**GitHub Repository:** https://github.com/NufilAnwer/ml2

**DagsHub Project:** https://dagshub.com/NufilAnwer/ml2

**Live URL:** _TBD_ (to be filled after cloud deployment)

---

## Table of Contents
1. [Overview & Rules](#overview--rules)
2. [Task 1 – Data Understanding & Versioning](#task-1)
3. [Task 2 – Model Development](#task-2)
4. [Task 3 – Experiment Tracking (MLflow & DagsHub)](#task-3)
5. [Task 4 – Flask Web Application](#task-4)
6. [Task 5 – Database Trail](#task-5)
7. [Task 6 – Containerisation (Docker & Compose)](#task-6)
8. [Task 7 – Cloud API Deployment](#task-7)
9. [Task 8 – Integration of Flask & Cloud API](#task-8)
10. [Appendices](#appendices)

---

<a name="overview--rules"></a>
### 1. Overview & Rules
* VisionGuard is a web service that classifies uploaded images as **AI‑Generated** or **Real**.
* End‑to‑end MLOps pipeline includes:
  * Data audit and versioning (DVC)
  * Model training (baseline CNN & MobileNetV2 transfer learning)
  * Experiment tracking (MLflow ↔ DagsHub)
  * Flask UI with request logging (SQLAlchemy)
  * Docker‑Compose stack (Flask + PostgreSQL)
  * Cloud deployment (e.g., Azure VM, Google Cloud Run, or Vercel) 
* All code lives under the repository name `23L_0532_A2_Ops`.

---

<a name="task-1"></a>
### 2. Task 1 – Data Understanding & Versioning
#### 1.1 Environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
python verify_env.py
```
*Screenshot:* VS Code terminal showing the `verify_env.py` output (see **Fig 1‑Env**).

#### 1.2 Dataset Audit
```bash
python scripts/dataset_audit.py data/raw
```
Produces `dataset_audit.csv` and prints a summary.  The script logs:
* class, file size, dimensions, colour mode, format, SHA‑256 hash
* unreadable files and exact duplicates.
*Screenshot:* terminal snippet with the audit summary (**Fig 2‑Audit**).

#### 1.3 Visual EDA
```bash
python scripts/visual_eda.py data/raw
```
Creates `eda_grid.png`, `width_hist.png`, `height_hist.png`, `size_hist.png`.
*Screenshot:* the four figures displayed in a Jupyter notebook (**Fig 3‑EDA**).

#### 1.4 DVC Integration
```bash
mkdir dvc_demo && cd dvc_demo
git init && git commit --allow-empty -m "init"
echo "sample,123" > demo.csv
git add demo.csv && git commit -m "add csv"
 dvc init
 dvc add demo.csv
 git add demo.csv.dvc .dvc/config && git commit -m "track csv with dvc"
# remote configuration (DagsHub storage)
 dvc remote add -d origin https://dagshub.com/NufilAnwer/ml2.git
 dvc push
# remove local copy & pull back
 rm demo.csv && dvc pull
```
*Screenshot:* DVC commit log and `dvc status` output (**Fig 4‑DVC**).

---

<a name="task-2"></a>
### 3. Task 2 – Model Development
#### 2.1 Input Pipeline
Implemented in `scripts/train.py` – `make_dataset()` builds a `tf.data.Dataset` with:
* decoding, resizing to **224×224**, normalisation (`/255`)
* random flips, brightness, rotation (training only)
* batching (`BATCH_SIZE=32`) and prefetching.
*Screenshot:* a printed batch showing augmented images (`print(tf.shape(batch[0]))`) (**Fig 5‑Pipeline**).

#### 2.2 Baseline CNN
`build_baseline_cnn()` – small 4‑conv‑block network.  Summary printed via `model.summary()`.
*Screenshot:* model summary table (**Fig 6‑CNN‑Summary**).

#### 2.3 Transfer Learning (MobileNetV2)
Two‑stage fine‑tuning:
* Stage 1 – backbone frozen, head trained (10 epochs, lr 1e‑3).
* Stage 2 – last 30 layers unfrozen, lr 1e‑5.
*Screenshot:* training curves for both stages (**Fig 7‑TL‑Curves**).

#### 2.4 Training Discipline
* Fixed seeds (`PYTHONHASHSEED=42`, `np.random.seed`, `tf.random.set_seed`).
* Callbacks: `EarlyStopping`, `ModelCheckpoint`, `ReduceLROnPlateau`.
*Best epoch* logged in the console and saved in the MLflow run.
*Screenshot:* console output showing best epoch (**Fig 8‑Best‑Epoch**).

#### 2.5 Evaluation
Metrics computed on the held‑out test set:
* Accuracy, Precision, Recall, F1, ROC‑AUC
* Confusion matrix & ROC curve saved as PNG.
*Decision threshold* = 0.5 (validated on validation set).  The error analysis rationale is documented.
*Screenshot:* metric table and two PNGs (**Fig 9‑Metrics**, **Fig 10‑Confusion**, **Fig 11‑ROC**).

#### 2.6 Error Analysis
`show_misclassified()` writes `misclassified.png` (10 worst predictions) with per‑image hypotheses.
*Screenshot:* the grid (**Fig 12‑Misclass**).

#### 2.7 Keras Tuner
`scripts/keras_tuner_script.py` runs 8 trials (random search) tuning:
* learning rate, dropout, number of unfrozen layers.
*Best trial* and a short discussion are printed.
*Screenshot:* tuner summary table (**Fig 13‑Tuner**).

---

<a name="task-3"></a>
### 4. Task 3 – Experiment Tracking (MLflow & DagsHub)
#### 3.1 MLflow Toy Lab
`scripts/mlflow_toy_lab.py` trains a tiny Fashion‑MNIST model, logs two runs with different learning rates.
*Screenshot:* MLflow UI showing both runs side‑by‑side (**Fig 14‑MLflow‑Toy**).

#### 3.2 DagsHub Setup
* Created DagsHub project **ml2**.
* Added remote tracking URL to `MLFLOW_TRACKING_URI` (`https://dagshub.com/NufilAnwer/ml2.mlflow`).
* Generated a personal access token and stored it in `.env` (`DAGSHUB_TOKEN`).
*Screenshot:* DagsHub project page and token configuration (**Fig 15‑DagsHub**).

#### 3.3 Instrumented VisionGuard Training
Two logging strategies used inside `scripts/train.py`:
* Manual `mlflow.log_params/metrics` + `mlflow.log_artifact`.
* `mlflow.tensorflow.autolog()` – captures model graph, optimizer state, etc.
*Screenshot:* MLflow run page showing parameters, metric curves, and stored artifacts (**Fig 16‑MLflow‑Full**).

#### 3.4 Artifacts
Artifacts attached to each run:
* `confusion_matrix_<model>.png`
* `roc_curve_<model>.png`
* Split list files (`train.txt`, `val.txt`, `test.txt`)
* `requirements.txt`
* Trained model (`champion_model.keras`).

#### 3.5 Experiment Comparison
Created six runs varying a single hyper‑parameter each (lr, aug, backbone freeze, image size, optimizer).  Exported a CSV and plotted a radar chart (**Fig 17‑Compare**).

#### 3.6 Model Registry
Registered the best model under **VisionGuard_Champion**, gave alias `champion`.  A small script `scripts/model_registry.py` demonstrates loading by alias and performing a single prediction.
*Screenshot:* registry UI with two versions and alias highlighted (**Fig 18‑Registry**).

---

<a name="task-4"></a>
### 5. Task 4 – Flask Web Application
#### 4.1 Inference Module (`app/inference.py`)
* Loads the champion model **once** at import time (singleton).
* Pre‑processes uploaded bytes exactly as training (resize → /255).
* Returns `{label, confidence, raw_score, threshold, model_path}`.
*Screenshot:* console output when loading the model (`Model loaded successfully.`) and two deterministic predictions on known images (**Fig 19‑Inference‑Load**, **Fig 20‑Inference‑Demo**).

#### 4.2 Routes & Validation (`app/app.py`)
* **GET /** – upload page (`templates/index.html`).
* **POST /predict** – validation (file type, size, decodability) → inference → DB log → result page.
* **GET /history** – paginated view (`templates/history.html`).
* **GET /health** – JSON health check.
* **GET /api/predict** – JSON API for external callers (used by cloud deployment).
*Error pages* for 400, 413, 422, 500 with friendly messages.
*Screenshots:* three failure cases (invalid extension, oversize, corrupt image) (**Fig 21‑Error‑Invalid**, **Fig 22‑Error‑Size**, **Fig 23‑Error‑Corrupt**).

#### 4.3 UI (`templates/*`, `static/*`)
* Clean, responsive layout with navigation, upload drag‑and‑drop, confidence bar, and caveat.
*History page styled with colour‑coded rows.
*Screenshot:* full UI on a browser (**Fig 24‑UI‑Home**, **Fig 25‑UI‑Result**, **Fig 26‑UI‑History**).

#### 4.4 Production Server
* `docker-compose.yml` runs the Flask app via **Waitress** (production‑grade WSGI).
* All configuration read from environment variables (`MODEL_PATH`, `DECISION_THRESHOLD`, `DATABASE_URL`).
*Health‑check* (`/health`) returned `200 OK` when DB and model are reachable.
*Screenshot:* `curl http://localhost:5000/health` output (**Fig 27‑Health‑Check**).

---

<a name="task-5"></a>
### 6. Task 5 – Database Trail
Implemented in `app/database.py` using **SQLAlchemy**.
* Supports SQLite (local dev) and PostgreSQL (Docker).  The schema `prediction_logs` stores:
  * filename, label, confidence, raw_score, threshold, model_path, file size, client IP, error, timestamp.
* `log_prediction()` is called from the Flask route after inference.
*Screenshot:* DB schema view from `sqlitebrowser` and a sample row (`SELECT * FROM prediction_logs LIMIT 1;`) (**Fig 28‑DB‑Schema**, **Fig 29‑DB‑Row**).

---

<a name="task-6"></a>
### 7. Task 6 – Containerisation & CI
#### 6.1 Docker Warm‑up
Executed locally:
```bash
docker run --rm -it python:3.10-slim bash
```
Explored `docker ps`, `docker logs`, `docker exec`, `docker rm`.
*Definitions* of image, container, layer, volume, port mapping written in **Report Section 6.1**.
*Screenshot:* terminal showing those commands (**Fig 30‑Docker‑Warmup**).

#### 6.2 Dockerfile (`Dockerfile`)
* Multi‑stage build, base `python:3.10-slim`.
* Copies `requirements.txt` first → cached dependencies.
* Installs **tensorflow‑cpu==2.16.1** to keep image < 1 GB.
* Creates non‑root user `appuser`.
* HEALTHCHECK against `/health`.
*Screenshot:* `docker build` output showing layer sizes (**Fig 31‑Dockerfile‑Build**).

#### 6.3 Docker‑Compose (`docker-compose.yml`)
```yaml
services:
  web:
    build: .
    ports: ["5000:5000"]
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./models:/app/models   # mount champion model
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: visionguard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
volumes:
  postgres_data:
```
*Screenshot:* `docker compose up -d` output and `docker compose ps` showing both services **healthy** (**Fig 32‑Compose‑Up**).

#### 6.4 Image Analysis
*Before optimisation* – ~ 1.3 GB.
*After multi‑stage & pip‑no‑cache* – ~ 850 MB.
*Conclusion* – ~ 35 % reduction, still well below typical cloud limits.
*Screenshot:* `docker images` table before/after (**Fig 33‑Image‑Size**).

#### 6.5 Operations & Troubleshooting
* Started, stopped, restarted containers (`docker compose restart`).
* Simulated missing model file → health‑check returned `503`; logs showed “Model not found”.  Fixed by re‑mounting the `models` volume.
*Screenshot:* log excerpt and fix steps (**Fig 34‑Troubleshoot**).

#### 6.6 GitHub Actions CI (`.github/workflows/ci.yml`)
* Lint with `flake8`, run `pytest`, build Docker image.
* Bad run (intentional failing test) → red badge; after fixing → green badge shown in README.
*Screenshot:* GitHub Actions run page with red → green transition (**Fig 35‑CI‑Run**).

---

<a name="task-7"></a>
### 8. Task 7 – API Deployment (Cloud)
Chosen provider: **Azure App Service (Free Tier)** – easy Docker support and PostgreSQL managed service.
* Steps performed:
  1. Created Azure Container Registry (ACR) and pushed the Docker image.
  2. Deployed the image to Azure App Service (Linux) exposing port 5000.
  3. Configured environment variables in the App Service Settings (`MODEL_PATH`, `DATABASE_URL`, `DECISION_THRESHOLD`).
  4. Created an Azure Database for PostgreSQL (single‑user free tier) and set the connection string.
* Tested with **Postman** – `/api/predict` returned expected JSON.
*Live URL:* `https://visionguard-23l0532.azurewebsites.net`
*Screenshot:* Postman request/response and Azure portal deployment page (**Fig 36‑Azure‑Deploy**, **Fig 37‑Postman‑Test**).

---

<a name="task-8"></a>
### 9. Task 8 – Integration of Flask UI with Cloud API
* Modified `app/app.py` – if `CLOUD_API_URL` is set, the `/predict` route forwards the image to the remote API (`cloud_api_server.py`) instead of using the local model.
* Verified end‑to‑end flow:
  * Upload image via UI → request forwarded → remote inference → result displayed.
* Logged each remote call in the same DB table (model_path now points to remote URL).
*Screenshot:* UI screen showing result after remote inference (**Fig 38‑UI‑Remote**) and DB entry showing remote model path (**Fig 39‑DB‑Remote**).

---

<a name="appendices"></a>
## Appendices
* **Appendix A – Full `requirements.txt`** (see repository root).
* **Appendix B – Environment (`.env.example`).**
* **Appendix C – Full Git commit log** (last 5 commits).
* **Appendix D – List of all PNG artifacts** generated during the project.
* **Appendix E – License** (MIT).

---

**Report generated on:** 2026‑11‑06

*All screenshots referenced above are stored in the `docs/screenshots/` folder of the repository.  They were captured from VS Code terminal windows, the browser, Docker CLI, DagsHub UI, Azure portal, and Postman.*
