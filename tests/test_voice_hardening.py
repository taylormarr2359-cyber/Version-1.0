from projrvt.voice import VoiceEngine, VoiceSettings


class _MockVoice:
    def __init__(self, name: str, voice_id: str) -> None:
        self.name = name
        self.id = voice_id


def test_pick_best_local_voice_prefers_deep_male():
    engine = VoiceEngine(
        VoiceSettings(
            preferred_voice_name="christopher",
            provider="local",
        )
    )
    voices = [
        _MockVoice("Microsoft Zira Desktop", "v1"),
        _MockVoice("Microsoft David Desktop", "v2"),
        _MockVoice("Christopher Neural", "v3"),
    ]
    chosen = engine._pick_best_local_voice(voices)
    assert chosen == "v3"


def test_voice_diagnostics_text_contains_core_fields():
    engine = VoiceEngine(VoiceSettings(provider="cloud", preferred_voice_name="en-US-ChristopherNeural"))
    diag = engine.diagnostics_text()
    assert "Voice Diagnostics" in diag
    assert "provider: cloud" in diag
    assert "preferred voice" in diag
