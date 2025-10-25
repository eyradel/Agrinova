# AgriNova API - Google Cloud Deployment Guide

This guide will help you deploy your AgriNova FastAPI application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud CLI**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Docker**: Install from [docker.com](https://docker.com)

## Setup Steps

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth configure-docker
```

### 2. Set Your Project ID

Edit `deploy.sh` and replace `your-gcp-project-id` with your actual GCP project ID:

```bash
PROJECT_ID="your-actual-project-id"
```

### 3. Deploy to Google Cloud Run

**Option A: Using the deployment script (Recommended)**

```bash
chmod +x deploy.sh
./deploy.sh
```

**Option B: Manual deployment**

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export SERVICE_NAME="agrinova-api"
export REGION="us-central1"

# Build and push the image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080
```

## Configuration

### Environment Variables

The application uses these environment variables:

- `PORT`: Server port (default: 8080)
- `PYTHONUNBUFFERED`: Python output buffering (set to 1)

### Resource Limits

- **Memory**: 2GB
- **CPU**: 2 cores
- **Timeout**: 5 minutes
- **Max Instances**: 10
- **Concurrency**: 80 requests per instance

## Testing Your Deployment

### 1. Health Check

```bash
curl https://your-service-url/health
```

### 2. API Documentation

Visit: `https://your-service-url/docs`

### 3. Test Prediction

```bash
curl -X POST "https://your-service-url/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Customer_ID": 101,
    "Recency_Days": 10,
    "Frequency": 5,
    "Monetary": 500.0,
    "Avg_Order_Value": 100.0,
    "Total_Items_Sold": 20,
    "Attribution": "Organic: Google",
    "Customer_Type": "new"
  }'
```

## Monitoring

### View Logs

```bash
gcloud run services logs read agrinova-api --region us-central1
```

### Monitor Performance

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Cloud Run
3. Select your service
4. View metrics and logs

## Cost Optimization

- **Min Instances**: 0 (scales to zero when not in use)
- **Max Instances**: 10 (prevents runaway costs)
- **CPU Allocation**: Only during request processing
- **Memory**: Optimized for ML model loading

## Troubleshooting

### Common Issues

1. **Models not loading**: Ensure all dependencies are in requirements.txt
2. **Memory errors**: Increase memory allocation in deployment
3. **Timeout errors**: Increase timeout or optimize model loading
4. **Cold start delays**: Consider keeping min instances > 0

### Debug Commands

```bash
# Check service status
gcloud run services describe agrinova-api --region us-central1

# View recent logs
gcloud run services logs read agrinova-api --region us-central1 --limit 50

# Test locally
docker run -p 8080:8080 gcr.io/PROJECT_ID/agrinova-api
```

## Security

- ✅ Non-root user in container
- ✅ HTTPS enforced
- ✅ No authentication required (public API)
- ✅ Resource limits applied
- ✅ Health checks enabled

## Scaling

The service will automatically scale based on:
- Request volume
- CPU utilization
- Memory usage
- Concurrent requests

## Updates

To update your deployment:

```bash
# Rebuild and redeploy
docker build -t gcr.io/$PROJECT_ID/agrinova-api .
docker push gcr.io/$PROJECT_ID/agrinova-api
gcloud run deploy agrinova-api --image gcr.io/$PROJECT_ID/agrinova-api
```
