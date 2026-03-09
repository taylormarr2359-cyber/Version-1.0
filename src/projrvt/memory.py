import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ConversationMemory:
    max_items: int = 20
    items: List[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        self.items.append(text)
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    def recent(self, n: int = 5) -> List[str]:
        n = max(1, n)
        return self.items[-n:]

    def relevant(self, query: str, top_k: int = 3) -> List[str]:
        if not self.items:
            return []
        tokens = {t for t in query.lower().split() if t}
        scored: list[tuple[int, str]] = []
        for item in self.items:
            lowered = item.lower()
            score = sum(1 for t in tokens if t in lowered)
            if "user:" in lowered:
                score += 1
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[: max(1, top_k)]]

    def proactive_insights(self) -> List[str]:
        if not self.items:
            return ["No historical signals yet."]
        tail = " ".join(self.recent(8)).lower()
        insights: list[str] = []
        if "plan" in tail or "schedule" in tail:
            insights.append("Offer a time-blocked plan and optional reminders.")
        if "email" in tail:
            insights.append("Offer to draft and prioritize outbound emails.")
        if "weather" in tail or "commute" in tail:
            insights.append("Offer commute-aware schedule adjustments.")
        if not insights:
            insights.append("Suggest next best action for current priority.")
        return insights

    def summary(self) -> str:
        if not self.items:
            return "No prior context."
        return " | ".join(self.recent(5))

    def save(self, path: Path) -> None:
        """Persist memory items to a JSON file. Silently ignores write errors."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.items, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load(self, path: Path) -> None:
        """Load memory items from a JSON file. Silently ignores missing/corrupt files."""
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self.items = [str(x) for x in data][-self.max_items :]
        except Exception:
            pass
