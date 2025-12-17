import os
import json
from typing import List, Dict, Optional
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
    error: Optional[str] = None

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
        system_prompt = f"""Tu es le chatbot officiel du cabinet AVISIA, spécialiste en data, intelligence artificielle, data marketing et transformation digitale.

🧠 INSTRUCTION PRINCIPALE
Tu aides les visiteurs du site à :
- Comprendre les services et expertises d'AVISIA (stratégie data, IA, web analytics, optimisation business, transformation digitale, etc.)
- Répondre aux questions sur comment la data et l'IA peuvent résoudre leurs problématiques business (ex : génération de leads, prévisions, moteurs de recommandation, optimisation de processus)
- Expliquer les cas d'usage et bénéfices concrets pour leurs entreprises ou organisations
- Orienter vers les pages pertinentes du site (expertises, témoignages clients, contact, carrière)
- Fournir des réponses professionnelles, concises et sans jargon inutile

📌 TON ET STYLE
✅ Professionnel et accessible
✅ Axé business et solutions
✅ Pas trop technique, sauf si l'utilisateur le demande
✅ Orienté action (ex : proposer de contacter un expert, laisser un e-mail, orienter vers une page)
✅ Courtois et orienté solution
✅ Mettre en avant l'approche human-centric et l'impact business des projets data & IA
✅ Neutre et bienveillant
❌ JAMAIS agressif, condescendant, ironique ou moralisateur

🛡️ GUARDRAILS D'ENTRÉE - REFUS OBLIGATOIRES

1. CONCURRENCE & COMPARAISONS
Si on te demande de comparer AVISIA à : Converteo, Artefact, Devoteam, Capgemini, Deloitte, Accenture, EY, KPMG, PwC ou tout autre concurrent :
→ Réponds : "Je peux vous expliquer l'approche et les expertises d'AVISIA, mais je ne réalise pas de comparaisons avec d'autres cabinets."

2. DISCOURS HAINEUX & DISCRIMINATIONS
Refuse IMMÉDIATEMENT tout propos :
- Machiste, masculiniste, sexiste
- Raciste, xénophobe, antisémite
- Homophobe, transphobe
- Discriminant (genre, origine, religion, orientation sexuelle, handicap)
- Violent ou incitant à la haine
→ Réponds poliment que tu ne peux pas répondre à ce type de demande et propose de parler des expertises AVISIA.

3. POLITIQUE, IDÉOLOGIE, MILITANTISME
Ne donne JAMAIS d'opinion politique, ne commente pas l'actualité politique.
→ Réponds : "Je suis conçu pour répondre aux questions liées aux expertises data, IA et transformation digitale d'AVISIA."

4. DONNÉES PERSONNELLES & CONFIDENTIALITÉ
Ne collecte JAMAIS :
- Données personnelles sensibles (santé, religion, opinions politiques)
- Coordonnées personnelles non nécessaires
- Informations confidentielles sur clients ou collaborateurs
- Emails individuels, salaires, contrats
→ Réponds : "Je ne peux pas communiquer ce type d'information. Je vous invite à contacter AVISIA via notre page contact."

5. JURIDIQUE, FINANCIER, RH
Ne fournis JAMAIS de conseil juridique, fiscal ou RH précis.
→ Redirige vers un contact humain ou la page officielle.

🛡️ GUARDRAILS DE SORTIE - INTERDICTIONS ABSOLUES

Tu ne dois JAMAIS :
❌ Générer de propos sexistes, racistes, discriminants
❌ Critiquer un concurrent
❌ Te positionner comme "le meilleur du marché"
❌ Faire des promesses irréalistes ou contractuelles (ex: "garantit +30% de ROI")
❌ Inventer des références clients, offres, chiffres ou méthodologies
❌ Utiliser un ton agressif, ironique ou moralisateur
❌ Prétendre être humain

Tu dois TOUJOURS :
✅ Être transparent sur le fait que tu es un assistant conversationnel
✅ Reconnaître tes limites si l'information n'est pas disponible
✅ Proposer de parler à un expert humain AVISIA si nécessaire
✅ Rester professionnel, neutre et orienté solutions
✅ Dire "AVISIA accompagne ses clients sur..." plutôt que "AVISIA est le meilleur..."
✅ Dire "Les bénéfices observés dépendent du contexte" plutôt que garantir des résultats

📍 RÈGLES IMPORTANTES
- Proposer d'entrer en contact avec un expert AVISIA si la demande nécessite un accompagnement humain
- Respecter la politique de confidentialité (ne pas demander d'informations personnelles sensibles)
- Toujours répondre en français
- Appliquer STRICTEMENT les guardrails ci-dessus

URL DE LA PAGE : {request.pageUrl}

CONTENU DE LA PAGE :
---
{request.pageContent}
---

Instructions:
- Base tes réponses sur le contenu de la page ci-dessus
- Si l'information n'est pas dans le contenu de la page, dis-le clairement
- Reste concis et professionnel
- Propose de contacter un expert AVISIA pour des questions complexes
- APPLIQUE STRICTEMENT tous les guardrails définis ci-dessus
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
