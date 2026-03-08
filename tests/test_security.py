from projrvt.security import mask_value, redact_secrets


def test_redact_sk_style_key():
    s = "my key is sk-abcdefghijklmnopqrstuvwxyz123456"
    out = redact_secrets(s)
    assert "REDACTED" in out
    assert "abcdefghijklmnopqrstuvwxyz" not in out


def test_redact_bearer_header():
    s = "Authorization: Bearer super-secret-token"
    out = redact_secrets(s)
    assert "***REDACTED***" in out
    assert "super-secret-token" not in out


def test_mask_value():
    assert mask_value("abcdef", keep=2).startswith("ab")
    assert len(mask_value("abcdef", keep=2)) == 6
