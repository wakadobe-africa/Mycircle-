# ─────────────────────────────────────────────────────────────────────────────
# Multi-stage Dockerfile for MyCIRCLE (Flask + Gunicorn)
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Keep Python output unbuffered so logs appear immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies required by mysql-connector
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create the uploads directory that is excluded from git
RUN mkdir -p mycirclepkg/static/uploads

# Expose the port gunicorn will listen on
EXPOSE 5000

# Production start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
