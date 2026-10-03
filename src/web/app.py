"""
FastAPI Server for Knowledge-Grounded Voice Calling Interface
Provides:
- Web Calling UI hosting
- Call turn processing with Voice Agent
- Edge-TTS neural speech synthesis streaming
- RAG Knowledge Base search API
- Mock CRM Leads API
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from ..agent.voice_bot import VoiceAgent
from ..agent.crm import MockCRM
from ..kb.retriever import HybridRetriever
from ..speech.tts import VoiceSynthesizer

load_dotenv()

app = FastAPI(title="ApexCare Voice Agent & Knowledge Base API", version="1.0.0")

# Mount static assets
static_dir = Path("src/web/static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Shared singletons
crm = MockCRM()
retriever = HybridRetriever()
agent = VoiceAgent(crm=crm, retriever=retriever)
tts = VoiceSynthesizer()


class CallTurnRequest(BaseModel):
    session_id: str
    user_transcript: str


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 3


@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "ApexCare Voice Agent API is running."}


@app.post("/api/call/start")
async def start_call():
    session_id = f"call_{uuid.uuid4().hex[:10]}"
    greeting_text = "Hello! Thank you for calling ApexCare Health Insurance. My name is Sarah. Are you looking to explore coverage options for yourself or your family today?"
    audio_path = await tts.synthesize(greeting_text)
    audio_url = f"/static/audio/{Path(audio_path).name}"

    agent.get_or_create_session(session_id)
    return {
        "session_id": session_id,
        "greeting": greeting_text,
        "audio_url": audio_url
    }


@app.post("/api/call/turn")
async def process_turn(req: CallTurnRequest):
    if not req.user_transcript.strip():
        raise HTTPException(status_code=400, detail="User transcript cannot be empty.")

    result = agent.process_turn(req.session_id, req.user_transcript)
    reply_text = result["reply"]

    # Synthesize neural voice
    audio_path = await tts.synthesize(reply_text)
    audio_url = f"/static/audio/{Path(audio_path).name}"

    return {
        "reply": reply_text,
        "audio_url": audio_url,
        "citations": result.get("citations", []),
        "session": result.get("session", {}),
        "lead_quote": result.get("lead_quote")
    }


@app.get("/api/kb/search")
async def search_kb(q: str, top_k: int = 3):
    res = retriever.search(q, top_k=top_k)
    return res.model_dump()


@app.get("/api/crm/leads")
async def get_crm_leads():
    leads = crm.get_all_leads()
    return [l.model_dump() for l in leads]


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "provider": agent.provider,
        "chunks_indexed": len(retriever.chunks),
        "crm_leads_stored": len(crm.leads)
    }
