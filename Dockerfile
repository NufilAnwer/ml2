# Task 6.2 - Production Dockerfile for VisionGuard Web App
# Optimized with:
# 1. python:3.10-slim base image (cuts size vs standard python ~1GB image)
# 2. Dependency layer caching: requirements.txt copied & installed BEFORE source code
# 3. CPU-only tensorflow package (tensorflow-cpu) to save ~2GB CUDA overhead
# 4. Non-root user (appuser, UID 1000) for container security
# 5. Native HEALTHCHECK targeting /health

FROM python:3.10-slim AS base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (curl for healthcheck, libgomp for OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Layer caching: copy requirements first to cache dependency installation
COPY requirements.txt .

# Install dependencies without pip cache to save ~500MB
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and template/static directories
COPY app/ ./app/
COPY models/ ./models/

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose web port
EXPOSE 5000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start production server using waitress
CMD ["python", "-m", "app.app"]
