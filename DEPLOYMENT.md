# Deployment Guide - Mistral AI Edition

Complete guide to deploying the Avisia Chatbot with Mistral AI to Google Cloud Platform.

## Prerequisites

- Google Cloud Platform account with billing enabled
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed
- Mistral AI API key
- GTM container set up on target website

## Step 1: Set Up GCP Project

### 1.1 Create or Select Project

```bash
# List existing projects
gcloud projects list

# Create new project (optional)
gcloud projects create avisia-chatbot-mistral --name="Avisia Chatbot Mistral"

# Set as active project
gcloud config set project avisia-chatbot-mistral
```

### 1.2 Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build API (optional, for CI/CD)
gcloud services enable cloudbuild.googleapis.com
```

### 1.3 Set Default Region

```bash
# Set region (choose one close to your users)
gcloud config set run/region us-central1
```

## Step 2: Get Mistral API Key

### From Mistral AI Console

1. Go to https://console.mistral.ai/
2. Sign up or log in to your account
3. Navigate to **API Keys** in the sidebar
4. Click **Create new key**
5. Give it a name (e.g., "Production Chatbot")
6. Copy the API key (it won't be shown again!)
7. Store it securely

### API Key Security

Never commit API keys to version control. Use one of these methods:

**Option 1: Environment variable (simple)**
```bash
export MISTRAL_API_KEY=your_key_here
```

**Option 2: Secret Manager (production)**
```bash
# Create secret
echo -n "YOUR_API_KEY" | gcloud secrets create mistral-api-key --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding mistral-api-key \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

## Step 3: Deploy to Cloud Run

### 3.1 Navigate to Backend Directory

```bash
cd backend
```

### 3.2 Test Locally (Optional)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MISTRAL_API_KEY=your_api_key_here
export MISTRAL_MODEL=mistral-small-latest

# Run locally
python main.py

# Test in another terminal
curl http://localhost:8080/health
```

### 3.3 Deploy to Cloud Run

```bash
# Deploy with default model (mistral-small-latest)
gcloud run deploy avisia-chatbot-mistral \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MISTRAL_API_KEY=YOUR_MISTRAL_API_KEY \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10

# Note: Replace YOUR_MISTRAL_API_KEY with your actual API key
```

### 3.4 Deploy with Different Model

```bash
# Deploy with medium model (better quality, higher cost)
gcloud run deploy avisia-chatbot-mistral \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MISTRAL_API_KEY=YOUR_KEY,MISTRAL_MODEL=mistral-medium-latest \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10

# Deploy with large model (best quality, highest cost)
gcloud run deploy avisia-chatbot-mistral \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MISTRAL_API_KEY=YOUR_KEY,MISTRAL_MODEL=mistral-large-latest \
  --memory 1Gi \
  --cpu 2 \
  --timeout 90 \
  --max-instances 10
```

### 3.5 Get Service URL

```bash
# Get the service URL
gcloud run services describe avisia-chatbot-mistral \
  --region us-central1 \
  --format='value(status.url)'
```

Save this URL - you'll need it for GTM configuration!

## Step 4: Configure GTM

1. Follow the instructions in [gtm/README.md](gtm/README.md)
2. Use the Cloud Run URL from Step 3.5
3. Test in GTM Preview mode
4. Publish when ready

## Step 5: Mistral Model Comparison

| Model | Speed | Quality | Cost* | Tokens/sec | Best For |
|-------|-------|---------|-------|------------|----------|
| mistral-small-latest | Fast | Good | $ | ~100 | Quick responses, simple queries |
| mistral-medium-latest | Medium | Better | $$ | ~70 | Balanced performance |
| mistral-large-latest | Slower | Best | $$$ | ~50 | Complex reasoning, best accuracy |

*Check current pricing at https://mistral.ai/pricing/

### Switching Models

You can change models without redeploying code:

```bash
# Update to medium model
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --set-env-vars MISTRAL_MODEL=mistral-medium-latest

