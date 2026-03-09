from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class DiagnosticsSnapshot:
    utc_time: str
    memory_items: int
    voice_muted: bool
    wake_word: str
    integrations_data_dir: str
    integrations_store_files_ok: bool
    api_key_loaded: bool

    def to_text(self) -> str:
        return "\n".join(
            [
                "Diagnostics:",
                f"- utc_time: {self.utc_time}",
                f"- memory_items: {self.memory_items}",
                f"- voice_muted: {self.voice_muted}",
                f"- wake_word: {self.wake_word}",
                f"- api_key_loaded: {self.api_key_loaded}",
                f"- integrations_data_dir: {self.integrations_data_dir}",
                f"- integrations_store_files_ok: {self.integrations_store_files_ok}",
            ]
        )


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_diagnostics_snapshot(
    *,
    memory_items: int,
    voice_muted: bool,
    wake_word: str,
    api_key_loaded: bool = False,
) -> DiagnosticsSnapshot:
    data_dir = _project_root() / "atlas_data"
    # Data files are created lazily on first write; only check the directory exists.
    files_ok = data_dir.exists()

    return DiagnosticsSnapshot(
        utc_time=datetime.utcnow().isoformat() + "Z",
        memory_items=memory_items,
        voice_muted=voice_muted,
        wake_word=wake_word,
        api_key_loaded=api_key_loaded,
        integrations_data_dir=str(data_dir),
        integrations_store_files_ok=files_ok,
    )
