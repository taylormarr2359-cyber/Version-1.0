# ATLAS Implementation TODO (Hardening Pass: 1 -> 5)

## 1) Voice quality hardening
- [ ] Update `src/projrvt/voice.py`
  - [ ] Deterministic deep-male voice selection heuristic
  - [ ] Fallback voice chain if preferred voice unavailable
  - [ ] Runtime controls (rate/volume/voice diagnostics)
  - [ ] Interruption-safe speak wrapper
- [ ] Add tests
  - [ ] `tests/test_voice_hardening.py`

## 2) Proactive intelligence layer
- [ ] Create `src/projrvt/proactive.py`
  - [ ] Daily briefing generator
  - [ ] Lightweight anomaly/routine insights
- [ ] Wire assistant commands in `src/projrvt/assistant.py`
  - [ ] `briefing`
  - [ ] `insights`
- [ ] Add tests
  - [ ] `tests/test_proactive.py`

## 3) Security hardening
- [ ] Create `src/projrvt/security.py`
  - [ ] Secret redaction utility
  - [ ] Key presence checks
  - [ ] Safe diagnostics masking
- [ ] Integrate security utilities where needed
  - [ ] `src/projrvt/assistant.py`
  - [ ] `src/projrvt/observability.py`
  - [ ] `src/projrvt/providers/blackbox_api.py` (if needed)
- [ ] Add tests
  - [ ] `tests/test_security.py`

## 4) UX polish
- [ ] Expand command help in `src/projrvt/assistant.py`
- [ ] Add `onboarding` command in `src/projrvt/assistant.py`
- [ ] Improve diagnostics readability in `src/projrvt/observability.py`
- [ ] Update `README.md` with hardening features and command usage

## 5) Packaging/deployment
- [ ] Add launcher scripts
  - [ ] `scripts/run_atlas.ps1`
  - [ ] `scripts/run_atlas.cmd`
- [ ] Add startup helper
  - [ ] `scripts/register_startup.ps1`
- [ ] Add packaging/deployment docs to `README.md`

## Thorough testing
- [ ] Run full test suite: `pytest -q`
- [ ] Add/update tests for new modules and flows
- [ ] Manual command smoke:
  - [ ] `help`
  - [ ] `onboarding`
  - [ ] `briefing`
  - [ ] `insights`
  - [ ] `diagnostics`
- [ ] Re-run API curl matrix to confirm no regressions
- [ ] Validate launcher scripts in shell
