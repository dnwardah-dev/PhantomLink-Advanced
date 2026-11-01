"""Tests for conservative evidence interpretation."""

from app.engine.risk_interpreter_v2 import interpret_url_evidence


def test_normal_url_is_not_declared_safe():
    result = interpret_url_evidence("https://example.com")
    assert result["category"] == "INSUFFICIENT_EVIDENCE"
    assert result["is_phishing_verdict"] is False


def test_complex_benign_style_url_is_observation():
    result = interpret_url_evidence(
        "https://school-portal-2026.example.com"
    )
    assert result["structural_priority_score"] == 40
    assert result["category"] == "STRUCTURAL_OBSERVATION"
    assert result["is_phishing_verdict"] is False


def test_userinfo_requires_additional_review():
    result = interpret_url_evidence(
        "https://user@example.com/login"
    )
    assert result["category"] == "ADDITIONAL_REVIEW"
    assert "URL_USERINFO_PRESENT" in (
        result["deceptive_structure_indicators"]
    )


def test_bare_brand_mention_not_strong_context():
    result = interpret_url_evidence(
        "https://paypal-tools.example.com"
    )
    assert result["category"] != "ADDITIONAL_REVIEW"


def test_output_is_not_a_probability():
    result = interpret_url_evidence("https://example.org")
    assert result["is_probability"] is False
