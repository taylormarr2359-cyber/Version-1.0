# ATLAS Implementation TODO (Hardening Pass: 1 -> 5)

## 1) Voice quality hardening
- [x] Update `src/projrvt/voice.py`
  - [x] Deterministic deep-male voice selection heuristic
  - [x] Fallback voice chain if preferred voice unavailable
  - [x] Runtime controls (rate/volume/voice diagnostics)
  - [x] Interruption-safe speak wrapper
- [x] Add tests
  - [x] `tests/test_voice_hardening.py`

## 2) Proactive intelligence layer
- [x] Create `src/projrvt/proactive.py`
  - [x] Daily briefing generator
  - [x] Lightweight anomaly/routine insights
- [x] Wire assistant commands in `src/projrvt/assistant.py`
  - [x] `briefing`
  - [x] `insights`
- [x] Add tests
  - [x] `tests/test_proactive.py`

## 3) Security hardening
- [x] Create `src/projrvt/security.py`
  - [x] Secret redaction utility
  - [x] Key presence checks
  - [x] Safe diagnostics masking
- [x] Integrate security utilities where needed
  - [x] `src/projrvt/assistant.py`
  - [x] `src/projrvt/observability.py`
  - [x] `src/projrvt/providers/blackbox_api.py` (if needed)
- [x] Add tests
  - [x] `tests/test_security.py`

## 4) UX polish
- [x] Expand command help in `src/projrvt/assistant.py`
- [x] Add `onboarding` command in `src/projrvt/assistant.py`
- [x] Improve diagnostics readability in `src/projrvt/observability.py`
- [x] Update `README.md` with hardening features and command usage

## 5) Packaging/deployment
- [x] Add launcher scripts
  - [x] `scripts/run_atlas.ps1`
  - [x] `scripts/run_atlas.cmd`
- [x] Add startup helper
  - [x] `scripts/register_startup.ps1`
- [ ] Add packaging/deployment docs to `README.md`

## Thorough testing
- [x] Run full test suite: `pytest -q` — 51 tests, all passing
- [x] Add/update tests for new modules and flows
- [ ] Manual command smoke:
  - [ ] `help`
  - [ ] `onboarding`
  - [ ] `briefing`
  - [ ] `insights`
  - [ ] `diagnostics`
- [ ] Re-run API curl matrix to confirm no regressions
- [ ] Validate launcher scripts in shell
