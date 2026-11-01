import pytest

from app.services.url_validator import (
    validate_url,
    URLValidationError,
)


@pytest.mark.parametrize("hostname", [
    "a" * 64 + ".example.com",
    "a" * 250 + ".example.com",
    "foo..example.com",
    "foo_bar.example.com",
    "-bad.example.com",
    "bad-.example.com",
    ".example.com",
])
def test_invalid_hostnames_rejected(hostname):
    with pytest.raises(URLValidationError):
        validate_url(f"https://{hostname}/")


@pytest.mark.parametrize("url", [
    "https://example.com/",
    "https://example.com./login",
    "https://xn--bcher-kva.example/login",
    "https://" + "a" * 63 + ".example.com/",
    "https://b\u00fccher.example/login",
])
def test_valid_hostnames_accepted(url):
    assert validate_url(url) == url


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/",
    "http://192.168.1.1/",
    "http://169.254.169.254/",
    "http://localhost/",
])
def test_local_targets_still_rejected(url):
    with pytest.raises(URLValidationError):
        validate_url(url)
