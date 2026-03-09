from dataclasses import dataclass
import logging
from typing import Generator

import anthropic

from .config import build_system_prompt, load_anthropic_api_key

logger = logging.getLogger(__name__)


@dataclass
class EngineResponse:
    text: str
    used_live_llm: bool


class AtlasEngine:
    def __init__(self) -> None:
        self.api_key = load_anthropic_api_key()
        self.system_prompt = build_system_prompt()
        # Create the client once and reuse it for all calls.
        self._client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def _fallback_reply(self, user_text: str, memory_summary: str) -> str:
        return (
            "ATLAS fallback response:\n"
            f"- You said: {user_text}\n"
            f"- Recent context: {memory_summary}\n"
            "- Suggestion: define your next single priority and I will break it into steps."
        )

    def _build_context_block(self, user_text: str, memory_summary: str) -> str:
        if memory_summary and memory_summary != "No prior context.":
            return f"Recent context:\n{memory_summary}\n\nUser: {user_text}"
        return f"User: {user_text}"

    def plan(self, objective: str) -> list[str]:
        objective = (objective or "").strip() or "the requested objective"
        return [
            f"Clarify objective and constraints for: {objective}",
            "Break objective into concrete milestones.",
            "Execute first milestone now and report progress.",
            "Review outcomes and iterate with optimizations.",
        ]

    def execution_outline(self, objective: str) -> str:
        steps = self.plan(objective)
        rendered = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])
        return f"Execution outline:\n{rendered}"

    def reply(self, user_text: str, memory_summary: str) -> EngineResponse:
        if not self._client:
            return EngineResponse(
                text=self._fallback_reply(user_text, memory_summary),
                used_live_llm=False,
            )

        try:
            with self._client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": self._build_context_block(user_text, memory_summary),
                    }
                ],
            ) as stream:
                message = stream.get_final_message()
            text = next(
                (block.text for block in message.content if hasattr(block, "text")),
                "",
            )
            return EngineResponse(text=text.strip(), used_live_llm=True)
        except Exception as exc:
            logger.warning("LLM call failed (%s: %s), using fallback.", type(exc).__name__, exc)
            return EngineResponse(
                text=self._fallback_reply(user_text, memory_summary),
                used_live_llm=False,
            )

    def reply_stream(self, user_text: str, memory_summary: str) -> Generator[str, None, None]:
        """Yield Claude response text chunk by chunk. Yields one chunk on fallback."""
        if not self._client:
            yield self._fallback_reply(user_text, memory_summary)
            return

        try:
            with self._client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": self._build_context_block(user_text, memory_summary),
                    }
                ],
            ) as stream:
                for token in stream.text_stream:
                    yield token
        except Exception as exc:
            logger.warning("LLM stream failed (%s: %s), using fallback.", type(exc).__name__, exc)
            yield self._fallback_reply(user_text, memory_summary)
