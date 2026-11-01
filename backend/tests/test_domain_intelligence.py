import pytest

from app.engine.domain_intelligence import analyze_domain_impersonation


@pytest.mark.parametrize(
    "url, expected_code",
    [
        ("https://paypal.com/login", None),
        ("https://accounts.google.com/login", None),
        (
            "https://paypal-login.example.com",
            "BRAND_AUTH_CONTEXT",
        ),
        (
            "https://secure-paypal-verification.example.net",
            "BRAND_AUTH_CONTEXT",
        ),
        (
            "https://paypa1.example.com",
            "BRAND_LOOKALIKE_PATTERN",
        ),
        (
            "https://example.com",
            None,
        ),
    ],
)
def test_domain_impersonation(url, expected_code):
    signals = analyze_domain_impersonation(url)
    codes = {signal["code"] for signal in signals}

    if expected_code is None:
        assert not signals
    else:
        assert expected_code in codes
