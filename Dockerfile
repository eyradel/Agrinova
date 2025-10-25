# Use official Python image
FROM python:3.10-slim

# Install system deps for opencv and others
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python deps first (leverage caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure models are present in image (expects models/best.onnx in repo)
# If your model is large, consider using GCS at runtime instead.

# Expose port
EXPOSE 8080

# Cloud Run provides $PORT; default to 8080
ENV PORT=8080

# Start uvicorn and bind to 0.0.0.0:$PORT, selecting desired module
# Change main to api_esp:app if you want that entrypoint
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1
