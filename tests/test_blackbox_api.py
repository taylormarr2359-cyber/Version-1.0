import os

import pytest

from projrvt.providers.blackbox_api import (
    BlackboxAPIError,
    build_chat_payload,
    load_blackbox_config,
    call_blackbox_chat,
)


def test_build_chat_payload_with_system_prompt():
    payload = build_chat_payload("hello", system_prompt="you are atlas", model="m1")
    assert payload["model"] == "m1"
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][0]["content"] == "you are atlas"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "hello"


def test_build_chat_payload_without_system_prompt():
    payload = build_chat_payload("hello", system_prompt=None, model="m1")
    assert payload["model"] == "m1"
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "hello"


def test_load_blackbox_config_defaults_to_openai_base_url(monkeypatch):
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)
    monkeypatch.delenv("BLACKBOX_API_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    cfg = load_blackbox_config()
    assert cfg.base_url == "https://api.openai.com/v1"


def test_load_blackbox_config_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("BLACKBOX_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
    with pytest.raises(BlackboxAPIError):
        load_blackbox_config()


def test_load_blackbox_config_timeout_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://api.test.local")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("OPENAI_TIMEOUT", "abc")
    cfg = load_blackbox_config()
    assert cfg.timeout_seconds == 45


class DummyResponse:
    def __init__(self, status_code=200, text="", json_data=None, json_raises=False):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("bad json")
        return self._json_data


def _set_required_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://api.test.local")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("OPENAI_MODEL", "m1")


def test_call_blackbox_chat_happy_path(monkeypatch):
    _set_required_env(monkeypatch)

    def fake_post(url, json, headers, timeout):
        assert url == "https://api.test.local/chat/completions"
        assert json["model"] == "m1"
        return DummyResponse(
            status_code=200,
            json_data={"choices": [{"message": {"content": "ok"}}]},
        )

    import projrvt.providers.blackbox_api as mod

    monkeypatch.setattr(mod.requests, "post", fake_post)
    out = call_blackbox_chat("hi")
    assert out == "ok"


def test_call_blackbox_chat_http_error(monkeypatch):
    _set_required_env(monkeypatch)

    def fake_post(url, json, headers, timeout):
        return DummyResponse(status_code=500, text="server err")

    import projrvt.providers.blackbox_api as mod

    monkeypatch.setattr(mod.requests, "post", fake_post)
    with pytest.raises(BlackboxAPIError):
        call_blackbox_chat("hi")


def test_call_blackbox_chat_non_json(monkeypatch):
    _set_required_env(monkeypatch)

    def fake_post(url, json, headers, timeout):
        return DummyResponse(status_code=200, json_raises=True)

    import projrvt.providers.blackbox_api as mod

    monkeypatch.setattr(mod.requests, "post", fake_post)
    with pytest.raises(BlackboxAPIError):
        call_blackbox_chat("hi")


def test_call_blackbox_chat_schema_fallback(monkeypatch):
    _set_required_env(monkeypatch)

    def fake_post(url, json, headers, timeout):
        return DummyResponse(status_code=200, json_data={"answer": "x"})

    import projrvt.providers.blackbox_api as mod

    monkeypatch.setattr(mod.requests, "post", fake_post)
    out = call_blackbox_chat("hi")
    assert "answer" in out


def test_call_blackbox_chat_request_exception(monkeypatch):
    _set_required_env(monkeypatch)

    import projrvt.providers.blackbox_api as mod

    def fake_post(url, json, headers, timeout):
        raise mod.requests.RequestException("boom")

    monkeypatch.setattr(mod.requests, "post", fake_post)
    with pytest.raises(BlackboxAPIError):
        call_blackbox_chat("hi")
