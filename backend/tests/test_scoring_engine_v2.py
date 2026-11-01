"""Tests for experimental structural scoring."""

import pytest

from app.engine.scoring_engine_v2 import score_structural_evidence


@pytest.mark.parametrize(
    "url, expected_score, expected_count",
    [
        ("https://example.com", 0, 0),
        ("https://site-portal.example.com", 10, 1),
        ("https://secure-login-2026.example.com", 25, 2),
        (
            "https://very-long-secure-login-2026.example.com",
            40,
            3,
        ),
    ],
)
def test_score_levels(url, expected_score, expected_count):
    result = score_structural_evidence(url)

    assert result["investigation_priority_score"] == expected_score
    assert result["signal_count"] == expected_count
    assert result["status"] == "experimental"
    assert result["is_phishing_verdict"] is False
    assert result["is_probability"] is False


def test_zero_score_does_not_claim_safety():
    result = score_structural_evidence("https://example.com")

    assert result["priority"] == "NO_STRUCTURAL_EVIDENCE"
    assert any(
        "zero score" in limitation.lower()
        for limitation in result["limitations"]
    )


def test_structural_signals_remain_explainable():
    result = score_structural_evidence(
        "https://secure-login-2026.example.com"
    )

    codes = {signal["code"] for signal in result["signals"]}

    assert "HOSTNAME_CONTAINS_DIGITS" in codes
    assert "HOSTNAME_CONTAINS_HYPHEN" in codes
