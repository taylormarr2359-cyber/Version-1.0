from __future__ import annotations

import asyncio
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from .config import (
    get_tts_provider,
    get_tts_rate,
    get_tts_style,
    get_tts_voice_name,
    get_tts_volume,
    get_voice_interruptible,
)


@dataclass
class VoiceSettings:
    rate: int = 155
    volume: float = 1.0
    preferred_gender: str = "male"
    preferred_voice_name: str = "en-US-ChristopherNeural"
    style: str = "calm_authoritative"
    provider: str = "cloud"
    interruptible: bool = True


class VoiceEngine:
    def __init__(self, settings: VoiceSettings | None = None) -> None:
        if settings is None:
            settings = VoiceSettings(
                rate=get_tts_rate(),
                volume=get_tts_volume(),
                preferred_voice_name=get_tts_voice_name(),
                style=get_tts_style(),
                provider=get_tts_provider(),
                interruptible=get_voice_interruptible(),
            )
        self.settings = settings
        self._engine = None
        self._speak_lock = threading.RLock()
        self._selected_local_voice_id: str | None = None

    def _pick_best_local_voice(self, voices) -> str | None:
        preferred = self.settings.preferred_voice_name.lower()
        ranked_hits: list[tuple[int, str]] = []
        deep_keywords = ("christopher", "guy", "davis", "david", "mark", "james", "male", "deep")
        for voice in voices:
            voice_name = (getattr(voice, "name", "") or "").lower()
            voice_id = (getattr(voice, "id", "") or "")
            score = 0
            if preferred and preferred in voice_name:
                score += 100
            if any(k in voice_name for k in deep_keywords):
                score += 50
            if "christopher" in voice_name or "guy" in voice_name:
                score += 35
            if "zira" in voice_name or "female" in voice_name:
                score -= 40
            if score > 0 and voice_id:
                ranked_hits.append((score, voice_id))
        if not ranked_hits:
            return None
        ranked_hits.sort(key=lambda x: x[0], reverse=True)
        return ranked_hits[0][1]

    def _init_engine(self) -> None:
        if self._engine is not None:
            return
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.settings.rate)
            self._engine.setProperty("volume", self.settings.volume)

            voices = self._engine.getProperty("voices") or []
            best_voice_id = self._pick_best_local_voice(voices)
            if best_voice_id:
                self._engine.setProperty("voice", best_voice_id)
                self._selected_local_voice_id = best_voice_id
        except Exception:
            self._engine = None

    def _style_to_edge_params(self) -> tuple[str, str]:
        style = self.settings.style.lower().strip()
        if "authoritative" in style or "deep" in style:
            return "-20%", "-2Hz"
        if "calm" in style:
            return "-12%", "-1Hz"
        return "-10%", "-1Hz"

    async def _edge_speak_async(self, text: str, output_file: Path) -> None:
        import edge_tts

        rate, pitch = self._style_to_edge_params()
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.settings.preferred_voice_name or "en-US-ChristopherNeural",
            rate=rate,
            pitch=pitch,
            volume="+0%",
        )
        await communicate.save(str(output_file))

    def _speak_cloud(self, text: str) -> bool:
        try:
            from playsound import playsound

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                temp_path = Path(tmp.name)

            asyncio.run(self._edge_speak_async(text, temp_path))
            playsound(str(temp_path))
            temp_path.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def stop(self) -> None:
        if self._engine is None:
            return
        try:
            self._engine.stop()
        except Exception:
            pass

    def speak(self, text: str) -> None:
        with self._speak_lock:
            if self.settings.interruptible:
                self.stop()

            if self.settings.provider == "cloud":
                if self._speak_cloud(text):
                    return

            self._init_engine()
            if self._engine is None:
                print(f"ATLAS (voice-fallback): {text}")
                return
            self._engine.say(text)
            self._engine.runAndWait()

    def diagnostics_text(self) -> str:
        selected = self._selected_local_voice_id or "auto/not-initialized"
        return (
            "Voice Diagnostics:\n"
            f"- provider: {self.settings.provider}\n"
            f"- preferred voice: {self.settings.preferred_voice_name}\n"
            f"- selected local voice: {selected}\n"
            f"- rate: {self.settings.rate}\n"
            f"- volume: {self.settings.volume}\n"
            f"- interruptible: {self.settings.interruptible}"
        )

    def speak_async(self, text: str) -> threading.Thread:
        worker = threading.Thread(target=self.speak, args=(text,), daemon=True)
        worker.start()
        return worker
