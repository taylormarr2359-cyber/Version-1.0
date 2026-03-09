# CLAUDE.md — ATLAS (projrvt) Codebase Guide

This file provides essential context for AI assistants (e.g., Claude Code) working in this repository.

---

## Project Overview

**ATLAS** is a proactive personal assistant scaffold written in Python. The installable package is named `projrvt`. It combines:

- An LLM backend (OpenAI-compatible API)
- Local and cloud text-to-speech (TTS)
- Conversation memory with sliding-window context
- Pluggable integrations (weather, calendar, email, notes, smart home)
- Proactive briefing and pattern-based insights
- Secret redaction and diagnostics utilities

**Entry point:** `python -m projrvt.main` or the `atlas` CLI command after installation.

---

## Repository Layout

```
Version-1.0/
├── src/projrvt/               # Main package source
│   ├── __init__.py            # Package init, loads .env, exports public API
│   ├── main.py                # CLI entry point (run_cli)
│   ├── assistant.py           # Core orchestrator (AtlasAssistant)
│   ├── config.py              # Configuration loading (env vars + api_key.txt)
│   ├── engine.py              # LLM engine (OpenAI gpt-4o-mini, fallback mode)
│   ├── integrations.py        # Integration hub (calendar, email, notes, smart home)
│   ├── memory.py              # Sliding-window conversation memory
│   ├── observability.py       # Diagnostics snapshot
│   ├── proactive.py           # Daily briefing and insight generation
│   ├── security.py            # Secret redaction and value masking
│   ├── voice.py               # TTS engine (pyttsx3 + edge-tts, thread-safe)
│   └── providers/
│       └── blackbox_api.py    # OpenAI-compatible HTTP provider (Blackbox fallback)
├── tests/                     # pytest test suite (21 tests, all passing)
│   ├── test_basic.py
│   ├── test_blackbox_api.py
│   ├── test_phase2_5.py
│   ├── test_proactive.py
│   ├── test_security.py
│   └── test_voice_hardening.py
├── atlas_data/                # Persistent JSON storage (gitignored runtime data)
│   ├── calendar.json
│   ├── email_outbox.json
│   ├── notes.json
│   └── smart_home.json
├── .github/workflows/ci.yml   # GitHub Actions CI (Python 3.10/3.11/3.12)
├── .pre-commit-config.yaml    # Black + isort + flake8
├── pyproject.toml             # Build config, dependencies, pytest settings
├── requirements.txt           # Test/dev deps (pytest, python-dotenv, azure-*)
├── README.md
├── CONTRIBUTING.md
├── TODO.md                    # Phased implementation roadmap
└── SECRET_MANAGEMENT.md       # Azure Key Vault and .env guidance
```

---

## Development Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1    # Windows PowerShell

