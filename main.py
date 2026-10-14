import os
import json
from pathlib import Path
from typing import List, Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tamil_corrector import TamilSpeechProcessor

app = FastAPI(
    title="Tamil Speech-to-Type & Corrector API",
    description="Fullstack Tamil voice input processing app with punctuation command support ('நிறுத்து' -> '.', 'தொடர்' -> ',') and Gemini / ChatGPT AI integration",
    version="1.1.0"
)

# Enable CORS for mobile browsers / WebView requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ProcessSpeechRequest(BaseModel):
    raw_text: str
    auto_correct_grammar: Optional[bool] = True

class SaveNoteRequest(BaseModel):
    title: str
    content: str
    timestamp: Optional[str] = None

class AITransformRequest(BaseModel):
    text: str
    provider: str = "gemini"  # "gemini" or "chatgpt"
    action: str = "polish"    # "polish", "translate_en", "translate_ta", "summarize", "formal_email", "reply", "custom"
    custom_prompt: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

# In-memory history store (saved notes)
SAVED_NOTES: List[dict] = []


@app.post("/api/process-speech")
async def process_speech(request: ProcessSpeechRequest):
    """
    Processes raw Tamil speech input:
    - Converts 'நிறுத்து' to '.'
    - Converts 'தொடர்' to ','
    - Applies spoken to written Tamil grammar rules
    """
    if not request.raw_text:
        return {"processed_text": "", "raw_input": ""}
    
    result = TamilSpeechProcessor.process_full(
        raw_text=request.raw_text,
        auto_correct_grammar=request.auto_correct_grammar
    )
    return result

@app.post("/api/correct")
async def correct_text(request: ProcessSpeechRequest):
    """
    Standard text normalization endpoint for existing text.
    """
    result = TamilSpeechProcessor.process_full(
        raw_text=request.raw_text,
        auto_correct_grammar=True
    )
    return result

@app.get("/api/commands")
async def get_commands():
    """
    Returns supported voice punctuation commands for UI display.
    """
    return {
        "commands": [
            {"command": "நிறுத்து", "action": "முற்றுப்புள்ளி (.)", "example": "நான் வருகிறேன் நிறுத்து -> நான் வருகிறேன்."},
            {"command": "தொடர்", "action": "காற்புள்ளி (,)", "example": "வணக்கம் தொடர் நலமா -> வணக்கம், நலமா"},
            {"command": "புதிய வரி / அடுத்த வரி", "action": "புதிய வரி (New Line)", "example": "முதல் வரி புதிய வரி இரண்டாம் வரி"},
            {"command": "கேள்விக்குறி", "action": "வினாக்குறி (?)", "example": "எப்படி இருக்கிறாய் கேள்விக்குறி -> எப்படி இருக்கிறாய்?"},
            {"command": "வியப்புக்குறி", "action": "ஆச்சரியக்குறி (!)", "example": "அற்புதம் வியப்புக்குறி -> அற்புதம்!"}
        ]
    }

@app.get("/api/history")
async def get_history():
    """
    Returns saved Tamil text transcriptions.
    """
    return {"notes": SAVED_NOTES}

@app.post("/api/history")
async def save_history(note: SaveNoteRequest):
    """
    Saves a transcribed note.
    """
    note_dict = {
        "id": len(SAVED_NOTES) + 1,
        "title": note.title or "தமிழ்ப் பதிவு",
        "content": note.content,
        "timestamp": note.timestamp
    }
    SAVED_NOTES.insert(0, note_dict)
    return {"status": "success", "note": note_dict}

@app.delete("/api/history/{note_id}")
async def delete_history(note_id: int):
    """
    Deletes a saved note by ID.
    """
    global SAVED_NOTES
    SAVED_NOTES = [n for n in SAVED_NOTES if n.get("id") != note_id]
    return {"status": "deleted"}

# --- AI Transformation (Gemini & ChatGPT) Utilities & Endpoints ---

def build_ai_prompt(action: str, text: str, custom_prompt: Optional[str] = None) -> tuple[str, str]:
    """
    Returns (system_prompt, user_content) tuned for Tamil language processing.
    """
    if action == "polish":
        system = (
            "You are an expert Tamil linguist and editor. The user provides text in Tamil (spoken, colloquial, or voice transcript). "
            "Rewrite and polish it into natural, grammatically sound, clear, and elegant written Tamil (தூய மற்றும் தெளிவான எழுத்துத் தமிழ்). "
            "Correct spelling errors, sandhi rules (சந்திப் பிழைகள்), and punctuation. "
            "Preserve the original meaning and tone completely. "
            "Return ONLY the polished Tamil text, with no introductory or concluding explanations."
        )
        user = text
    elif action == "translate_en":
        system = (
            "You are a professional Tamil-to-English translator. Translate the provided Tamil text into "
            "accurate, fluent, and natural English. Return ONLY the English translation, with no extra commentary."
        )
        user = text
    elif action == "translate_ta":
        system = (
            "You are an expert English-to-Tamil translator. Translate the provided text into "
            "natural, fluent, and grammatically accurate Tamil (எழுத்துத் தமிழ்). Return ONLY the Tamil translation."
        )
        user = text
    elif action == "summarize":
        system = (
            "You are an expert summarizer. Summarize the core points of the given Tamil text concisely and clearly in Tamil. "
            "Use clean bullet points or a short concise paragraph. Return ONLY the summary in Tamil."
        )
        user = text
    elif action == "formal_email":
        system = (
            "You are a professional Tamil communications expert. Transform the provided raw text or rough notes into "
            "a formal, courteous, and well-structured letter or email in Tamil (with formal salutation, polite body, and professional closing). "
            "Return ONLY the formatted letter or email text."
        )
        user = text
    elif action == "reply":
        system = (
            "You are a helpful, respectful, and intelligent AI assistant. The user provides a message, question, or thought in Tamil. "
            "Formulate a thoughtful, comprehensive, and helpful reply in Tamil. Return ONLY the reply."
        )
        user = text
    elif action == "custom":
        inst = custom_prompt.strip() if custom_prompt else "Enhance and improve the following text."
        system = (
            f"You are a helpful AI assistant. Follow this instruction carefully on the provided text:\n"
            f"Instruction: {inst}\n"
            "Return ONLY the processed output without any conversational preamble or wrap-around code blocks."
        )
        user = text
    else:
        system = "You are a helpful Tamil assistant. Polish and improve this text in Tamil. Return ONLY the result."
        user = text

    return system, user


