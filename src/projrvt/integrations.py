from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class IntegrationResult:
    ok: bool
    message: str


class IntegrationsHub:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self._data_dir = project_root / "atlas_data"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._calendar_file = self._data_dir / "calendar.json"
        self._notes_file = self._data_dir / "notes.json"
        self._email_file = self._data_dir / "email_outbox.json"
        self._smart_home_file = self._data_dir / "smart_home.json"

    def _read_json(self, file_path: Path, default: Any) -> Any:
        if not file_path.exists():
            return default
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _write_json(self, file_path: Path, value: Any) -> None:
        file_path.write_text(json.dumps(value, indent=2), encoding="utf-8")

    def weather(self, location: str) -> IntegrationResult:
        now = datetime.now().strftime("%H:%M")
        clean_location = (location or "").strip() or "your area"
        return IntegrationResult(
            ok=True,
            message=f"[{now}] Weather integration placeholder for {clean_location}.",
        )

    def calendar(self) -> IntegrationResult:
        return self.calendar_list()

    def calendar_list(self) -> IntegrationResult:
        events = self._read_json(self._calendar_file, [])
        if not events:
            return IntegrationResult(ok=True, message="Calendar is empty.")
        lines = ["Upcoming events:"]
        for idx, event in enumerate(events[-10:], start=1):
            lines.append(f"{idx}. {event.get('title', 'Untitled')} @ {event.get('when', 'unspecified')}")
        return IntegrationResult(ok=True, message="\n".join(lines))

    def calendar_delete(self, index: str) -> IntegrationResult:
        events = self._read_json(self._calendar_file, [])
        try:
            idx = int(index) - 1
            if not (0 <= idx < len(events)):
                raise IndexError
        except (ValueError, IndexError):
            return IntegrationResult(ok=False, message=f"calendar delete: no event at position {index}.")
        removed = events.pop(idx)
        self._write_json(self._calendar_file, events)
        return IntegrationResult(ok=True, message=f"Deleted event: {removed.get('title', '')} @ {removed.get('when', '')}")

    def calendar_add(self, title: str, when: str) -> IntegrationResult:
        clean_title = (title or "").strip()
        clean_when = (when or "").strip()
        if not clean_title or not clean_when:
            return IntegrationResult(ok=False, message="calendar add requires: <title> | <when>")
        events = self._read_json(self._calendar_file, [])
        events.append(
            {
                "title": clean_title,
                "when": clean_when,
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
        )
        self._write_json(self._calendar_file, events)
        return IntegrationResult(ok=True, message=f"Added calendar event: {clean_title} @ {clean_when}")

    def email(self) -> IntegrationResult:
        return self.email_list()

    def email_list(self) -> IntegrationResult:
        outbox = self._read_json(self._email_file, [])
        if not outbox:
            return IntegrationResult(ok=True, message="Email outbox is empty.")
        lines = ["Email outbox:"]
        for idx, item in enumerate(outbox[-10:], start=1):
            lines.append(
                f"{idx}. To={item.get('to','?')} Subject={item.get('subject','(no subject)')} Status={item.get('status','queued')}"
            )
        return IntegrationResult(ok=True, message="\n".join(lines))

    def email_send(self, to: str, subject: str, body: str) -> IntegrationResult:
        clean_to = (to or "").strip()
        clean_subject = (subject or "").strip()
        clean_body = (body or "").strip()
        if not clean_to or not clean_subject or not clean_body:
            return IntegrationResult(ok=False, message="email send requires: <to> | <subject> | <body>")
        outbox = self._read_json(self._email_file, [])
        outbox.append(
            {
                "to": clean_to,
                "subject": clean_subject,
                "body": clean_body,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
        )
        self._write_json(self._email_file, outbox)
        return IntegrationResult(ok=True, message=f"Queued email to {clean_to} with subject '{clean_subject}'.")

    def notes(self) -> IntegrationResult:
        return self.notes_list()

    def notes_list(self) -> IntegrationResult:
        notes = self._read_json(self._notes_file, [])
        if not notes:
            return IntegrationResult(ok=True, message="No saved notes.")
        lines = ["Notes:"]
        for idx, note in enumerate(notes[-15:], start=1):
            lines.append(f"{idx}. {note.get('text', '')}")
        return IntegrationResult(ok=True, message="\n".join(lines))

    def notes_add(self, text: str) -> IntegrationResult:
        clean_text = (text or "").strip()
        if not clean_text:
            return IntegrationResult(ok=False, message="notes add requires text.")
        notes = self._read_json(self._notes_file, [])
        notes.append({"text": clean_text, "created_at": datetime.utcnow().isoformat() + "Z"})
        self._write_json(self._notes_file, notes)
        return IntegrationResult(ok=True, message="Note saved.")

    def notes_delete(self, index: str) -> IntegrationResult:
        notes = self._read_json(self._notes_file, [])
        try:
            idx = int(index) - 1
            if not (0 <= idx < len(notes)):
                raise IndexError
        except (ValueError, IndexError):
            return IntegrationResult(ok=False, message=f"notes delete: no note at position {index}.")
        removed = notes.pop(idx)
        self._write_json(self._notes_file, notes)
        return IntegrationResult(ok=True, message=f"Deleted note: {removed.get('text', '')}")

    def notes_find(self, query: str) -> IntegrationResult:
        clean_query = (query or "").strip().lower()
        if not clean_query:
            return IntegrationResult(ok=False, message="notes find requires a query.")
        notes = self._read_json(self._notes_file, [])
        matches = [n for n in notes if clean_query in str(n.get("text", "")).lower()]
        if not matches:
            return IntegrationResult(ok=True, message="No matching notes found.")
        lines = [f"Matches for '{query}':"]
        for idx, note in enumerate(matches[:15], start=1):
            lines.append(f"{idx}. {note.get('text', '')}")
        return IntegrationResult(ok=True, message="\n".join(lines))

    def smart_home(self) -> IntegrationResult:
        return self.smart_home_status()

    def smart_home_status(self) -> IntegrationResult:
        state = self._read_json(self._smart_home_file, {"lights": "off", "thermostat": "70", "locks": "locked"})
        lines = [
            "Smart home status:",
            f"- lights: {state.get('lights', 'off')}",
            f"- thermostat: {state.get('thermostat', '70')}",
            f"- locks: {state.get('locks', 'locked')}",
        ]
        return IntegrationResult(ok=True, message="\n".join(lines))

    def smart_home_set(self, device: str, value: str) -> IntegrationResult:
        clean_device = (device or "").strip().lower()
        clean_value = (value or "").strip().lower()
        allowed = {"lights", "thermostat", "locks"}
        if clean_device not in allowed:
            return IntegrationResult(ok=False, message="smart home set requires device in: lights, thermostat, locks")
        if not clean_value:
            return IntegrationResult(ok=False, message="smart home set requires a value.")
        state = self._read_json(self._smart_home_file, {"lights": "off", "thermostat": "70", "locks": "locked"})
        state[clean_device] = clean_value
        self._write_json(self._smart_home_file, state)
        return IntegrationResult(ok=True, message=f"Updated {clean_device} to {clean_value}.")

    def dispatch(self, action: str, payload: dict | None = None) -> IntegrationResult:
        payload = payload or {}
        normalized = (action or "").strip().lower().replace("-", "_").replace(" ", "_")

        if normalized == "weather":
            return self.weather(str(payload.get("location", "")))

        if normalized in {"calendar", "calendar_list"}:
            return self.calendar_list()
        if normalized == "calendar_add":
            return self.calendar_add(str(payload.get("title", "")), str(payload.get("when", "")))
        if normalized == "calendar_delete":
            return self.calendar_delete(str(payload.get("index", "")))

        if normalized in {"email", "email_list"}:
            return self.email_list()
        if normalized == "email_send":
            return self.email_send(
                str(payload.get("to", "")),
                str(payload.get("subject", "")),
                str(payload.get("body", "")),
            )

        if normalized in {"notes", "notes_list"}:
            return self.notes_list()
        if normalized == "notes_add":
            return self.notes_add(str(payload.get("text", "")))
        if normalized == "notes_find":
            return self.notes_find(str(payload.get("query", "")))
        if normalized == "notes_delete":
            return self.notes_delete(str(payload.get("index", "")))

        if normalized in {"smart_home", "smarthome", "smart_home_status"}:
            return self.smart_home_status()
        if normalized == "smart_home_set":
            return self.smart_home_set(str(payload.get("device", "")), str(payload.get("value", "")))

        return IntegrationResult(
            ok=False,
            message="Unsupported action: "
            f"{action}. Available: weather, calendar_list/calendar_add, email_list/email_send, "
            "notes_list/notes_add/notes_find, smart_home_status/smart_home_set.",
        )
