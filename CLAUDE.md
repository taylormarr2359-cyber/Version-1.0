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

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main`/`master` and all PRs:

1. Checkout code
2. Set up Python (matrix: 3.10, 3.11, 3.12)
3. `pip install -r requirements.txt && pip install -e .`
4. `pytest -q`

All matrix versions must pass. Do not merge if CI is red.

---

## Adding New Features — Checklist

- [ ] Implement in the appropriate module (see layout above).
- [ ] Register new commands in `assistant.py` `handle()`.
- [ ] Add/update integration data file and `observability.py` if storage is involved.
- [ ] Write pytest tests in `tests/` (target: keep 100% of existing tests green, add new ones).
- [ ] Run `pre-commit run --all-files` and fix any issues.
- [ ] Update `README.md` command list if a user-facing command was added.
- [ ] Ensure no secrets appear in code, tests, or committed files.

---

## Security Guidelines

- Never commit API keys, tokens, or credentials. Use `.env` (gitignored) or Azure Key Vault.
- Wrap any output that may contain user-provided strings in `security.redact_secrets()`.
- Do not log raw LLM responses without redaction.
- Validate external URLs — reject placeholders like `example.com`.
- Refer to `SECRET_MANAGEMENT.md` for production secret-handling guidance.

---

## Persistent Data

Runtime data lives in `atlas_data/` (JSON files). These are **not** committed (they are runtime state). When working locally you may need to seed them:

```bash
echo '[]' > atlas_data/calendar.json
echo '[]' > atlas_data/notes.json
echo '[]' > atlas_data/email_outbox.json
echo '{"lights": "off", "thermostat": 70, "locks": "locked"}' > atlas_data/smart_home.json
```

---

## Pending Work (TODO.md)

Phase 5 (packaging/deployment) is not yet complete:

- Launcher scripts (`atlas.sh`, `atlas.bat`)
- Systemd/launchd startup helpers
- Docker packaging

Do not assume these exist when writing new tooling.
