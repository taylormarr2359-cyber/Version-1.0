from dataclasses import dataclass

from .engine import AtlasEngine
from .integrations import IntegrationsHub
from .memory import ConversationMemory
from .voice import VoiceEngine


@dataclass
class AssistantResult:
    text: str
    spoken: bool


class AtlasAssistant:
    def __init__(self) -> None:
        self.memory = ConversationMemory()
        self.engine = AtlasEngine()
        self.voice = VoiceEngine()
        self.integrations = IntegrationsHub()

    def handle(self, user_text: str, speak: bool = False) -> AssistantResult:
        lowered = user_text.strip().lower()

        if lowered.startswith("weather "):
            location = user_text.split(" ", 1)[1].strip()
            result = self.integrations.weather(location)
            text = result.message
        elif lowered == "calendar":
            text = self.integrations.calendar().message
        elif lowered == "email":
            text = self.integrations.email().message
        elif lowered == "notes":
            text = self.integrations.notes().message
        elif lowered in {"smart home", "smarthome"}:
            text = self.integrations.smart_home().message
        else:
            memory_summary = self.memory.summary()
            engine_response = self.engine.reply(user_text, memory_summary)
            text = engine_response.text

        self.memory.add(f"User: {user_text}")
        self.memory.add(f"ATLAS: {text}")

        if speak:
            self.voice.speak(text)
            return AssistantResult(text=text, spoken=True)

        return AssistantResult(text=text, spoken=False)
