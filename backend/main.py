import os
import json
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mistralai import Mistral
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Avisia Chatbot API - Mistral Edition")

# Configure CORS - allows GTM-injected script to call this API
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Mistral AI
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

# Initialize Mistral client
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# Model configuration
MODEL_NAME = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))

# Request/Response models
class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    pageContent: str
    pageUrl: str
    conversationHistory: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    error: str = None

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Avisia Chatbot API - Mistral Edition",
        "model": MODEL_NAME
    }

@app.get("/health")
def health_check():
    """Health check for Cloud Run"""
    return {"status": "healthy", "model": MODEL_NAME}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user questions with webpage context
    """
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(request.pageContent) > MAX_CONTENT_LENGTH:
            # Truncate content if too long
            request.pageContent = request.pageContent[:MAX_CONTENT_LENGTH] + "...[content truncated]"

        # Build the system prompt with context
        system_prompt = f"""You are a helpful AI assistant embedded in a webpage chatbot.
Your role is to answer questions about the current webpage content.

WEBPAGE URL: {request.pageUrl}

WEBPAGE CONTENT:
---
{request.pageContent}
---

Instructions:
- Answer questions based on the webpage content above
- Be concise and helpful
- If the answer is not in the webpage content, say so clearly
- Provide specific references to sections when relevant
- Keep responses conversational and friendly
"""

        # Build conversation messages for Mistral API
        messages = []

        # Add system message
        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # Add conversation history
        for msg in request.conversationHistory:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # Call Mistral API
        chat_response = mistral_client.chat.complete(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # Extract response
        assistant_message = chat_response.choices[0].message.content

        return ChatResponse(
            response=assistant_message,
            error=None
        )

    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            error=str(e)
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "response": "An unexpected error occurred. Please try again later.",
        "error": str(exc)
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"Starting server with model: {MODEL_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=port)