# Switch back to small model
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --set-env-vars MISTRAL_MODEL=mistral-small-latest
```

## Step 6: Production Optimizations

### 6.1 Set Up Custom Domain (Optional)

```bash
# Map custom domain
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --add-domain-mapping chat.yourdomain.com
```

### 6.2 Configure CORS Restrictions

```bash
# Restrict to your domain only
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --set-env-vars ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 6.3 Use Secret Manager (Production)

```bash
# Create secret
echo -n "YOUR_API_KEY" | gcloud secrets create mistral-api-key --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding mistral-api-key \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Update Cloud Run to use secret
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --update-secrets MISTRAL_API_KEY=mistral-api-key:latest
```

### 6.4 Set Up Cloud Monitoring

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# View logs
gcloud run logs read avisia-chatbot-mistral --region us-central1 --limit 50

# Follow logs in real-time
gcloud run logs tail avisia-chatbot-mistral --region us-central1

# Filter for errors only
gcloud run logs read avisia-chatbot-mistral \
  --region us-central1 \
  --filter="severity>=ERROR" \
  --limit 20
```

### 6.5 Configure Autoscaling

```bash
# Set min/max instances based on your traffic
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 20 \
  --concurrency 80
```

## Step 7: Cost Optimization

### Monitor Costs

```bash
# View Cloud Run costs in billing console
gcloud console --project=$(gcloud config get-value project)
```

### Optimization Strategies

1. **Use smaller model for simpler queries**
   ```bash
   --set-env-vars MISTRAL_MODEL=mistral-small-latest
   ```

2. **Reduce max instances**
   ```bash
   --max-instances 5
   ```

3. **Limit content length**
   ```bash
   --set-env-vars MAX_CONTENT_LENGTH=30000
   ```

4. **Set budget alerts** in GCP Console

## Step 8: Monitoring and Maintenance

### View Metrics

```bash
# Request count
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'

# Request latencies
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"'
```

### Update Service

```bash
# After making code changes
cd backend
gcloud run deploy avisia-chatbot-mistral --source .
```

### Roll Back

```bash
# List revisions
gcloud run revisions list \
  --service avisia-chatbot-mistral \
  --region us-central1

# Roll back to specific revision
gcloud run services update-traffic avisia-chatbot-mistral \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Service Errors

```bash
# Check logs
gcloud run logs read avisia-chatbot-mistral --region us-central1 --limit 100

# Check service status
gcloud run services describe avisia-chatbot-mistral --region us-central1
```

### Mistral API Errors

Common errors and solutions:

- **401 Unauthorized**: Check API key is correct
- **429 Rate Limit**: Reduce request rate or upgrade plan
- **500 Server Error**: Temporary Mistral AI issue, retry
- **Content too long**: Reduce MAX_CONTENT_LENGTH

### Performance Issues

```bash
# Increase memory and CPU for large model
gcloud run services update avisia-chatbot-mistral \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

## Security Checklist

- [ ] Use Secret Manager for API keys
- [ ] Configure CORS restrictions
- [ ] Enable Cloud Armor (for DDoS protection)
- [ ] Set up rate limiting
- [ ] Use HTTPS only
- [ ] Regularly rotate API keys
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated
- [ ] Set budget alerts
- [ ] Implement request logging

## Comparison: Mistral vs Gemini

| Feature | Mistral | Gemini |
|---------|---------|---------|
| Provider | Mistral AI (Europe) | Google |
| GDPR Compliance | Strong | Strong |
| Multilingual | Excellent | Excellent |
| Pricing | Competitive | Competitive |
| API Simplicity | Simple | Simple |
| Open Models | Yes | No |
| Integration | Standard REST | Standard REST |

Choose Mistral if:
- European data residency is important
- You want open-source model options
- You prefer European AI providers

## Next Steps

1. Test the chatbot on your website
2. Monitor usage and costs
3. Optimize model selection based on performance
4. Customize the UI to match your brand
5. Add analytics tracking
6. Consider implementing feedback collection

## Support

For issues:
- Mistral AI Documentation: https://docs.mistral.ai/
- GCP Cloud Run: https://cloud.google.com/run/docs
- Check Cloud Run logs
- Verify environment variables
