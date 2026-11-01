import pytest

from app.services.ip_obfuscation_checker import check_ip_obfuscation
from app.services.url_analyzer import validate_url_with_dns


@pytest.mark.parametrize("hostname", [
    "127.0.0.1",
    "2130706433",
    "0x7f000001",
    "127.1",
    "0177.0.0.1",
    "192.168.1.1",
])
def test_obfuscated_ip_blocked(hostname):
    result = check_ip_obfuscation(hostname)
    assert result["safe"] is False


@pytest.mark.parametrize("hostname", [
    "8.8.8.8",
    "example.com",
])
def test_normal_hostname_accepted(hostname):
    result = check_ip_obfuscation(hostname)
    assert result["safe"] is True


@pytest.mark.parametrize("url", [
    "http://127.0.0.1",
    "http://2130706433",
    "http://0x7f000001",
    "http://127.1",
    "http://0177.0.0.1",
])
def test_url_validator_blocks_obfuscation(url):
    result = validate_url_with_dns(url)
    assert result["valid"] is False
