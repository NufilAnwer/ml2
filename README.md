# VisionGuard: AI vs Real Image Classification & Deployment

[![VisionGuard CI Pipeline](https://github.com/NufilAnwer/ml2/actions/workflows/ci.yml/badge.svg)](https://github.com/NufilAnwer/ml2/actions)
[![DagsHub Project](https://img.shields.io/badge/DagsHub-Project-18BFFF?logo=dagshub)](https://dagshub.com/NufilAnwer/ml2)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker)](docker-compose.yml)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?logo=python)](verify_env.py)

---

## 1. Project Overview & Architecture
VisionGuard is an enterprise MLOps web service engineered to classify uploaded imagery as either **AI-Generated** (synthetic diffusion/GAN media) or **Real** (authentic photographic capture). The project establishes a complete end-to-end Machine Learning Operations lifecycle:

1. **Task 1: Data Understanding & Versioning** — Dataset audit, Pillow validation, SHA-256 deduplication, and DVC tracking backed by DagsHub storage.
2. **Task 2: Model Development** — Custom baseline CNN vs. fine-tuned MobileNetV2 with two-stage transfer learning, hyperparameter tuning via Keras Tuner, and threshold calibration for high AI-recall.
3. **Task 3: Experiment Tracking** — MLflow tracking integrated with DagsHub, artifact logging (ROC, Confusion Matrix, splits), and MLflow Model Registry alias `@champion`.
4. **Task 4: Flask Web Application** — Production web UI with singleton model inference, MIME/byte stream validation, responsive drag-and-drop UI, and health diagnostics.
5. **Task 5: Database Trail** — Persistent SQLAlchemy audit logging (SQLite local / PostgreSQL containerized) recording request timestamps, confidence scores, and raw model outputs.
6. **Task 6: Containerization & CI** — Multi-stage non-root Dockerfile (`python:3.10-slim`, `tensorflow-cpu`), Docker Compose stack with isolated network, and GitHub Actions CI workflow.
7. **Task 7: Cloud API Deployment** — Containerized REST API deployed on cloud infrastructure with `/health`, `/predict`, and `/history` endpoints.
8. **Task 8: Client Gateway Integration** — Local Flask server operating seamlessly with the remote Cloud API.

---

## 2. Quickstart

### Prerequisites
- Python 3.10 or 3.11
- Git
- Docker & Docker Compose (optional for local containerization)

### Local Setup
```bash
# 1. Clone repository
git clone https://github.com/NufilAnwer/ml2.git
cd ml2

# 2. Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Run verification script
python verify_env.py

# 6. Run unit tests
python -m unittest tests/test_app.py

# 7. Start the application
python -m app.app
```
Access the application at `http://127.0.0.1:5000`.

---

## 3. Docker Compose Orchestration
Run the entire production stack (Flask web app + PostgreSQL 16) with a single command:
```bash
docker compose up -d --build
```
- **Web App**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/health`
- **Database**: Isolated on `visionguard_net` with persistent named volume `postgres_data`.
