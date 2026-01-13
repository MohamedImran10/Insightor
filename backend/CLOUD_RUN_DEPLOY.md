# Cloud Run Deployment Guide for Insightor Backend

## Required Environment Variables

Set these in Cloud Run → Edit & Deploy New Revision → Variables & Secrets:

```
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
USE_PINECONE=true
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
USE_WEAVIATE=false
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=research-agent-b7cb0
```

## Steps to Deploy

### 1. Build and Push Docker Image

```bash
# Set your project ID
export PROJECT_ID=research-agent-b7cb0

# Build the image
cd backend
docker build -t gcr.io/$PROJECT_ID/insightor-backend .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/insightor-backend
```

### 2. Deploy to Cloud Run (Console)

1. Go to Cloud Run Console
2. Click "Edit & Deploy New Revision"
3. Set Container image to: `gcr.io/research-agent-b7cb0/insightor-backend`
4. Set **Container port: 8080**
5. Add all environment variables from above
6. Set Memory: 2 GiB (recommended for ML models)
7. Set CPU: 2 (recommended)
8. Click Deploy

### 3. Or Deploy via CLI

```bash
gcloud run deploy insightor-backend \
  --image gcr.io/$PROJECT_ID/insightor-backend \
  --platform managed \
  --region us-central1 \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=xxx,TAVILY_API_KEY=xxx,USE_PINECONE=true,PINECONE_API_KEY=xxx,PINECONE_ENVIRONMENT=us-east-1,USE_WEAVIATE=false,FIREBASE_ENABLED=true,FIREBASE_PROJECT_ID=research-agent-b7cb0"
```

## Firebase Service Account (Important!)

For Cloud Run to access Firebase, you need to either:

### Option A: Use Secret Manager (Recommended)
1. Upload your Firebase service account JSON to Secret Manager
2. Mount it as a volume in Cloud Run
3. Set `FIREBASE_CREDENTIALS_PATH` to the mounted path

### Option B: Use Default Service Account
1. Give Cloud Run's service account Firebase Admin permissions
2. Remove `FIREBASE_CREDENTIALS_PATH` from env vars
3. Firebase Admin SDK will use default credentials

## Troubleshooting

If container fails to start:
- Check Cloud Logging for detailed errors
- Ensure PORT=8080 is being used
- Verify all required env vars are set
- Check memory allocation (ML models need 2GB+)
