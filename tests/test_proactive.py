from projrvt.proactive import build_daily_briefing, build_insights


def test_daily_briefing_contains_wake_word_and_counts():
    text = build_daily_briefing(
        notes=["note one", "note two"],
        calendar_items=["standup at 9am"],
        wake_word="atlas",
    )
    assert "atlas" in text.lower()
    assert "calendar item(s)" in text
    assert "note(s)" in text


def test_insights_empty_memory():
    text = build_insights([])
    assert "No notable patterns yet" in text


def test_insights_detects_patterns():
    memory = [
        "User: weather boston",
        "User: weather seattle",
        "User: plan my day",
        "User: plan weekly roadmap",
        "User: notes add buy milk",
        "User: notes find milk",
    ]
    text = build_insights(memory)
    assert "daily forecast briefing" in text
    assert "daily priority plan" in text
    assert "weekly note summaries" in text
