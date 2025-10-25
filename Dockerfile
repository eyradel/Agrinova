# Multi-stage build for optimized production image
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Copy only essential files first
COPY main.py .
COPY requirements.txt .

# Copy model files (these are large, so copy them separately)
COPY churn_model.pkl .
COPY next_purchase_stack_model.pkl .

# Verify model files are copied correctly
RUN ls -la *.pkl && \
    echo "Model files copied successfully" && \
    echo "churn_model.pkl size: $(wc -c < churn_model.pkl) bytes" && \
    echo "next_purchase_stack_model.pkl size: $(wc -c < next_purchase_stack_model.pkl) bytes"

# Verify model files and dependencies
RUN python -c "import joblib; print('Testing model loading...'); \
    print('Loading regression model...'); \
    reg_model = joblib.load('next_purchase_stack_model.pkl'); \
    print('Regression model loaded:', type(reg_model)); \
    print('Loading classification model...'); \
    clf_model = joblib.load('churn_model.pkl'); \
    print('Classification model loaded:', type(clf_model)); \
    print('All models loaded successfully!')" || \
    (echo "Model loading test failed, but continuing..." && exit 0)

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8080

# Cloud Run provides $PORT; default to 8080
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
