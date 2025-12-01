# Dockerfile
FROM python:3.12-slim

# System deps (optional but often useful, e.g. for bandit/pylint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Cloud Run sets $PORT; default to 8080 for local testing.
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# IMPORTANT: do NOT hardcode API keys; pass GOOGLE_API_KEY at deploy time.
# ENV GOOGLE_API_KEY=...

EXPOSE 8080

# Start FastAPI via uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
