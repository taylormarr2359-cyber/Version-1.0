# CLAUDE.md — AI Assistant Guide for ATLAS (Version 1.0)

This file provides guidance for AI assistants (Claude Code and similar) working in this repository. It describes the codebase structure, development workflows, conventions, and key patterns to follow.

---

## Project Overview

**ATLAS** is a Python-based proactive personal assistant with voice synthesis, LLM integration, and local data persistence. It features:
- GPT-4o-mini (OpenAI) as the primary LLM backend with a Blackbox API fallback
- Local text-to-speech via `pyttsx3`, with cloud TTS fallback via `edge-tts`
- Conversation memory, calendar, notes, email, and smart home integrations backed by local JSON files
- Proactive briefing and pattern-based insight generation
- Secret redaction and observability diagnostics

**Package name:** `projrvt`
**Version:** `1.0.0`
**Python requirement:** `>=3.10`

---

## Repository Structure

```
Version-1.0/
├── src/projrvt/              # Main application source
│   ├── __init__.py
│   ├── main.py               # CLI entry point (interactive loop)
│   ├── assistant.py          # AtlasAssistant — central command dispatcher
│   ├── config.py             # Configuration loader (env vars + defaults)
│   ├── engine.py             # AtlasEngine — LLM calls (plan/reply)
│   ├── voice.py              # VoiceEngine — TTS, mute/unmute, threading
│   ├── integrations.py       # IntegrationsHub — calendar, notes, email, etc.
│   ├── memory.py             # ConversationMemory — sliding window buffer
│   ├── proactive.py          # Briefing + pattern-based insights
│   ├── observability.py      # DiagnosticsSnapshot dataclass
│   ├── security.py           # Secret redaction utilities
│   └── providers/
│       └── blackbox_api.py   # Unified API provider (OpenAI-first + fallback)
├── tests/                    # pytest test suite (21 tests)
│   ├── test_basic.py
│   ├── test_blackbox_api.py
│   ├── test_security.py
│   ├── test_phase2_5.py
│   ├── test_proactive.py
│   └── test_voice_hardening.py
├── atlas_data/               # Local JSON persistence (git-tracked defaults)
│   ├── calendar.json
│   ├── notes.json
│   ├── email_outbox.json
│   └── smart_home.json
├── .github/workflows/ci.yml  # GitHub Actions CI (Python 3.10–3.12)
├── .pre-commit-config.yaml   # black, isort, flake8 hooks
├── pyproject.toml            # Project metadata + pytest config
├── requirements.txt          # Dev/test dependencies
├── README.md                 # User-facing quick-start and command reference
├── CONTRIBUTING.md           # Contributor setup guide
├── SECRET_MANAGEMENT.md      # Security practices for API keys
└── TODO.md                   # Phased development roadmap
```

---

## Development Workflow

### Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\Activate.ps1      # Windows PowerShell

