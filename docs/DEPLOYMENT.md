# Cloud deployment and Flask integration

## Deploy the inference API

The API is a separate FastAPI service. Build it with Dockerfile.api, provide the champion model artifact, and configure these environment variables in the cloud dashboard:

MODEL_PATH=models/champion.keras
MODEL_FAMILY=cnn or mobilenet
MODEL_THRESHOLD=the validation-selected threshold
API_KEY=a long random secret
IMAGE_HEIGHT=224
IMAGE_WIDTH=224
MAX_UPLOAD_MB=8

The API exposes GET /health and authenticated POST /predict. The request uses multipart form field file and header X-API-Key. Never commit the API key or model secrets.

Cloud deployment steps:
1. Create a container/web service from this repository.
2. Select Dockerfile.api as the build file.
3. Make the champion model available to the service as a private artifact or mounted file; do not commit the large model to Git.
4. Configure the environment variables in the provider dashboard.
5. Deploy and wait for the health check.
6. Test /health and /predict with Postman from a different network.
7. Record the actual provider, settings, public API URL, Postman response and external-network test in the report.

A live URL is not available until the deployment is actually performed in the user's cloud account.

## Connect Flask to the cloud API

Set the following values in the local .env file used by Compose:

MODEL_API_URL=https://YOUR_PUBLIC_API_HOST
MODEL_API_KEY=the-same-secret-configured-on-the-api-service
POSTGRES_PASSWORD=your-local-database-password
FLASK_SECRET_KEY=a-long-random-flask-secret

Then run:

docker compose up --build -d
docker compose ps
docker compose logs -f web
docker compose logs -f db

Open http://localhost:5000, submit several images, and open History. Flask sends the image to the remote API and stores successful decisions in PostgreSQL. The database is not published to the host.

## Docker evidence commands

Use a warm-up image and capture the actual outputs:

docker run -d --name warmup -p 8080:80 nginx:alpine
docker logs warmup
docker exec -it warmup sh
docker stop warmup
docker rm warmup
docker image ls
docker history visionguard-web:latest
docker compose ps
docker compose restart web
docker compose exec web sh
docker compose exec db sh
docker compose down

For troubleshooting evidence, deliberately break a local test configuration (for example, a wrong database password), inspect logs, diagnose it, fix the value and capture both states. Do not use a broken configuration in a live deployment.
