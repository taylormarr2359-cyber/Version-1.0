from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class BlackboxAPIConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: int = 45


class BlackboxAPIError(RuntimeError):
    pass


def load_blackbox_config() -> BlackboxAPIConfig:
    """
    Load provider config (OpenAI-first, Blackbox-compatible fallback).

    Preferred env:
      - OPENAI_API_BASE_URL   (optional, default: https://api.openai.com/v1)
      - OPENAI_API_KEY        (preferred)
      - OPENAI_MODEL          (optional, default: gpt-4o-mini)
      - OPENAI_TIMEOUT        (optional, default: 45)

    Legacy fallback env (still supported):
      - BLACKBOX_API_BASE_URL
      - BLACKBOX_API_KEY
      - BLACKBOX_MODEL
      - BLACKBOX_TIMEOUT
    """
    base_url = (
        (os.getenv("OPENAI_API_BASE_URL") or "").strip()
        or (os.getenv("BLACKBOX_API_BASE_URL") or "").strip()
        or "https://api.openai.com/v1"
    )
    api_key = (
        (os.getenv("OPENAI_API_KEY") or "").strip()
        or (os.getenv("BLACKBOX_API_KEY") or "").strip()
    )
    model = (
        (os.getenv("OPENAI_MODEL") or "").strip()
        or (os.getenv("BLACKBOX_MODEL") or "").strip()
        or "gpt-4o-mini"
    )

    timeout_raw = (
        (os.getenv("OPENAI_TIMEOUT") or "").strip()
        or (os.getenv("BLACKBOX_TIMEOUT") or "").strip()
        or "45"
    )
    try:
        timeout_seconds = max(5, int(timeout_raw))
    except Exception:
        timeout_seconds = 45

    if "example.com" in base_url.lower():
        raise BlackboxAPIError(
            "API base URL is using a placeholder host (example.com). "
            "Set OPENAI_API_BASE_URL (or BLACKBOX_API_BASE_URL) to a real host."
        )
    if not api_key:
        raise BlackboxAPIError(
            "Missing API key. Set OPENAI_API_KEY (preferred) or BLACKBOX_API_KEY."
        )

    return BlackboxAPIConfig(
        base_url=base_url.rstrip("/"),
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )


def build_chat_payload(user_prompt: str, system_prompt: str | None = None, model: str = "") -> dict[str, Any]:
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
    }
    return payload


def call_blackbox_chat(
    user_prompt: str,
    *,
    system_prompt: str | None = None,
    endpoint_path: str = "/chat/completions",
) -> str:
    """
    Generic BLACKBOX chat API call template.

    User should insert/adjust endpoint/auth/header/body format here if provider differs.
    """
    cfg = load_blackbox_config()
    url = f"{cfg.base_url}{endpoint_path}"

    payload = build_chat_payload(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model=cfg.model,
    )

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=cfg.timeout_seconds)
    except requests.RequestException as exc:
        raise BlackboxAPIError(f"BLACKBOX request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise BlackboxAPIError(f"Provider API HTTP {resp.status_code} at {url}: {resp.text}")

    try:
        data = resp.json()
    except Exception as exc:
        raise BlackboxAPIError("Provider API returned non-JSON response.") from exc

    # OpenAI-compatible parse path
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        # Fallback to raw JSON string if schema differs.
        return str(data)
