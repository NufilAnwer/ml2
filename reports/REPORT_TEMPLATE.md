# <ROLL_NUMBER>_VisionGuard — Assignment Report

Replace every bracketed placeholder. Include genuine screenshots from your machine and actual service dashboards. Do not report a metric, URL, screenshot or deployment that you have not produced.

## Front matter
- Student name: [Your name]
- Roll number: [Your roll number]
- Project identifier: [ROLL_NUMBER_A2_Ops]
- GitHub: https://github.com/NufilAnwer/ml2
- DagsHub: [Your DagsHub project URL]
- Live API URL: [Your deployed API URL]
- Graded commit: [Git commit SHA]
- AI/tutorial disclosure: [Describe tools used and what they helped with]

## Task 1 — Data understanding and versioning
### 1.1 Environment
[Python, TensorFlow, package versions; GPU availability screenshot.]

### 1.2 Dataset audit
[Per-class counts; width, height and byte-size min/median/max; corrupt images; SHA-256 exact duplicates. Insert audit table and terminal screenshot.]

### 1.3 Visual EDA
[Sample grid and three histograms. Add a 2–3 sentence interpretation and caption for each.]

### 1.4 DVC
[Show toy CSV v1/v2 commits, checkout of older version, remote push, local deletion and pull. Then show dataset DVC tracking and explain pointer files.]

## Task 2 — Model development
### 2.1 tf.data input pipeline
[Explain split manifests, decode, RGB conversion, resize, aspect-ratio handling, normalization/preprocessing, train-only augmentation, batching and prefetch. Insert augmented batch.]

### 2.2 Custom CNN
[Model summary, per-layer output shapes/parameter counts, loss/optimizer/metrics and rationale.]

### 2.3 MobileNetV2 transfer learning
[Explain ImageNet preprocessing, frozen-head stage, last-block fine-tuning stage, trainable layers and curves.]

### 2.4 Training discipline
[Seed, early stopping, best-validation-loss checkpoint, ReduceLROnPlateau and best epoch.]

### 2.5 Evaluation
[Threshold selected from validation data only. Insert both model metric rows, confusion matrices, ROC curves and explain which product error is costlier.]

### 2.6 Error analysis
[Show ten test mistakes and a hypothesis for each.]

### 2.7 Keras Tuner
[Toy Fashion-MNIST trial table and at least eight VisionGuard trials. Discuss validation overfitting and most influential hyperparameter.]

## Task 3 — MLflow and DagsHub
### 3.1 Local MLflow toy lab
[Two learning-rate runs, comparison view, and definitions of experiment/run/parameter/metric/artifact/tag.]

### 3.2 DagsHub setup
[Repository screenshot, tracking URI configured through environment, token hidden, .env ignored.]

### 3.3 Instrumented training
[Manual callback versus TensorFlow autolog run pages; compare what each logs.]

### 3.4 Artifacts
[Artifacts tab showing confusion matrix, ROC, split lists, package list and model.]

### 3.5 Experiment comparison
[At least six controlled runs, one meaningful change at a time; compare and justify selected model.]

### 3.6 Registry
[Two registered versions, champion alias and alias prediction terminal output.]

## Task 4 — Flask web application
[Inference module loads champion once; explain identical preprocessing. Include two known-image outputs, upload/result/history/health screenshots, invalid MIME, oversized upload and undecodable image failures. Explain environment configuration and debug=False.]

## Task 5 — Database trail
[Show database schema and history rows: timestamp, filename, verdict, confidence, model and AI probability.]

## Task 6 — Docker and Compose
[Warm-up commands and definitions; Dockerfile layer cache/non-root/healthcheck; Compose healthy services and DB port isolation; image size before/after; start/stop/restart/logs/exec; deliberate failure, diagnosis and fix; CI red/green toy runs and project green run.]

## Task 7 — Cloud API deployment
[Provider and deployment steps, secrets/environment variables, API URL, Postman request/response and proof tested from another network.]

## Task 8 — Flask/API integration
[Show Flask configured with deployed API URL, multiple requests and corresponding database history entries.]

## Final checklist
- [ ] Real dataset audited and DVC-pushed
- [ ] Two models trained and evaluated
- [ ] Six or more MLflow experiment runs
- [ ] DagsHub registry contains two versions and champion alias
- [ ] Flask UI and database work
- [ ] Docker Compose works with healthy DB
- [ ] Cloud API publicly reachable and tested externally
- [ ] Flask calls the cloud API and records history
- [ ] All screenshots are genuine and captioned
