from dataclasses import dataclass
from typing import Generator

import anthropic

from .config import build_system_prompt, load_anthropic_api_key


@dataclass
class EngineResponse:
    text: str
    used_live_llm: bool


class AtlasEngine:
    def __init__(self) -> None:
        self.api_key = load_anthropic_api_key()
        self.system_prompt = build_system_prompt()

    def _fallback_reply(self, user_text: str, memory_summary: str) -> str:
        return (
            "ATLAS fallback response:\n"
            f"- You said: {user_text}\n"
            f"- Recent context: {memory_summary}\n"
            "- Suggestion: define your next single priority and I will break it into steps."
        )

    def _build_context_block(self, user_text: str, memory_summary: str) -> str:
        return f"Context: {memory_summary}\nUser: {user_text}"

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
        # If no key, fallback quickly.
        if not self.api_key:
            return EngineResponse(
                text=self._fallback_reply(user_text, memory_summary),
                used_live_llm=False,
            )

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            with client.messages.stream(
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
        except Exception:
            return EngineResponse(
                text=self._fallback_reply(user_text, memory_summary),
                used_live_llm=False,
            )

    def reply_stream(self, user_text: str, memory_summary: str) -> Generator[str, None, None]:
        """Yield LLM response text chunk by chunk. Yields one chunk on fallback."""
        if not self.api_key:
            yield self._fallback_reply(user_text, memory_summary)
            return

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": self._build_context_block(user_text, memory_summary),
                    },
                ],
                temperature=0.6,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception:
            yield self._fallback_reply(user_text, memory_summary)
