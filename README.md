# ATLAS (Version 1.0)

ATLAS is a proactive personal assistant scaffold with:

- Conversational assistant loop
- Memory/context tracking
- Voice output engine with deep-male prioritization and fallback
- Integration hub stubs (weather, calendar, email, notes, smart home)
- Anthropic Claude-backed response engine with safe fallback mode

## Quick Start

1. Create and activate virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

1. Install dependencies:

   ```bash
   pip install -e .
   ```

1. Set API key — create a `.env` file in the project root:

   ```text
   ANTHROPIC_API_KEY=your_key_here
   ```

   Get your key at [console.anthropic.com](https://console.anthropic.com).

   Alternative: set an environment variable directly:

   ```bash
   # Windows CMD
   set ANTHROPIC_API_KEY=your_key_here

   # PowerShell
   $env:ANTHROPIC_API_KEY="your_key_here"
   ```

   Or create `api_key.txt` in the project root and paste the key there.

1. Configure ATLAS voice (deep male profile):

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

1. Run tests:

   ```bash
   pytest
   ```

1. Run assistant:

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

## Commands

Inside the CLI:

- `atlas <message>` — wake-word style
- `plan <objective>` — create a structured action plan
- `do <objective>` — execute with orchestration outline behavior
- `weather <city>`
- `calendar list` | `calendar add <title> | <when>`
- `email list` | `email send <to> | <subject> | <body>`
- `notes list` | `notes add <text>` | `notes find <query>`
- `smart home status` | `smart home set <device> <value>`
- `diagnostics` — system health snapshot
- `voice diagnostics` — TTS engine status
- `onboarding` — getting-started guide
- `briefing` — daily summary
- `insights` — memory-based recommendations
- `mute` / `unmute` — toggle voice output
- `stop speaking` (aliases: `stop voice`, `silence`) — interrupt speech
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

- Unit tests: `pytest -q` — all passing.
- Live LLM: Anthropic `claude-opus-4-6` with adaptive thinking and streaming.

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

**Start ATLAS API server (already binds to all interfaces):**
```bash
python -m projrvt.serve
```

**Access ATLAS from your phone:**
```
http://<tailscale-ip>:8000
```
Replace `<tailscale-ip>` with the IP shown by `tailscale ip -4` (e.g. `http://100.64.1.5:8000`).

To install as an Android home screen app: open the URL in Chrome → tap the three-dot menu → **"Add to Home Screen"**.

### Why Tailscale

- **Free** for personal use (up to 3 users, 100 devices)
- **End-to-end encrypted** — traffic never passes through a cloud server unencrypted
- **No router/firewall changes** needed (works behind NAT)
- **Always-on** — the Tailscale IP never changes, no DNS needed

### Optional: lock down the API

Set a bearer token so only your phone can talk to ATLAS:
```bash
export ATLAS_API_AUTH_KEY=your-secret-token
python -m projrvt.serve
```
Then add `Authorization: Bearer your-secret-token` to requests, or add it in `static/index.html`'s `fetch` calls.

---

## Security Note

Do not commit API keys to git. Use a `.env` file or environment variables. The `.env` file is listed in `.gitignore`.
