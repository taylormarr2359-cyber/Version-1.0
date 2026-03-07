from dataclasses import dataclass, field
from typing import List


@dataclass
class ConversationMemory:
    max_items: int = 20
    items: List[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        self.items.append(text)
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    def summary(self) -> str:
        if not self.items:
            return "No prior context."
        return " | ".join(self.items[-5:])
