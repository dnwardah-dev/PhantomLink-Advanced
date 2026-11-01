"""Tests for shared canonical hostname handling."""

import pytest

from app.services.hostname_canonicalizer import canonical_hostname
from app.services.url_validator import URLValidationError


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://example.com/", "example.com"),
        ("https://EXAMPLE.COM./login", "example.com"),
        ("https://b\u00fccher.example/login", "xn--bcher-kva.example"),
        ("https://xn--bcher-kva.example/login", "xn--bcher-kva.example"),
        ("https://" + "a" * 63 + ".example.com/", "a" * 63 + ".example.com"),
    ],
)
def test_canonical_hostnames(url, expected):
    assert canonical_hostname(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/",
        "http://127.0.0.1/",
        "http://169.254.169.254/",
        "https://foo..example.com/",
        "https://foo_bar.example.com/",
        "https://" + "a" * 64 + ".example.com/",
        "https://user@example.com/",
    ],
)
def test_unsafe_or_invalid_hostnames_rejected(url):
    with pytest.raises(URLValidationError):
        canonical_hostname(url)
