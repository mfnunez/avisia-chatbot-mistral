# Quick Start Guide - Mistral AI Edition

Get your Mistral AI-powered chatbot up and running in 15 minutes!

## Prerequisites

- Google Cloud account with billing
- Google Tag Manager container
- Mistral AI API key

## Step 1: Get Mistral API Key (2 minutes)

1. Go to https://console.mistral.ai/
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new API key
5. Copy the key

## Step 2: Deploy Backend (5 minutes)

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy from backend directory
cd backend
gcloud run deploy avisia-chatbot-mistral \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MISTRAL_API_KEY=YOUR_API_KEY

# Get the service URL
gcloud run services describe avisia-chatbot-mistral \
  --region us-central1 \
  --format='value(status.url)'
```

Copy the service URL (e.g., `https://avisia-chatbot-mistral-xxx.run.app`)

## Step 3: Configure GTM (5 minutes)

1. Open GTM
2. Create new **Custom HTML** tag
3. Copy contents of [gtm/chatbot-tag.html](gtm/chatbot-tag.html)
4. Replace `YOUR_CLOUD_RUN_URL` with your Cloud Run URL
5. Set trigger to **All Pages**
6. Save and publish

## Step 4: Test (3 minutes)

1. Visit your website
2. Click the chatbot button (bottom right)
3. Ask: "What is this page about?"
4. The chatbot should respond with page content!

## Done!

Your Mistral AI-powered chatbot is live. Now you can:

- Customize the styling in the GTM tag
- Choose different Mistral models (small, medium, large)
- Adjust content extraction settings
- Monitor usage in Cloud Run console

## Model Selection

Choose the right model for your needs:

```bash
# Use small model (fast, cheaper) - DEFAULT
--set-env-vars MISTRAL_MODEL=mistral-small-latest

# Use medium model (balanced)
--set-env-vars MISTRAL_MODEL=mistral-medium-latest

# Use large model (best quality)
--set-env-vars MISTRAL_MODEL=mistral-large-latest
```

## Troubleshooting

**Chatbot doesn't appear**
- Check GTM published successfully
- View browser console for errors

**No response from chatbot**
- Verify Cloud Run URL is correct
- Check Cloud Run logs: `gcloud run logs read avisia-chatbot-mistral`
- Verify Mistral API key is valid

**Wrong content extracted**
- Adjust selectors in chatbot JavaScript
- Check page structure with browser DevTools

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- See [README.md](README.md) for full documentation
- Check Mistral pricing: https://mistral.ai/pricing/

## Cost Estimate

For typical usage (1000 conversations/day):
- Cloud Run: ~$0 (within free tier)
- Mistral API (small model): ~$5-10/month

Total: Under $15/month for most use cases!

## Why Mistral AI?

- **European company**: GDPR-compliant
- **Multilingual**: Strong support for French, German, Spanish, Italian
- **Open models**: Some models available open-source
- **Competitive pricing**: Good quality-to-cost ratio
