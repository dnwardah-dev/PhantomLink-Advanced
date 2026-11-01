"""Security and integration tests for the offline V2 pipeline."""

import socket

import pytest

from app.engine.analysis_pipeline_v2 import analyze_url_v2
from app.services.url_validator import URLValidationError


@pytest.mark.parametrize(
    "url, expected_category",
    [
        ("https://example.com/", "INSUFFICIENT_EVIDENCE"),
        (
            "https://school-portal-2026.example.com/",
            "STRUCTURAL_OBSERVATION",
        ),
        (
            "https://paypal-login.example.com/",
            "ADDITIONAL_REVIEW",
        ),
    ],
)
def test_pipeline_interpretation(url, expected_category):
    result = analyze_url_v2(url)

    assert result["status"] == "analyzed"
    assert result["interpretation"]["category"] == expected_category
    assert result["network_requests_performed"] is False
    assert result["is_phishing_verdict"] is False


def test_unicode_and_punycode_equivalence():
    unicode_url = "https://b\u00fccher.example/login"
    punycode_url = "https://xn--bcher-kva.example/login"

    unicode_result = analyze_url_v2(unicode_url)
    punycode_result = analyze_url_v2(punycode_url)

    assert unicode_result["hostname"] == "xn--bcher-kva.example"
    assert unicode_result["hostname"] == punycode_result["hostname"]
    assert unicode_result["normalized_url"] == punycode_result["normalized_url"]


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/admin",
        "http://127.0.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/",
        "https://foo..example.com/",
        "https://foo_bar.example.com/",
        "https://" + "a" * 64 + ".example.com/",
        "https://user@example.com/",
        "javascript:alert(1)",
    ],
)
def test_invalid_targets_rejected(url):
    with pytest.raises(URLValidationError):
        analyze_url_v2(url)


def test_pipeline_does_not_use_socket(monkeypatch):
    def block_network(*args, **kwargs):
        raise AssertionError("Unexpected network operation!")

    monkeypatch.setattr(socket, "getaddrinfo", block_network)
    monkeypatch.setattr(socket, "create_connection", block_network)
    monkeypatch.setattr(socket.socket, "connect", block_network)
    monkeypatch.setattr(socket.socket, "connect_ex", block_network)

    result = analyze_url_v2(
        "https://secure-login-2026.example.com/"
    )

    assert result["status"] == "analyzed"
    assert result["network_requests_performed"] is False
