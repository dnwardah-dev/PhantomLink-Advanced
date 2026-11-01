"""Evidence Traceability regression tests."""

import pytest

from app.engine.analysis_pipeline_v2 import analyze_url_v2
from app.engine.evidence_traceability import build_evidence_trace


@pytest.mark.parametrize(
    "url,expected_count",
    [
        ("https://example.com", 0),
        ("https://school-portal-2026.example.com", 3),
        ("https://paypal-login.example.com", 2),
    ],
)
def test_all_signals_are_traceable(url, expected_count):
    result = analyze_url_v2(url)
    interpretation = result["interpretation"]

    original_signals = {
        (source, signal["code"])
        for source, signals in [
            ("structural", interpretation["structural_signals"]),
            ("domain", interpretation["domain_signals"]),
        ]
        for signal in signals
    }

    traces = build_evidence_trace(interpretation)

    traced_signals = {
        (record["source"], record["signal_code"])
        for record in traces
    }

    assert original_signals == traced_signals
    assert len(traces) == expected_count
    assert all(record["is_phishing_verdict"] is False for record in traces)


def test_evidence_ids_are_stable():
    interpretation = {
        "structural_signals": [
            {
                "code": "HOSTNAME_CONTAINS_HYPHEN",
                "evidence": "Hostname contains a hyphen.",
                "confidence": "LOW",
            }
        ],
        "domain_signals": [],
    }

    first = build_evidence_trace(interpretation)
    second = build_evidence_trace(interpretation)

    assert first[0]["evidence_id"] == second[0]["evidence_id"]


def test_domain_description_is_supported():
    interpretation = {
        "structural_signals": [],
        "domain_signals": [
            {
                "code": "BRAND_AUTH_CONTEXT",
                "description": "Brand and authentication context detected.",
                "confidence": "MEDIUM",
            }
        ],
    }

    traces = build_evidence_trace(interpretation)

    assert len(traces) == 1
    assert traces[0]["source"] == "domain"
    assert traces[0]["signal_code"] == "BRAND_AUTH_CONTEXT"
    assert traces[0]["confidence"] == "MEDIUM"
    assert traces[0]["is_phishing_verdict"] is False
