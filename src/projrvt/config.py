import os
from pathlib import Path
from typing import Literal


def _read_api_key_from_file(file_path: Path) -> str:
    if not file_path.exists():
        return ""
    text = file_path.read_text(encoding="utf-8").strip()
    return text


def load_anthropic_api_key() -> str:
    # Priority:
    # 1) ANTHROPIC_API_KEY env var
    # 2) ATLAS_API_KEY env var
    # 3) local api_key.txt in project root
    env_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ATLAS_API_KEY")
    if env_key:
        return env_key.strip()

    project_root = Path(__file__).resolve().parents[2]
    key_file = project_root / "api_key.txt"
    return _read_api_key_from_file(key_file)


def get_tts_provider() -> Literal["local", "cloud"]:
    provider = (os.getenv("ATLAS_TTS_PROVIDER", "local") or "local").strip().lower()
    return "cloud" if provider == "cloud" else "local"


def get_tts_voice_name() -> str:
    return (os.getenv("ATLAS_TTS_VOICE", "deep_male") or "deep_male").strip()


def get_tts_rate() -> int:
    raw = (os.getenv("ATLAS_TTS_RATE", "155") or "155").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 155
    return max(110, min(210, value))


def get_tts_volume() -> float:
    raw = (os.getenv("ATLAS_TTS_VOLUME", "1.0") or "1.0").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 1.0
    return max(0.0, min(1.0, value))


def get_tts_style() -> str:
    return (os.getenv("ATLAS_TTS_STYLE", "calm_authoritative") or "calm_authoritative").strip()


def get_voice_interruptible() -> bool:
    raw = (os.getenv("ATLAS_VOICE_INTERRUPTIBLE", "true") or "true").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def get_wake_word() -> str:
    return (os.getenv("ATLAS_WAKE_WORD", "atlas") or "atlas").strip().lower()


def get_voice_timeout_sec() -> float:
    raw = (os.getenv("ATLAS_VOICE_TIMEOUT_SEC", "4.0") or "4.0").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 4.0
    return max(1.0, min(30.0, value))


def get_api_host() -> str:
    return (os.getenv("ATLAS_API_HOST", "0.0.0.0") or "0.0.0.0").strip()


def get_api_port() -> int:
    raw = (os.getenv("ATLAS_API_PORT", "8000") or "8000").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 8000
    return max(1, min(65535, value))


def get_api_auth_key() -> str:
    return (os.getenv("ATLAS_API_AUTH_KEY", "") or "").strip()


def build_system_prompt() -> str:
    return (
        "You are ATLAS, a proactive, insightful personal assistant. "
        "Be concise, practical, and action-oriented. "
        "Offer next steps and optional automations when useful."
    )