# Install runtime + test dependencies
pip install -r requirements.txt
pip install -e .                 # Editable install (exposes `atlas` CLI)
```

### Required Environment Variable

```bash
export OPENAI_API_KEY="sk-..."   # Or ATLAS_API_KEY as a fallback
```

Alternatively, place the key in `api_key.txt` in the project root (not committed). The assistant degrades gracefully to fallback mode if no key is found.

---

## Running Tests

```bash
pytest           # Run all tests
pytest -q        # Quiet output (matches CI behaviour)
pytest tests/test_basic.py  # Run a single module
```

All 21 tests must pass before merging. CI runs against Python 3.10, 3.11, and 3.12.

---

## Code Formatting and Linting

Pre-commit hooks enforce style automatically:

```bash
pip install pre-commit
pre-commit install       # Install hooks into .git
pre-commit run --all-files  # Run manually on all files
```

| Tool    | Version  | Role                   |
|---------|----------|------------------------|
| black   | 24.1.0   | Code formatter         |
| isort   | 5.12.0   | Import sorter          |
| flake8  | 7.0.0    | Linter                 |

Do not submit code that fails any of these checks.

---

## Key Modules and Conventions

### `assistant.py` — `AtlasAssistant`

The central orchestrator. Holds references to all subsystems:

```python
assistant = AtlasAssistant()
result = assistant.handle("weather")   # returns AssistantResult(text, spoken)
```

- Commands are matched by simple string prefix/keyword inside `handle()`.
- Always add new top-level commands here and route to the appropriate subsystem.
- `AssistantResult` is a dataclass; don't break its interface.

### `engine.py` — `AtlasEngine`

Wraps the OpenAI client. Uses model `gpt-4o-mini` with `temperature=0.6`.

- `generate_response(prompt, context)` → `EngineResponse(text, used_live_llm)`
- Falls back to a canned message when `OPENAI_API_KEY` is absent.
- Do not hard-code model names elsewhere; change them only here.

### `config.py`

Loads all configuration from environment variables with sane defaults. Key helpers:

- `load_api_key()` — checks `OPENAI_API_KEY`, then `ATLAS_API_KEY`, then `api_key.txt`
- `load_voice_settings()` — returns a `VoiceSettings` dataclass
- `build_system_prompt()` — returns the ATLAS personality system prompt string

### `voice.py` — `VoiceEngine`

Thread-safe TTS with two backends:

1. **Local:** `pyttsx3` (default)
2. **Cloud:** `edge-tts` (set `ATLAS_TTS_PROVIDER=cloud`)

Voice selection uses a deterministic deep-male heuristic (prefers "Christopher", "David", "James" over feminine voices). The heuristic lives in `_score_voice()` — do not randomise voice selection.

```python
engine = VoiceEngine(settings)
engine.speak("Hello")
engine.stop()
engine.mute() / engine.unmute()
```

### `memory.py` — `ConversationMemory`

Sliding window of the last 20 turns (configurable). Provides:

- `add(role, content)` — append a turn
- `recent(n)` — last n items
- `relevant(query)` — keyword-scored retrieval
- `summary()` — plain-text summary for system prompt injection
- `proactive_insights()` — list of pattern-based recommendations

### `integrations.py` — `IntegrationHub`

Routes commands to integration backends. Each backend reads/writes JSON under `atlas_data/`. The dispatch interface:

```python
result = hub.dispatch("calendar list")   # IntegrationResult(ok, message)
```

When adding a new integration:
1. Add a JSON file under `atlas_data/`.
2. Implement a method on `IntegrationHub`.
3. Register the keyword in `dispatch()`.
4. Add the data file path to `observability.py`'s file-existence check.

### `security.py`

Always run user-visible output through `redact_secrets(text)` before logging or displaying in diagnostics. Patterns covered: `sk-*` keys, `api_key=` params, `Authorization: Bearer` headers.

### `providers/blackbox_api.py`

OpenAI-compatible HTTP provider used as a fallback or alternative backend. Configuration priority:

1. `OPENAI_*` env vars (preferred)
2. `BLACKBOX_*` env vars (legacy fallback)

The provider validates that `base_url` is not a placeholder (rejects `example.com`).

---

## Environment Variables Reference

| Variable                  | Default          | Description                                 |
|---------------------------|------------------|---------------------------------------------|
| `OPENAI_API_KEY`          | —                | Primary LLM API key (preferred)             |
| `ATLAS_API_KEY`           | —                | Fallback LLM API key                        |
| `OPENAI_API_BASE_URL`     | OpenAI default   | Override API endpoint                       |
| `OPENAI_MODEL`            | `gpt-4o-mini`    | Model name                                  |
| `OPENAI_TIMEOUT`          | `30`             | Request timeout (seconds)                   |
| `BLACKBOX_API_BASE_URL`   | —                | Legacy Blackbox endpoint                    |
| `BLACKBOX_API_KEY`        | —                | Legacy Blackbox API key                     |
| `BLACKBOX_MODEL`          | —                | Legacy Blackbox model                       |
| `ATLAS_TTS_PROVIDER`      | `local`          | `local` (pyttsx3) or `cloud` (edge-tts)     |
| `ATLAS_TTS_VOICE`         | `david`          | Preferred voice keyword                     |
| `ATLAS_TTS_RATE`          | `155`            | Speech rate (clamped 110–210)               |
| `ATLAS_TTS_VOLUME`        | `1.0`            | Volume (0.0–1.0)                            |
| `ATLAS_TTS_STYLE`         | `calm_authoritative` | Voice style hint                        |
| `ATLAS_WAKE_WORD`         | `atlas`          | Prefix stripped before command processing   |
| `ATLAS_VOICE_INTERRUPTIBLE` | `true`         | Allow mid-speech interruption               |
| `ATLAS_VOICE_TIMEOUT_SEC` | `4.0`            | Per-utterance timeout                       |

---

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs automatically on:
- Push to `main` or `master`
- Pull requests targeting those branches

The pipeline:
1. Checks out code
2. Sets up Python 3.10, 3.11, 3.12 (matrix)
3. Installs dependencies (`pip install -e . && pip install -r requirements.txt`)
4. Runs `pytest -q`

All tests must pass on all three Python versions before merging.

---

## Adding New Features

1. **Configuration first**: Add any new env vars to `config.py` with sensible defaults and clamping if numeric.
2. **Module boundary**: Place logic in the appropriate existing module. Create a new module only if the feature is genuinely orthogonal to all existing modules.
3. **Integration result**: New integration actions must return `IntegrationResult`.
4. **Tests required**: Add tests in `tests/test_<feature>.py` covering the happy path and at least one failure/edge case.
5. **No secrets in code**: Load API keys exclusively via `os.environ.get(...)` in `config.py`.
6. **Format before commit**: Run `black`, `isort`, and `flake8` before every commit.
7. **Update TODO.md**: If completing a roadmap item or identifying a new one, update `TODO.md`.

---

## Common Commands Reference

| Task | Command |
|---|---|
| Run assistant (CLI) | `python -m projrvt.main` |
| Run API server | `python -m projrvt.serve` |
| Run all tests | `pytest -q` |
| Run specific test | `pytest tests/test_security.py -v` |
| Format code | `black src/ tests/ && isort src/ tests/` |
| Lint | `flake8 src/ tests/` |
| All pre-commit checks | `pre-commit run --all-files` |
| Install (editable, CLI only) | `pip install -e .` |
| Install (editable, with API) | `pip install -e ".[api]"` |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` / `ATLAS_API_KEY` | — | LLM API key (required for live replies) |
| `ATLAS_TTS_PROVIDER` | `local` | `local` or `cloud` |
| `ATLAS_TTS_VOICE` | auto | Voice name or keyword for selection |
| `ATLAS_TTS_RATE` | `150` | Speech rate (clamped 110–210) |
| `ATLAS_TTS_VOLUME` | `1.0` | Volume (clamped 0.0–1.0) |
| `ATLAS_TTS_STYLE` | `calm_authoritative` | Voice style descriptor |
| `ATLAS_WAKE_WORD` | `atlas` | Prefix keyword to trigger the assistant |
| `ATLAS_VOICE_INTERRUPTIBLE` | `true` | Allow speech interruption |
| `ATLAS_VOICE_TIMEOUT_SEC` | `10.0` | Voice synthesis timeout (clamped 1.0–30.0) |
| `ATLAS_API_HOST` | `0.0.0.0` | API server bind address |
| `ATLAS_API_PORT` | `8000` | API server port (clamped 1–65535) |
| `ATLAS_API_AUTH_KEY` | `""` | Bearer token required on all API endpoints; empty = auth disabled |

