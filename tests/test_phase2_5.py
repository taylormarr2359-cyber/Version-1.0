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
