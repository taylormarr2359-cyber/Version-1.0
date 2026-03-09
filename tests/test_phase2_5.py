import pathlib

from projrvt.assistant import AtlasAssistant
from projrvt.engine import AtlasEngine
from projrvt.integrations import IntegrationsHub
from projrvt.memory import ConversationMemory


def test_memory_recent_retrieval_and_summary():
    mem = ConversationMemory(max_items=10)
    mem.add("User: plan gym and meals")
    mem.add("ATLAS: draft schedule")
    mem.add("User: prioritize deep work")
    mem.add("ATLAS: block morning focus")

    summary = mem.summary()
    assert "deep work" in summary or "focus" in summary


def test_integrations_dispatch_weather():
    hub = IntegrationsHub()
    result = hub.dispatch("weather", {"location": "Seattle"})
    assert result.ok is True
    assert "Seattle" in result.message


def test_integrations_dispatch_unknown():
    hub = IntegrationsHub()
    result = hub.dispatch("unknown_action", {})
    assert result.ok is False
    assert "Unsupported action" in result.message


def test_engine_plan_generation_shape():
    engine = AtlasEngine()
    plan = engine.plan("prepare for monday meeting")
    assert isinstance(plan, list)
    assert len(plan) >= 3


def test_assistant_plan_command():
    assistant = AtlasAssistant()
    result = assistant.handle("plan prepare for monday meeting", speak=False)
    assert "Plan:" in result.text


def test_assistant_do_command():
    assistant = AtlasAssistant()
    result = assistant.handle("do prepare for monday meeting", speak=False)
    assert "Execution outline" in result.text


def test_memory_save_and_load(tmp_path):
    mem = ConversationMemory(max_items=10)
    mem.add("User: hello")
    mem.add("ATLAS: hi there")

    path = tmp_path / "memory.json"
    mem.save(path)
    assert path.exists()

    mem2 = ConversationMemory(max_items=10)
    mem2.load(path)
    assert "User: hello" in mem2.items
    assert "ATLAS: hi there" in mem2.items


def test_memory_load_missing_file(tmp_path):
    mem = ConversationMemory()
    mem.load(tmp_path / "nonexistent.json")  # must not raise
    assert mem.items == []


def test_memory_load_corrupt_file(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json!!!", encoding="utf-8")
    mem = ConversationMemory()
    mem.load(bad)  # must not raise
    assert mem.items == []


def test_assistant_handle_stream_structured():
    """Structured command yields one chunk (non-empty) via handle_stream."""
    assistant = AtlasAssistant()
    chunks = list(assistant.handle_stream("mute"))
    assert len(chunks) == 1
    assert "muted" in chunks[0].lower()


def test_assistant_handle_stream_llm_fallback():
    """Without an API key the LLM fallback yields at least one non-empty chunk."""
    assistant = AtlasAssistant()
    chunks = list(assistant.handle_stream("tell me something interesting"))
    assert len(chunks) >= 1
    assert any(c.strip() for c in chunks)
