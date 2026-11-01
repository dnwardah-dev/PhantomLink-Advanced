import pytest

from app.services.unicode_checker import check_unicode_hostname
from app.services.url_analyzer import validate_url_with_dns


@pytest.mark.parametrize("hostname", [
    "google.com",
    "example.com",
    "sub.example.com",
])
def test_normal_hostnames(hostname):
    result = check_unicode_hostname(hostname)
    assert result["safe"] is True


@pytest.mark.parametrize("hostname", [
    "gооgle.com",
    "xn--e1afmkfd.xn--p1ai",
    "google.com ",
    "example!.com",
    "",
])
def test_suspicious_hostnames(hostname):
    result = check_unicode_hostname(hostname)
    assert result["safe"] is False


@pytest.mark.parametrize("url", [
    "https://gооgle.com",
    "https://xn--e1afmkfd.xn--p1ai",
])
def test_url_validator_blocks_unicode(url):
    result = validate_url_with_dns(url)
    assert result["valid"] is False
