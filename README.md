# ATLAS (Version 1.0)

ATLAS is a proactive personal assistant with voice synthesis, LLM integration, and local data persistence. It runs as a CLI on desktop and as an installable Progressive Web App (PWA) on Android and any browser.

**Features:**

- Conversational assistant loop with sliding-window memory
- Voice output engine (deep-male prioritization, cloud TTS fallback)
- Integration hub — calendar, notes, email, smart home
- Anthropic Claude-backed response engine with safe fallback mode
- FastAPI REST API + PWA for Android / cross-platform access
- JARVIS-style animated face with state-reactive animations
- Proactive daily briefing and memory-based insights

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows CMD
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
pip install -r requirements.txt
```

### 3. Set your API key

Create a `.env` file in the project root:

```text
ANTHROPIC_API_KEY=your_key_here
```

Get your key at [console.anthropic.com](https://console.anthropic.com).

Or set it as an environment variable:

```bash
# Windows CMD
set ANTHROPIC_API_KEY=your_key_here

# PowerShell
$env:ANTHROPIC_API_KEY="your_key_here"

# Linux / macOS
export ANTHROPIC_API_KEY=your_key_here
```

You can also create `api_key.txt` in the project root and paste the key there.

### 4. Configure voice (optional)

```bash
set ATLAS_TTS_PROVIDER=local
set ATLAS_TTS_VOICE=david
set ATLAS_TTS_RATE=150
set ATLAS_TTS_VOLUME=1.0
set ATLAS_TTS_STYLE=calm_authoritative
```

| Variable | Values | Notes |
| --- | --- | --- |
| `ATLAS_TTS_PROVIDER` | `local` / `cloud` | `local` uses pyttsx3; `cloud` uses edge-tts |
| `ATLAS_TTS_VOICE` | keyword or name | e.g. `david`, `mark`, `male`, `deep_male` |
| `ATLAS_TTS_RATE` | `110`–`210` | Lower = deeper / more natural |
| `ATLAS_TTS_VOLUME` | `0.0`–`1.0` | |

### 5. Run tests

```bash
pytest -q
```

### 6. Run the CLI assistant

```bash
python -m projrvt.main
```

Or use the launcher scripts in `scripts/`:

```bash
# CMD
scripts\run_atlas.cmd

# PowerShell
scripts\run_atlas.ps1
```

---

## PWA / Android Access

ATLAS includes a FastAPI server and installable Progressive Web App for use on any device.

### Start the API server

```bash
pip install -e ".[api]"      # one-time: installs fastapi + uvicorn
python -m projrvt.serve      # starts on http://0.0.0.0:8000
```

### Access from any device on your local network

Open `http://<server-ip>:8000` in any browser. On Android Chrome, tap the three-dot menu → **"Add to Home Screen"** to install ATLAS as an app.

Swagger API docs: `http://localhost:8000/docs`

---

## Commands

Inside the CLI or PWA chat:

| Command | Description |
| --- | --- |
| `atlas <message>` | Wake-word style input |
| `plan <objective>` | Create a structured 4-step action plan |
| `do <objective>` | Execute with orchestration outline |
| `briefing` | Daily summary of calendar, notes, and insights |
| `insights` | Memory-based pattern recommendations |
| `calendar list` | List upcoming events |
| `calendar add <title> \| <when>` | Add a calendar event |
| `calendar delete <title>` | Delete a calendar event |
| `notes list` | List all notes |
| `notes add <text>` | Add a note |
| `notes find <query>` | Search notes |
| `notes delete <text>` | Delete a note |
| `email list` | List outbox |
| `email send <to> \| <subject> \| <body>` | Queue an email |
| `smart home status` | Show smart home device states |
| `smart home set <device> <value>` | Control a device |
| `weather <city>` | Weather stub |
| `diagnostics` | System health snapshot |
| `voice diagnostics` | TTS engine status |
| `onboarding` | Getting-started guide |
| `mute` / `unmute` | Toggle voice output |
| `stop speaking` | Interrupt current speech (aliases: `stop voice`, `silence`) |
| `exit` | Quit |

---

## Runtime Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | — | LLM API key (required for live replies) |
| `ATLAS_TTS_PROVIDER` | `local` | `local` or `cloud` |
| `ATLAS_TTS_VOICE` | auto | Voice name or keyword |
| `ATLAS_TTS_RATE` | `150` | Speech rate (110–210) |
| `ATLAS_TTS_VOLUME` | `1.0` | Volume (0.0–1.0) |
| `ATLAS_TTS_STYLE` | `calm_authoritative` | Voice style descriptor |
| `ATLAS_WAKE_WORD` | `atlas` | CLI wake prefix |
| `ATLAS_VOICE_INTERRUPTIBLE` | `true` | Allow speech interruption |
| `ATLAS_VOICE_TIMEOUT_SEC` | `10.0` | Voice synthesis timeout (1.0–30.0) |
| `ATLAS_API_HOST` | `0.0.0.0` | API server bind address |
| `ATLAS_API_PORT` | `8000` | API server port |
| `ATLAS_API_AUTH_KEY` | `""` | Bearer token for API auth; empty = open |

---

## Remote Access (Outside Home)

ATLAS uses **Tailscale** to give you secure access from anywhere — your phone on mobile data, a laptop at a coffee shop, anywhere.

### One-time setup

**On the PC running ATLAS:**

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate (opens browser)
sudo tailscale up

# Check your Tailscale IP (e.g. 100.x.y.z)
tailscale ip -4
```

**On your Android phone:**

1. Install **Tailscale** from the Google Play Store
2. Sign in with the same account used above
3. Enable the VPN in the Tailscale app

**Start ATLAS API server:**

```bash
python -m projrvt.serve
```

**Access ATLAS from your phone:**

```text
http://<tailscale-ip>:8000
```

Replace `<tailscale-ip>` with the IP from `tailscale ip -4`. To install as a home screen app: open in Chrome → three-dot menu → **"Add to Home Screen"**.

### Why Tailscale

- **Free** for personal use (up to 3 users, 100 devices)
- **End-to-end encrypted** — traffic never passes through a cloud server unencrypted
- **No router/firewall changes** needed (works behind NAT)
- **Always-on** — the Tailscale IP never changes, no DNS needed

### Optional: lock down the API

```bash
export ATLAS_API_AUTH_KEY=your-secret-token
python -m projrvt.serve
```

Then pass `Authorization: Bearer your-secret-token` in requests. To enable in the PWA, add the header to the `fetch` calls in `static/index.html`.

---

## Test Status

```bash
pytest -q   # all tests passing on Python 3.10, 3.11, 3.12
```

CI validates:

- Unit tests across the full test suite
- Valid auth + valid JSON → `200`
- Invalid auth → `401`
- Malformed JSON → `400`
- Invalid endpoint → `404`

---

## Security

- Never commit API keys to git — use `.env` or environment variables
- `.env` is listed in `.gitignore`
- See [SECRET_MANAGEMENT.md](SECRET_MANAGEMENT.md) for production key practices
