"""Regression tests for conservative URL evidence mapping."""

from app.engine.analysis_pipeline_v2 import analyze_url_v2
from app.engine.url_evidence_mapping import build_url_evidence_map


def test_direct_character_mapping():
    result = analyze_url_v2(
        "https://school-portal-2026.example.com"
    )

    mappings = build_url_evidence_map(
        result["normalized_url"],
        result["evidence_trace"],
    )

    by_code = {
        item["signal_code"]: item
        for item in mappings
    }

    assert set(by_code) == {
        "HOSTNAME_CONTAINS_DIGITS",
        "HOSTNAME_CONTAINS_HYPHEN",
    }

    hostname = result["hostname"]

    for code, item in by_code.items():
        assert item["component"] == "hostname"
        assert item["component_value"] == hostname
        assert item["mapping_type"] == "DIRECT_CHARACTER_MATCH"
        assert item["is_phishing_verdict"] is False

        chars = [
            hostname[span["start"]:span["end"]]
            for span in item["spans"]
        ]

        if code == "HOSTNAME_CONTAINS_DIGITS":
            assert chars == list("2026")
        else:
            assert chars == ["-", "-"]


def test_mapping_keeps_evidence_ids():
    result = analyze_url_v2(
        "https://school-portal-2026.example.com"
    )

    traces = result["evidence_trace"]
    mappings = build_url_evidence_map(
        result["normalized_url"], traces
    )

    trace_ids = {record["evidence_id"] for record in traces}

    assert mappings
    assert all(
        mapping["evidence_id"] in trace_ids
        for mapping in mappings
    )


def test_safe_example_has_no_mapping():
    result = analyze_url_v2("https://example.com")

    mappings = build_url_evidence_map(
        result["normalized_url"],
        result["evidence_trace"],
    )

    assert mappings == []


def test_unmapped_domain_signal_is_not_invented():
    result = analyze_url_v2(
        "https://paypal-login.example.com"
    )

    mappings = build_url_evidence_map(
        result["normalized_url"],
        result["evidence_trace"],
    )

    codes = {item["signal_code"] for item in mappings}

    assert "BRAND_AUTH_CONTEXT" not in codes
    assert "HOSTNAME_CONTAINS_HYPHEN" in codes
