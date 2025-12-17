# Avisia Chatbot - Mistral AI Edition

A lightweight chatbot that can be injected into any webpage via Google Tag Manager (GTM). It uses the webpage's content as context and is powered by Mistral AI.

## Features

- Injects via GTM - no code changes needed on target websites
- Smart content extraction - filters out navigation, ads, and irrelevant content
- Session-based conversation memory
- Vanilla JavaScript - no dependencies, lightweight
- Cloud Run backend - serverless, auto-scaling
- Powered by Mistral AI (mistral-small, mistral-medium, or mistral-large)

## Architecture

```
Webpage + GTM
    ↓ (injects chatbot.js + chatbot.css)
Chatbot UI
    ↓ (sends question + page content)
Cloud Run API
    ↓ (processes with Mistral AI)
Mistral API
    ↓ (returns AI response)
User sees answer
```

## Prerequisites

- Google Cloud Platform account with billing enabled
- Google Tag Manager container set up
- Mistral AI API key (from Mistral AI platform)

## Setup Instructions

### 1. Deploy Cloud Run Backend

```bash
# Set your GCP project ID
gcloud config set project YOUR_PROJECT_ID

# Set environment variables
export PROJECT_ID=YOUR_PROJECT_ID
export REGION=us-central1
export SERVICE_NAME=avisia-chatbot-mistral

# Deploy to Cloud Run
cd backend
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars MISTRAL_API_KEY=YOUR_MISTRAL_API_KEY
```

### 2. Configure Google Tag Manager

1. Go to your GTM container
2. Create a new **Custom HTML** tag
3. Copy the contents of `gtm/chatbot-tag.html`
4. Replace `YOUR_CLOUD_RUN_URL` with your Cloud Run service URL
5. Set trigger to **All Pages** (or specific pages as needed)
6. Save and publish the container

### 3. Get Mistral API Key

1. Go to https://console.mistral.ai/
2. Sign up or log in
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key (keep it secure!)

## Project Structure

```
avisia-chatbot-mistral/
├── backend/              # Cloud Run service
│   ├── main.py          # FastAPI application
│   ├── Dockerfile       # Container definition
│   └── requirements.txt # Python dependencies
├── client/              # Frontend code
│   ├── chatbot.js      # Main chatbot logic
│   └── chatbot.css     # Styling
├── gtm/                # GTM configuration
│   └── chatbot-tag.html # GTM tag template
└── README.md
```

## Configuration

### Backend Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key (required)
- `MISTRAL_MODEL`: Model to use (default: "mistral-small-latest")
  - Options: "mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"
- `ALLOWED_ORIGINS`: CORS origins (default: "*")
- `MAX_CONTENT_LENGTH`: Max webpage content length (default: 50000)

### Client Customization

Edit `client/chatbot.js`:
- `API_ENDPOINT`: Your Cloud Run URL
- `CHATBOT_POSITION`: 'bottom-right', 'bottom-left', etc.
- `PRIMARY_COLOR`: Brand color for the chatbot

Edit `client/chatbot.css`:
- Modify colors, fonts, animations to match your brand

## Mistral AI Models

Choose the model based on your needs:

| Model | Speed | Quality | Cost | Use Case |
|-------|-------|---------|------|----------|
| mistral-small-latest | Fast | Good | $ | Quick responses, simple queries |
| mistral-medium-latest | Medium | Better | $$ | Balanced performance |
| mistral-large-latest | Slower | Best | $$$ | Complex reasoning, best quality |

## Smart Content Extraction

The chatbot uses intelligent content extraction that:
- Removes navigation bars, headers, footers
- Filters out advertisements and tracking scripts
- Excludes repetitive elements
- Focuses on main content areas (article, main, content sections)
- Cleans up whitespace and formatting

## Session Management

- Conversations are stored in browser sessionStorage
- Persists across page navigation on the same site
- Cleared when browser tab is closed
- No backend storage required

## Cost Estimation

- **Cloud Run**: Free tier covers ~2 million requests/month
- **Mistral API**: Pay per request (check current pricing at https://mistral.ai/pricing/)
- **Bandwidth**: Minimal for text-based chat

Typical costs for 1000 conversations/day:
- Cloud Run: ~$0 (free tier)
- Mistral API: ~$5-15/month (depending on model)

## Security Considerations

- Add CORS restrictions in production
- Consider adding rate limiting
- Sanitize user input on backend
- Use HTTPS for Cloud Run endpoint
- Rotate API keys regularly
- Store API keys in Secret Manager (production)

## Troubleshooting

### Chatbot doesn't appear
- Check GTM tag is published
- Verify GTM trigger is firing
- Check browser console for errors

### API errors
- Verify Cloud Run URL is correct
- Check Mistral API key is valid
- Review Cloud Run logs: `gcloud run logs read $SERVICE_NAME`

### Content extraction issues
- Adjust selectors in `chatbot.js`
- Check for single-page app rendering delays
- Increase content extraction delay for dynamic sites

## Development

### Local Testing

Backend:
```bash
cd backend
pip install -r requirements.txt
export MISTRAL_API_KEY=your_key
python main.py
```

Client:
```bash
cd client
# Serve files with any HTTP server
python -m http.server 8080
```

### Updating

Backend:
```bash
gcloud run deploy $SERVICE_NAME --source .
```

GTM:
1. Update the Custom HTML tag in GTM
2. Publish new container version

## Comparison with Gemini Version

**Advantages of Mistral:**
- European-based company (GDPR friendly)
- Competitive pricing
- Strong multilingual support
- Open-source model options available

**Differences:**
- API endpoint and authentication
- Different model names and capabilities
- Separate API key management

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Mistral AI Documentation: https://docs.mistral.ai/
- Open an issue in the repository
