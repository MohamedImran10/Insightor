#!/bin/bash
# Insightor Backend Deployment Script for Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Insightor Backend - Cloud Run Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
PROJECT_ID="research-agent-b7cb0"
SERVICE_NAME="insightor-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Step 1: Check if gcloud is installed
echo -e "\n${YELLOW}[1/5] Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Step 2: Set project
echo -e "\n${YELLOW}[2/5] Setting Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to $PROJECT_ID${NC}"

# Step 3: Build Docker image
echo -e "\n${YELLOW}[3/5] Building Docker image...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
docker build -t $IMAGE_NAME .
echo -e "${GREEN}✓ Docker image built successfully${NC}"

# Step 4: Push to Google Container Registry
echo -e "\n${YELLOW}[4/5] Pushing to Google Container Registry...${NC}"
echo -e "${YELLOW}This may take 2-5 minutes...${NC}"
docker push $IMAGE_NAME
echo -e "${GREEN}✓ Image pushed to GCR${NC}"

# Step 5: Deploy to Cloud Run
echo -e "\n${YELLOW}[5/5] Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_API_KEY=AIzaSyBW--0y8kDJKI1F_lrF8YMQ8aYKa1MafFE,TAVILY_API_KEY=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,USE_PINECONE=true,PINECONE_API_KEY=pcsk_3n2rkr_A2nij5UfSqC1hHbgsbQGr4gBPB854G2Wh8e7LnLBXUKCzNPpgfB9EKfBTNULb4S,PINECONE_ENVIRONMENT=us-east-1,USE_WEAVIATE=false,FIREBASE_ENABLED=true,FIREBASE_PROJECT_ID=research-agent-b7cb0,BACKEND_HOST=0.0.0.0,DEBUG=false"

# Get the service URL
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo -e "\n${GREEN}Your backend is now live at:${NC}"
echo -e "${GREEN}$SERVICE_URL${NC}"

echo -e "\n${YELLOW}Test your deployment:${NC}"
echo -e "curl $SERVICE_URL/health"
echo -e "curl $SERVICE_URL/debug"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Update your frontend .env.production with:"
echo -e "   ${GREEN}VITE_API_URL=$SERVICE_URL${NC}"
echo -e "2. Deploy your frontend to Vercel"
echo -e "3. Test the full application"

echo -e "\n${YELLOW}View logs:${NC}"
echo -e "gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50"
