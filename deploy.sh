#!/bin/bash

# AgriNova FastAPI Deployment Script for Google Cloud Run
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # Replace with your GCP project ID
SERVICE_NAME="agrinova-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying AgriNova API to Google Cloud Run"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME . --no-cache

# Test the image locally first
echo "🧪 Testing image locally..."
docker run --rm -d --name agrinova-test -p 8080:8080 $IMAGE_NAME
sleep 10

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Local test passed"
    docker stop agrinova-test
else
    echo "❌ Local test failed"
    docker logs agrinova-test
    docker stop agrinova-test
    exit 1
fi

echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "🧪 Test your API:"
echo "curl -X POST \"$SERVICE_URL/predict\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"Customer_ID\": 101, \"Recency_Days\": 10, \"Frequency\": 5, \"Monetary\": 500.0, \"Avg_Order_Value\": 100.0, \"Total_Items_Sold\": 20, \"Attribution\": \"Organic: Google\", \"Customer_Type\": \"new\"}'"
echo ""
echo "📊 API Documentation: $SERVICE_URL/docs"
