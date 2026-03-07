from projrvt.assistant import AtlasAssistant
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