pip install -e .
pip install -r requirements.txt
```

### Running the Assistant

```bash
python -m projrvt.main
```

### Running Tests

```bash
pytest -q
```

All 21 tests must pass. The CI matrix validates Python 3.10, 3.11, and 3.12.

### Code Quality

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

Or run all pre-commit hooks at once:

```bash
pre-commit run --all-files
```

---

## Key Conventions

### Code Style

- **Formatter:** `black` (v24.1.0) — no manual formatting decisions; run it and commit
- **Import order:** `isort` (v5.12.0) — always run after adding imports
- **Linting:** `flake8` (v7.0.0) — zero warnings expected before committing
- Line length follows black's default (88 chars)

### Module Responsibilities

Each module has a single, well-defined role. Do not cross concerns:

| Module | Responsibility |
|---|---|
| `assistant.py` | Command dispatch and user-facing response logic |
| `engine.py` | LLM prompt construction and API calls only |
| `voice.py` | TTS synthesis and audio control only |
| `integrations.py` | Data read/write for calendar, notes, email, smart home |
| `memory.py` | Conversation context storage and retrieval |
| `proactive.py` | Briefing and insight generation (read-only against memory/integrations) |
| `observability.py` | Diagnostics snapshot, no side effects |
| `security.py` | Secret redaction only |
| `config.py` | Environment variable loading and default values |
| `providers/blackbox_api.py` | HTTP-level API abstraction |

### Configuration Pattern

All runtime settings come from environment variables loaded in `config.py`. The pattern is:

```python
os.environ.get("ATLAS_SETTING_NAME", default_value)
```

Numeric values are clamped to valid ranges (e.g., TTS rate: 110–210, volume: 0.0–1.0, timeout: 1.0–30.0). Never hardcode configuration values in feature modules — always add them to `config.py` first.

### Data Storage

Local JSON files in `atlas_data/` use this schema:

- **calendar.json**: `[{"title": str, "when": str, "created_at": str (ISO + "Z")}]`
- **notes.json**: `[{"text": str, "created_at": str (ISO + "Z")}]`
- **email_outbox.json**: `[{"to": str, "subject": str, "body": str, "status": "queued", "created_at": str}]`
- **smart_home.json**: `{"lights": str, "thermostat": str, "locks": str}`

All timestamps use ISO 8601 format with a trailing `Z` (UTC). Do not change the schema without updating `integrations.py` and adding a migration path.

### Integration Return Type

All `IntegrationsHub` methods must return an `IntegrationResult(ok: bool, message: str)` named tuple. Do not return raw data or raise exceptions from integration methods — surface errors through `ok=False, message=<description>`.

### LLM Engine

- Model: `gpt-4o-mini` (OpenAI primary)
- Temperature: `0.6` (do not change without testing)
- `engine.plan()` always returns a 4-step numbered plan
- `engine.reply()` appends the latest user message to memory before calling the API
- System prompt is assembled by `config.py:build_system_prompt()`

### Security

- **Never** commit API keys, `.env` files, or secrets to the repository
- `.env` is in `.gitignore` — use it locally for keys
- The `security.py` module provides `redact_secrets()` — use it when logging any user input or API responses
- API key patterns covered: `sk-*` (OpenAI), generic `api_key=*`, `Bearer *` tokens
- For production/CI: use Azure Key Vault (see `SECRET_MANAGEMENT.md`)

### Voice Engine

- Local voice selection uses a deterministic deep-male preference heuristic in `voice.py:_select_best_local_voice()`
- TTS runs on a background thread; `stop_speaking()` is interrupt-safe
- Mute state is tracked in `VoiceEngine.muted` (bool)
- Cloud TTS (edge-tts) is the fallback when `ATLAS_TTS_PROVIDER=cloud`

---

## Testing Conventions

- All tests live in `tests/`, no subdirectories
- Use `pytest` only — no unittest-style classes (plain functions with descriptive names)
- Mock external API calls with `unittest.mock.patch` — tests must not make real HTTP requests
- Fixture data (JSON payloads) for API edge cases lives in root or `tests/` as `.json` files
- Test file naming: `test_<feature>.py`
- Test function naming: `test_<what_it_checks>()`
- Every new module or non-trivial function needs at least one test

### Running a Specific Test File

```bash
pytest tests/test_security.py -v
```

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
| Run assistant | `python -m projrvt.main` |
| Run all tests | `pytest -q` |
| Run specific test | `pytest tests/test_security.py -v` |
| Format code | `black src/ tests/ && isort src/ tests/` |
| Lint | `flake8 src/ tests/` |
| All pre-commit checks | `pre-commit run --all-files` |
| Install (editable) | `pip install -e .` |

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

---

## Known Patterns & Pitfalls

- **Fallback mode**: When no API key is set, `engine.py` returns a static fallback string rather than raising. Tests exploit this to avoid mocking HTTP.
- **Voice on CI**: `pyttsx3` may fail silently on headless CI environments. `VoiceEngine` is instantiated but voice output is skipped in test assertions.
- **JSON edge cases**: The `tests/` directory contains `.json` fixture files simulating malformed API responses, large payloads, missing fields, and timeouts. Consult these before writing new provider tests.
- **Memory window**: `ConversationMemory` holds 20 items by default. `relevant()` uses token-based scoring — avoid changing the window size without updating `test_phase2_5.py`.
- **Timestamp format**: Always append `"Z"` to ISO timestamps in `atlas_data/` files — the briefing parser expects UTC-suffixed strings.
