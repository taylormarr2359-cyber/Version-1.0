# ATLAS (Version 1.0)

ATLAS is a proactive personal assistant scaffold with:
- Conversational assistant loop
- Memory/context tracking
- Voice output engine with deep-male prioritization and fallback
- Integration hub stubs (weather, calendar, email, notes, smart home)
- OpenAI-backed response engine with safe fallback mode

## Quick Start

1. Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set API key (recommended via environment variable):

```bash
set OPENAI_API_KEY=your_key_here
```

Alternative: create `api_key.txt` in project root and paste the key there.

4. Configure ATLAS voice (deep male profile):

```bash
set ATLAS_TTS_PROVIDER=local
set ATLAS_TTS_VOICE=david
set ATLAS_TTS_RATE=150
set ATLAS_TTS_VOLUME=1.0
set ATLAS_TTS_STYLE=calm_authoritative
```

Notes:
- `ATLAS_TTS_PROVIDER`: `local` (default) or `cloud` (cloud path currently placeholder with local fallback)
- `ATLAS_TTS_VOICE`: preferred voice keyword/name (e.g. `david`, `mark`, `male`, `deep_male`)
- `ATLAS_TTS_RATE`: clamped to 110..210 (lower usually sounds deeper/more natural)
- `ATLAS_TTS_VOLUME`: clamped to 0.0..1.0

5. Run tests:

```bash
pytest
```

6. Run assistant:

```bash
python -m projrvt.main
```

## Commands

Inside CLI:
- `atlas <message>` wake-word style
- `plan <objective>` create a structured action plan
- `do <objective>` execute with orchestration outline behavior
- `mute` disable voice output
- `unmute` re-enable voice output
- `stop speaking` (aliases: `stop voice`, `silence`) interrupt current speech
- `weather <city>`
- `calendar`
- `email`
- `notes`
- `smart home`
- `exit`

## Runtime Environment Controls

In addition to the TTS settings above, runtime behavior can be configured with:

```bash
set ATLAS_WAKE_WORD=atlas
set ATLAS_VOICE_INTERRUPTIBLE=true
set ATLAS_VOICE_TIMEOUT_SEC=8
```

- `ATLAS_WAKE_WORD`: wake prefix used by CLI parsing.
- `ATLAS_VOICE_INTERRUPTIBLE`: allows speech interruption handling.
- `ATLAS_VOICE_TIMEOUT_SEC`: timeout used by voice/listening paths where applicable.

## Test Status Snapshot

Validated in this environment:
- Unit tests: `pytest -q` => `21/21` passing.
- Backend/API curl matrix:
  - valid auth + valid JSON => `200`
  - invalid auth => `401`
  - malformed JSON => `400`
  - invalid endpoint => `404`

## Security Note

Do not commit API keys to git. Prefer environment variables for secrets.