async def call_gemini_api(system_prompt: str, user_prompt: str, api_key: str, model: Optional[str] = None) -> str:
    # Use gemini-2.5-flash by default, fallback to gemini-1.5-flash if needed
    model_name = model or "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "parts": [{"text": user_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, json=payload)

        # Fallback to gemini-1.5-flash if 2.5-flash is not available for this key
        if response.status_code == 404 and "gemini-2.5-flash" in model_name:
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            response = await client.post(fallback_url, json=payload)

        if response.status_code != 200:
            error_detail = response.text
            try:
                err_json = response.json()
                error_detail = err_json.get("error", {}).get("message", error_detail)
            except Exception:
                pass
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Gemini API பிழை ({response.status_code}): {error_detail}"
            )

        data = response.json()
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini-ல் இருந்து பதில் எதுவும் பெறப்படவில்லை.")
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini பதிலை எடுப்பதில் பிழை: {str(e)}")


async def call_chatgpt_api(system_prompt: str, user_prompt: str, api_key: str, model: Optional[str] = None) -> str:
    model_name = model or "gpt-4o-mini"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            error_detail = response.text
            try:
                err_json = response.json()
                error_detail = err_json.get("error", {}).get("message", error_detail)
            except Exception:
                pass
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ChatGPT API பிழை ({response.status_code}): {error_detail}"
            )

        data = response.json()
        try:
            choices = data.get("choices", [])
            if not choices:
                raise ValueError("ChatGPT-ல் இருந்து பதில் எதுவும் பெறப்படவில்லை.")
            text = choices[0].get("message", {}).get("content", "").strip()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ChatGPT பதிலை எடுப்பதில் பிழை: {str(e)}")


@app.get("/api/ai-config")
async def get_ai_config():
    """
    Checks if API keys are configured on the server environment.
    """
    return {
        "has_server_gemini_key": bool(os.environ.get("GEMINI_API_KEY")),
        "has_server_openai_key": bool(os.environ.get("OPENAI_API_KEY"))
    }


@app.post("/api/ai-transform")
async def ai_transform(request: AITransformRequest):
    """
    Transforms text using Gemini AI or ChatGPT (OpenAI).
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="மாற்றுவதற்கான உரை காலியாக உள்ளது. தயவுசெய்து உரையை தட்டச்சு செய்யவும் அல்லது பேசவும்."
        )

    provider = request.provider.lower().strip()
    system_prompt, user_prompt = build_ai_prompt(request.action, request.text, request.custom_prompt)

    if provider in ["gemini", "google"]:
        api_key = (request.api_key or "").strip() or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Gemini API Key வழங்கப்படவில்லை. அமைப்பில் உங்கள் இலவச Gemini API Key-ஐ உள்ளிடவும் அல்லது பக்கத்தில் உள்ள 'Gemini-ல் திற' பொத்தானைப் பயன்படுத்தவும்."
            )
        transformed = await call_gemini_api(system_prompt, user_prompt, api_key, request.model)
        return {
            "status": "success",
            "provider": "Gemini AI",
            "action": request.action,
            "transformed_text": transformed
        }

    elif provider in ["chatgpt", "openai"]:
        api_key = (request.api_key or "").strip() or os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="ChatGPT (OpenAI) API Key வழங்கப்படவில்லை. அமைப்பில் உங்கள் OpenAI API Key-ஐ உள்ளிடவும் அல்லது பக்கத்தில் உள்ள 'ChatGPT-ல் திற' பொத்தானைப் பயன்படுத்தவும்."
            )
        transformed = await call_chatgpt_api(system_prompt, user_prompt, api_key, request.model)
        return {
            "status": "success",
            "provider": "ChatGPT",
            "action": request.action,
            "transformed_text": transformed
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"செல்லுபடியாகாத AI வழங்குநர்: '{request.provider}'. 'gemini' அல்லது 'chatgpt'-ஐத் தேர்ந்தெடுக்கவும்."
        )


# Mount static files directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Tamil Speech-to-Type API Server Running</h1><p>Static files loading...</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