---

## Known Patterns & Pitfalls

- **Fallback mode**: When no API key is set, `engine.py` returns a static fallback string rather than raising. Tests exploit this to avoid mocking HTTP.
- **Voice on CI**: `pyttsx3` may fail silently on headless CI environments. `VoiceEngine` is instantiated but voice output is skipped in test assertions.
- **JSON edge cases**: The `tests/` directory contains `.json` fixture files simulating malformed API responses, large payloads, missing fields, and timeouts. Consult these before writing new provider tests.
- **Memory window**: `ConversationMemory` holds 20 items by default. `relevant()` uses token-based scoring — avoid changing the window size without updating `test_phase2_5.py`.
- **Timestamp format**: Always append `"Z"` to ISO timestamps in `atlas_data/` files — the briefing parser expects UTC-suffixed strings.
- **API singleton state**: `api.py` holds one `AtlasAssistant` instance (`_assistant`) for the process lifetime. This means conversation memory is shared across all connected clients. This is intentional for the single-user case; be aware if adding multi-user auth.
- **PWA auth header**: When `ATLAS_API_AUTH_KEY` is set, the PWA's `fetch` calls do not currently include the `Authorization` header — add it in `index.html`'s `sendMessage` function if you need authenticated PWA access.
- **Testing the API**: `test_api.py` uses `fastapi.testclient.TestClient` which imports `httpx`. Both `fastapi` and `httpx` must be installed (`pip install -e ".[api]" && pip install httpx`). Tests are skipped gracefully if either is absent.
