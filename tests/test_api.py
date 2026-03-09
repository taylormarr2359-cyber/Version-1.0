"""Tests for the ATLAS FastAPI REST API layer."""
from unittest.mock import MagicMock, patch

import pytest

# FastAPI TestClient requires httpx
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

import projrvt.api as _api_mod  # noqa: E402
from projrvt.api import app, _get_assistant  # noqa: E402
from projrvt.assistant import AssistantResult  # noqa: E402
from projrvt.integrations import IntegrationResult, IntegrationsHub  # noqa: E402

client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True)
def isolated_api_data(tmp_path):
    """Each API test gets a fresh assistant backed by an isolated temp directory.

    This prevents tests from writing to the real atlas_data/ files.
    IntegrationsHub is patched to use tmp_path; the API singleton is reset so
    every test constructs a new AtlasAssistant that picks up the patch.
    """
    _api_mod._assistant = None  # force fresh assistant on next request

    def _hub_init(self):
        self._data_dir = tmp_path
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._calendar_file = tmp_path / "calendar.json"
        self._notes_file = tmp_path / "notes.json"
        self._email_file = tmp_path / "email_outbox.json"
        self._smart_home_file = tmp_path / "smart_home.json"

    with patch.object(IntegrationsHub, "__init__", _hub_init):
        yield

    _api_mod._assistant = None  # clean up after test


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "wake_word" in body


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
def test_chat_help_command():
    resp = client.post("/chat", json={"message": "help"})
    assert resp.status_code == 200
    body = resp.json()
    assert "response" in body
    assert len(body["response"]) > 0
    assert isinstance(body["spoken"], bool)


def test_chat_fallback_no_key():
    """Without an API key the engine returns a static fallback — no HTTP error."""
    resp = client.post("/chat", json={"message": "What is the meaning of life?"})
    assert resp.status_code == 200
    assert "response" in resp.json()


def test_chat_mute_command():
    resp = client.post("/chat", json={"message": "mute"})
    assert resp.status_code == 200
    assert "muted" in resp.json()["response"].lower()


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------
def test_calendar_list():
    resp = client.get("/calendar")
    assert resp.status_code == 200
    assert "ok" in resp.json()


def test_calendar_add_and_list():
    add = client.post("/calendar", json={"title": "API test event", "when": "5pm"})
    assert add.status_code == 200
    assert add.json()["ok"] is True

    listing = client.get("/calendar")
    assert "API test event" in listing.json()["message"]


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
def test_notes_list():
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert "ok" in resp.json()


def test_notes_add_and_search():
    unique = "api_layer_test_note_xyz"
    add = client.post("/notes", json={"text": unique})
    assert add.status_code == 200
    assert add.json()["ok"] is True

    search = client.get("/notes/search", params={"q": "api_layer_test"})
    assert search.status_code == 200
    assert unique in search.json()["message"]


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
def test_email_list():
    resp = client.get("/email")
    assert resp.status_code == 200
    assert "ok" in resp.json()


def test_email_send():
    resp = client.post(
        "/email",
        json={"to": "test@example.com", "subject": "Hello", "body": "Test body."},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# Smart home
# ---------------------------------------------------------------------------
def test_smart_home_status():
    resp = client.get("/smart-home")
    assert resp.status_code == 200
    assert "lights" in resp.json()["message"]


def test_smart_home_set():
    resp = client.post("/smart-home", json={"device": "lights", "value": "on"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_smart_home_set_invalid_device():
    resp = client.post("/smart-home", json={"device": "oven", "value": "500"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


# ---------------------------------------------------------------------------
# Briefing / insights / diagnostics
# ---------------------------------------------------------------------------
def test_briefing_returns_message():
    resp = client.get("/briefing")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_insights_returns_message():
    resp = client.get("/insights")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_diagnostics_returns_message():
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    assert "message" in resp.json()


# ---------------------------------------------------------------------------
# Auth: when ATLAS_API_AUTH_KEY is set, unauthenticated requests are rejected
# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------
def test_chat_stream_returns_event_stream():
    """POST /chat/stream must return SSE content-type and emit a done event."""
    with client.stream("POST", "/chat/stream", json={"message": "help"}) as resp:
        assert resp.status_code == 200
        ct = resp.headers.get("content-type", "")
        assert "text/event-stream" in ct
        lines = list(resp.iter_lines())
    combined = "\n".join(lines)
    assert "data:" in combined
    assert '"done": true' in combined or '"done":true' in combined


def test_chat_stream_yields_token():
    """Structured command must emit at least one token chunk."""
    with client.stream("POST", "/chat/stream", json={"message": "mute"}) as resp:
        lines = list(resp.iter_lines())
    combined = "\n".join(lines)
    assert '"token"' in combined


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def test_auth_blocks_unauthenticated(monkeypatch):
    monkeypatch.setenv("ATLAS_API_AUTH_KEY", "secret-test-key")

    # Reload auth key by patching the function used by the dependency
    with patch("projrvt.api.get_api_auth_key", return_value="secret-test-key"):
        resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 401


def test_auth_allows_valid_bearer(monkeypatch):
    monkeypatch.setenv("ATLAS_API_AUTH_KEY", "secret-test-key")

    with patch("projrvt.api.get_api_auth_key", return_value="secret-test-key"):
        resp = client.post(
            "/chat",
            json={"message": "help"},
            headers={"Authorization": "Bearer secret-test-key"},
        )
    assert resp.status_code == 200
