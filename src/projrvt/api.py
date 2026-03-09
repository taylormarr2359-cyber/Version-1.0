"""FastAPI REST API for ATLAS — enables Android/cross-platform access and sync.

All data lives on the server (atlas_data/); clients read and write through
this API, which provides automatic multi-device synchronization.

Run with:
    python -m projrvt.serve
"""
from __future__ import annotations

import asyncio
import json as _json
import pathlib
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .assistant import AtlasAssistant
from .config import get_api_auth_key, get_wake_word

# ---------------------------------------------------------------------------
# Singleton assistant — shared across all requests
# ---------------------------------------------------------------------------
_assistant: Optional[AtlasAssistant] = None


def _get_assistant() -> AtlasAssistant:
    global _assistant
    if _assistant is None:
        _assistant = AtlasAssistant()
    return _assistant


# ---------------------------------------------------------------------------
# Optional Bearer-token auth
# ---------------------------------------------------------------------------
def _check_auth(authorization: Optional[str] = Header(default=None)) -> None:
    required_key = get_api_auth_key()
    if not required_key:
        return  # auth disabled
    if authorization != f"Bearer {required_key}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    speak: bool = False


class ChatResponse(BaseModel):
    response: str
    spoken: bool


class CalendarAddRequest(BaseModel):
    title: str
    when: str


class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str


class NoteAddRequest(BaseModel):
    text: str


class SmartHomeSetRequest(BaseModel):
    device: str
    value: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ATLAS API",
    version="1.0.0",
    description="Cross-platform REST API for the ATLAS personal assistant.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the PWA static files at /static and / (index.html)
_STATIC_DIR = pathlib.Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    index = _STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return FileResponse(str(index))  # will 404 naturally if missing


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "wake_word": get_wake_word()}


@app.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> StreamingResponse:
    """Server-Sent Events endpoint — yields tokens as they arrive from the LLM."""

    async def _event_stream():
        loop = asyncio.get_event_loop()
        gen = assistant.handle_stream(req.message)
        _stop = object()
        while True:
            chunk = await loop.run_in_executor(None, next, gen, _stop)
            if chunk is _stop:
                break
            yield f"data: {_json.dumps({'token': chunk})}\n\n"
        yield f"data: {_json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> ChatResponse:
    result = assistant.handle(req.message, speak=req.speak)
    return ChatResponse(response=result.text, spoken=result.spoken)


@app.get("/calendar")
async def calendar_list(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.calendar_list()
    return {"ok": result.ok, "message": result.message}


@app.post("/calendar")
async def calendar_add(
    req: CalendarAddRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.calendar_add(req.title, req.when)
    return {"ok": result.ok, "message": result.message}


@app.get("/email")
async def email_list(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.email_list()
    return {"ok": result.ok, "message": result.message}


@app.post("/email")
async def email_send(
    req: EmailSendRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.email_send(req.to, req.subject, req.body)
    return {"ok": result.ok, "message": result.message}


@app.get("/notes")
async def notes_list(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.notes_list()
    return {"ok": result.ok, "message": result.message}


@app.post("/notes")
async def notes_add(
    req: NoteAddRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.notes_add(req.text)
    return {"ok": result.ok, "message": result.message}


@app.get("/notes/search")
async def notes_search(
    q: str = "",
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.notes_find(q)
    return {"ok": result.ok, "message": result.message}


@app.get("/smart-home")
async def smart_home_status(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.smart_home_status()
    return {"ok": result.ok, "message": result.message}


@app.post("/smart-home")
async def smart_home_set(
    req: SmartHomeSetRequest,
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.integrations.smart_home_set(req.device, req.value)
    return {"ok": result.ok, "message": result.message}


@app.get("/briefing")
async def briefing(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.handle("briefing")
    return {"message": result.text}


@app.get("/insights")
async def insights(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.handle("insights")
    return {"message": result.text}


@app.get("/diagnostics")
async def diagnostics(
    assistant: AtlasAssistant = Depends(_get_assistant),
    _: None = Depends(_check_auth),
) -> dict:
    result = assistant.handle("diagnostics")
    return {"message": result.text}
