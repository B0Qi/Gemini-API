import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from gemini_webapi import GeminiClient
from gemini_webapi.constants import Model
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

app = FastAPI(title="Gemini OpenAI Compatible API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
SECURE_1PSID = os.getenv('SECURE_1PSID')
SECURE_1PSIDTS = os.getenv('SECURE_1PSIDTS')
PORT = int(os.getenv('PORT', 8080))
HOST = os.getenv('HOST', '0.0.0.0')

if not SECURE_1PSID:
    raise ValueError("SECURE_1PSID not found in environment. Please set it in config.env")

client = None
client_lock = asyncio.Lock()
chat_sessions = {}

# Cookie file path for persistence
COOKIE_FILE = Path("/app/cookies/gemini_cookies.json")

# OpenAI compatible models
class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:8]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Usage

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "google"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

# Model mapping
GEMINI_MODEL_MAP = {
    "gpt-3.5-turbo": "gemini-2.5-flash",
    "gpt-4": "gemini-2.5-pro",
    "gpt-4-turbo": "gemini-2.5-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.0-flash-thinking": "gemini-2.0-flash-thinking",
}

def save_cookies(cookies: dict):
    """Save cookies to file for persistence"""
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f)

def load_cookies():
    """Load cookies from file if exists"""
    if COOKIE_FILE.exists():
        try:
            with open(COOKIE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

async def get_client():
    global client
    async with client_lock:
        if client is None:
            # Try to load saved cookies first
            saved_cookies = load_cookies()
            if saved_cookies:
                try:
                    client = GeminiClient(
                        saved_cookies.get('SECURE_1PSID', SECURE_1PSID),
                        saved_cookies.get('SECURE_1PSIDTS', SECURE_1PSIDTS),
                        proxy=None
                    )
                except:
                    # Fall back to env cookies if saved ones fail
                    client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS, proxy=None)
            else:
                client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS, proxy=None)
            
            await client.init(timeout=30, auto_close=False, close_delay=300, auto_refresh=True)
            
            # Save working cookies
            if client:
                save_cookies({
                    'SECURE_1PSID': SECURE_1PSID,
                    'SECURE_1PSIDTS': SECURE_1PSIDTS
                })
    return client

@app.on_event("startup")
async def startup_event():
    try:
        await get_client()
        print("✅ Gemini client initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize Gemini client on startup: {e}")
        print("   Client will be initialized on first request")

def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens (1 token ≈ 4 characters)"""
    return len(text) // 4

def format_messages_for_gemini(messages: List[Message]) -> str:
    """Convert OpenAI format messages to a single prompt for Gemini"""
    formatted_parts = []
    
    for msg in messages:
        role = msg.role
        content = msg.content
        
        if role == "system":
            formatted_parts.append(f"System: {content}")
        elif role == "user":
            formatted_parts.append(f"User: {content}")
        elif role == "assistant":
            formatted_parts.append(f"Assistant: {content}")
    
    return "\n\n".join(formatted_parts)

async def stream_response(response_text: str, model: str, request_id: str) -> AsyncGenerator[str, None]:
    """Stream response in OpenAI format"""
    chunks = response_text.split()
    
    for i, chunk in enumerate(chunks):
        if i > 0:
            chunk = " " + chunk
            
        chunk_data = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": chunk},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk_data)}\n\n"
        await asyncio.sleep(0.01)
    
    # Send final chunk
    final_chunk = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/")
async def root():
    return {
        "message": "Gemini OpenAI Compatible API",
        "docs": "/docs",
        "openai_base_url": f"http://{HOST}:{PORT}/v1"
    }

@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """List available models in OpenAI format"""
    models = [
        ModelInfo(id="gpt-3.5-turbo", owned_by="openai-mapped"),
        ModelInfo(id="gpt-4", owned_by="openai-mapped"),
        ModelInfo(id="gemini-2.5-flash", owned_by="google"),
        ModelInfo(id="gemini-2.5-pro", owned_by="google"),
    ]
    return ModelsResponse(data=models)

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """Create chat completion in OpenAI format"""
    try:
        gemini_client = await get_client()
        
        # Map model name
        gemini_model = GEMINI_MODEL_MAP.get(request.model, request.model)
        
        # Format messages
        prompt = format_messages_for_gemini(request.messages)
        
        # Get or create chat session
        session_id = request.user or "default"
        if session_id not in chat_sessions:
            chat_sessions[session_id] = gemini_client.start_chat(model=gemini_model)
        
        chat = chat_sessions[session_id]
        
        # Generate response
        response = await chat.send_message(prompt)
        
        # Handle streaming
        if request.stream:
            return StreamingResponse(
                stream_response(response.text, request.model, f"chatcmpl-{uuid.uuid4().hex[:8]}"),
                media_type="text/event-stream"
            )
        
        # Calculate tokens
        prompt_tokens = estimate_tokens(prompt)
        completion_tokens = estimate_tokens(response.text)
        
        # Format response
        return ChatCompletionResponse(
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=response.text),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def create_completion(request: Request):
    """Legacy completions endpoint - redirect to chat completions"""
    body = await request.json()
    
    # Convert to chat format
    messages = [Message(role="user", content=body.get("prompt", ""))]
    
    chat_request = ChatCompletionRequest(
        model=body.get("model", "gpt-3.5-turbo"),
        messages=messages,
        temperature=body.get("temperature", 0.7),
        max_tokens=body.get("max_tokens"),
        stream=body.get("stream", False)
    )
    
    return await create_chat_completion(chat_request)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "client_initialized": client is not None,
        "active_sessions": len(chat_sessions),
        "cookie_persistence": COOKIE_FILE.exists()
    }

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)