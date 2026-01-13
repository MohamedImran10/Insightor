# Cloud Run Deployment Guide for Insightor Backend

## Prerequisites
- Google Cloud SDK installed (`gcloud` command)
- Docker installed and running
- Google Cloud project created (`research-agent-b7cb0`)
- Pinecone account and API key

## Required Environment Variables

Set these in Cloud Run → Edit & Deploy New Revision → Variables & Secrets:

```
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
USE_PINECONE=true
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
USE_WEAVIATE=false
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=research-agent-b7cb0
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

## Deployment Steps

### Step 1: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project research-agent-b7cb0

# Configure Docker to use gcloud credentials
gcloud auth configure-docker
```

### Step 2: Build and Push Docker Image

```bash
# Navigate to backend directory
cd /home/imran/Desktop/AI_projects/Insightor/backend

# Set your project ID
export PROJECT_ID=research-agent-b7cb0

# Build the Docker image (this takes 5-10 minutes)
docker build -t gcr.io/$PROJECT_ID/insightor-backend .

# Push to Google Container Registry (takes 2-5 minutes)
docker push gcr.io/$PROJECT_ID/insightor-backend
```

### Step 3: Deploy to Cloud Run

#### Option A: Deploy via CLI (Recommended)

```bash
gcloud run deploy insightor-backend \
  --image gcr.io/research-agent-b7cb0/insightor-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_API_KEY=AIzaSyBW--0y8kDJKI1F_lrF8YMQ8aYKa1MafFE,TAVILY_API_KEY=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,USE_PINECONE=true,PINECONE_API_KEY=pcsk_3n2rkr_A2nij5UfSqC1hHbgsbQGr4gBPB854G2Wh8e7LnLBXUKCzNPpgfB9EKfBTNULb4S,PINECONE_ENVIRONMENT=us-east-1,USE_WEAVIATE=false,FIREBASE_ENABLED=true,FIREBASE_PROJECT_ID=research-agent-b7cb0,BACKEND_HOST=0.0.0.0,BACKEND_PORT=8000,DEBUG=false"
```

#### Option B: Deploy via Cloud Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **"CREATE SERVICE"** (or select existing service to update)
3. Configure the service:
   - **Container image URL**: `gcr.io/research-agent-b7cb0/insightor-backend:latest`
   - **Service name**: `insightor-backend`
   - **Region**: `us-central1`
   - **Authentication**: Allow unauthenticated invocations
4. Click **"Container, Networking, Security"** to expand:
   - **Container port**: `8000`
   - **Memory**: `2 GiB`
   - **CPU**: `2`
   - **Request timeout**: `300 seconds`
   - **Maximum instances**: `10`
5. Add **Environment Variables** (click "+ ADD VARIABLE" for each):
   ```
   GOOGLE_API_KEY=AIzaSyBW--0y8kDJKI1F_lrF8YMQ8aYKa1MafFE
   TAVILY_API_KEY=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
   USE_PINECONE=true
   PINECONE_API_KEY=pcsk_3n2rkr_A2nij5UfSqC1hHbgsbQGr4gBPB854G2Wh8e7LnLBXUKCzNPpgfB9EKfBTNULb4S
   PINECONE_ENVIRONMENT=us-east-1
   USE_WEAVIATE=false
   FIREBASE_ENABLED=true
   FIREBASE_PROJECT_ID=research-agent-b7cb0
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   DEBUG=false
   ```
6. Click **"CREATE"** or **"DEPLOY"**

### Step 4: Get Your Cloud Run URL

```bash
# Get the service URL
gcloud run services describe insightor-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

The URL will look like: `https://insightor-backend-xxxxx-uc.a.run.app`

### Step 5: Test Your Deployment

```bash
# Test health endpoint
curl https://insightor-backend-xxxxx-uc.a.run.app/health

# Test debug endpoint (should show Pinecone backend)
curl https://insightor-backend-xxxxx-uc.a.run.app/debug
```

### Step 6: Update Frontend Environment

Update your frontend `.env.production` file with the Cloud Run URL:

```bash
# In frontend/.env.production
VITE_API_URL=https://insightor-backend-xxxxx-uc.a.run.app
```

## Migration from Weaviate to Pinecone

If you have existing data in Weaviate that needs to be migrated to Pinecone:

```bash
# Run migration script locally (make sure both databases are accessible)
cd backend
python migrate_to_pinecone.py
```

## Monitoring and Logs

```bash
# View logs
gcloud run services logs read insightor-backend \
  --region us-central1 \
  --limit 50

# Follow logs in real-time
gcloud run services logs tail insightor-backend \
  --region us-central1
```

## Update Deployment (After Code Changes)

```bash
# Rebuild and push
docker build -t gcr.io/research-agent-b7cb0/insightor-backend .
docker push gcr.io/research-agent-b7cb0/insightor-backend

# Cloud Run will auto-detect and you can deploy new revision
# Or manually trigger:
gcloud run services update insightor-backend \
  --region us-central1 \
  --image gcr.io/research-agent-b7cb0/insightor-backend:latest
```

## Troubleshooting

### Issue: Container fails to start
- Check logs: `gcloud run services logs read insightor-backend`
- Verify environment variables are set correctly
- Ensure container port matches (8000)

### Issue: Out of memory errors
- Increase memory allocation to 4 GiB
- Reduce batch sizes in code

### Issue: Timeout errors
- Increase timeout to 900 seconds (max)
- Optimize slow operations

### Issue: Pinecone connection errors
- Verify PINECONE_API_KEY is correct
- Verify PINECONE_ENVIRONMENT matches your index region
- Check Pinecone dashboard for index status

## Cost Optimization

- Set **min-instances=0** for development (cold starts OK)
- Set **min-instances=1** for production (faster response)
- Use **--concurrency=80** to handle more requests per instance
- Monitor usage in Cloud Console → Cloud Run → Metrics

## Next Steps

1. ✅ Backend deployed to Cloud Run
2. Deploy frontend to Vercel (see frontend/README.md)
3. Update CORS settings if needed
4. Set up custom domain (optional)
5. Enable Cloud Run authentication (optional)
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
