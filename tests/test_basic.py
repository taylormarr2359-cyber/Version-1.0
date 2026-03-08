from projrvt.assistant import AtlasAssistant
from projrvt.config import get_voice_interruptible, get_voice_timeout_sec, get_wake_word
from projrvt.main import hello
from projrvt.voice import VoiceEngine, VoiceSettings


def test_hello():
    assert hello("Alice") == "Hello, Alice!"


def test_assistant_fallback_or_live():
    assistant = AtlasAssistant()
    result = assistant.handle("Help me plan today", speak=False)
    assert isinstance(result.text, str)
    assert len(result.text) > 0


def test_voice_engine_constructs_with_settings():
    engine = VoiceEngine(
        VoiceSettings(
            rate=150,
            volume=0.9,
            preferred_voice_name="david",
            provider="local",
        )
    )
    assert engine is not None


def test_assistant_voice_mute_unmute_commands():
    assistant = AtlasAssistant()

    muted = assistant.handle("mute", speak=False)
    assert muted.text == "Voice output muted."
    assert assistant.voice_muted is True

    unmuted = assistant.handle("unmute", speak=False)
    assert unmuted.text == "Voice output unmuted."
    assert assistant.voice_muted is False


def test_assistant_stop_speaking_command():
    assistant = AtlasAssistant()
    result = assistant.handle("stop speaking", speak=False)
    assert result.text == "Stopping speech now."
    assert result.spoken is False


def test_config_voice_runtime_defaults(monkeypatch):
    monkeypatch.delenv("ATLAS_VOICE_INTERRUPTIBLE", raising=False)
    monkeypatch.delenv("ATLAS_WAKE_WORD", raising=False)
    monkeypatch.delenv("ATLAS_VOICE_TIMEOUT_SEC", raising=False)

    assert get_voice_interruptible() is True
    assert get_wake_word() == "atlas"
    assert get_voice_timeout_sec() == 4.0
