from dataclasses import dataclass

from .config import get_wake_word
from .engine import AtlasEngine
from .integrations import IntegrationsHub
from .memory import ConversationMemory
from .observability import build_diagnostics_snapshot
from .proactive import build_daily_briefing, build_insights
from .security import redact_secrets
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
        self.voice_muted = False

    def handle(self, user_text: str, speak: bool = False) -> AssistantResult:
        lowered = user_text.strip().lower()

        if lowered in {"stop speaking", "stop voice", "silence"}:
            self.voice.stop()
            text = "Stopping speech now."
        elif lowered in {"mute", "mute voice"}:
            self.voice_muted = True
            text = "Voice output muted."
        elif lowered in {"unmute", "unmute voice"}:
            self.voice_muted = False
            text = "Voice output unmuted."
        elif lowered.startswith("plan "):
            objective = user_text.split(" ", 1)[1].strip()
            steps = self.engine.plan(objective)
            text = "Plan:\n" + "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])
        elif lowered.startswith("do "):
            objective = user_text.split(" ", 1)[1].strip()
            text = self.engine.execution_outline(objective)
        elif lowered.startswith("weather "):
            location = user_text.split(" ", 1)[1].strip()
            text = self.integrations.dispatch("weather", {"location": location}).message
        elif lowered in {"calendar", "calendar list"}:
            text = self.integrations.dispatch("calendar_list", {}).message
        elif lowered.startswith("calendar add "):
            raw = user_text.split(" ", 2)[2].strip()
            if "|" in raw:
                title, when = [p.strip() for p in raw.split("|", 1)]
            else:
                title, when = raw, ""
            text = self.integrations.dispatch("calendar_add", {"title": title, "when": when}).message
        elif lowered in {"email", "email list"}:
            text = self.integrations.dispatch("email_list", {}).message
        elif lowered.startswith("email send "):
            raw = user_text.split(" ", 2)[2].strip()
            parts = [p.strip() for p in raw.split("|")]
            to = parts[0] if len(parts) >= 1 else ""
            subject = parts[1] if len(parts) >= 2 else ""
            body = "|".join(parts[2:]).strip() if len(parts) >= 3 else ""
            text = self.integrations.dispatch("email_send", {"to": to, "subject": subject, "body": body}).message
        elif lowered in {"notes", "notes list"}:
            text = self.integrations.dispatch("notes_list", {}).message
        elif lowered.startswith("notes add "):
            note_text = user_text.split(" ", 2)[2].strip()
            text = self.integrations.dispatch("notes_add", {"text": note_text}).message
        elif lowered.startswith("notes find "):
            query = user_text.split(" ", 2)[2].strip()
            text = self.integrations.dispatch("notes_find", {"query": query}).message
        elif lowered in {"smart home", "smarthome", "smart home status"}:
            text = self.integrations.dispatch("smart_home_status", {}).message
        elif lowered.startswith("smart home set "):
            parts3 = user_text.split(" ", 3)
            raw = parts3[3].strip() if len(parts3) > 3 else ""
            parts = raw.split(" ", 1)
            device = parts[0].strip() if len(parts) >= 1 else ""
            value = parts[1].strip() if len(parts) >= 2 else ""
            text = self.integrations.dispatch("smart_home_set", {"device": device, "value": value}).message
        elif lowered in {"help", "commands"}:
            text = (
                "ATLAS Commands:\n"
                "- plan <objective>\n"
                "- do <objective>\n"
                "- weather <location>\n"
                "- calendar list | calendar add <title> | <when>\n"
                "- notes list | notes add <text> | notes find <query>\n"
                "- email list | email send <to> | <subject> | <body>\n"
                "- smart home status | smart home set <device> <value>\n"
                "- diagnostics | voice diagnostics\n"
                "- onboarding | briefing | insights\n"
                "- mute/unmute | stop speaking"
            )
        elif lowered == "onboarding":
            text = (
                "Welcome to ATLAS.\n"
                "Start with: 'plan my day', 'calendar add Team standup | 9am', "
                "'notes add Focus on deep work', and 'briefing'."
            )
        elif lowered == "briefing":
            text = build_daily_briefing(
                notes=self.memory.recent(10),
                calendar_items=[],
                wake_word=get_wake_word(),
            )
        elif lowered == "insights":
            text = build_insights(self.memory.recent(50))
        elif lowered == "voice diagnostics":
            text = self.voice.diagnostics_text()
        elif lowered == "diagnostics":
            snapshot = build_diagnostics_snapshot(
                memory_items=len(self.memory.recent(200)),
                voice_muted=self.voice_muted,
                wake_word=get_wake_word(),
            )
            text = redact_secrets(snapshot.to_text())
        else:
            memory_summary = self.memory.summary()
            engine_response = self.engine.reply(user_text, memory_summary)
            text = engine_response.text

        self.memory.add(f"User: {user_text}")
        self.memory.add(f"ATLAS: {text}")

        if speak and not self.voice_muted:
            self.voice.speak(text)
            return AssistantResult(text=text, spoken=True)

        return AssistantResult(text=text, spoken=False)
