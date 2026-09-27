# Production Dockerfile for Google Cloud Run (100% Free Tier Eligible)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run with Gunicorn on Cloud Run dynamic $PORT (1 worker, 8 threads for lightweight sub-50ms execution)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
