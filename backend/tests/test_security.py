import pytest

from app.services.url_analyzer import validate_url
from app.services.hostname_checker import check_hostname_security
from app.services.url_analyzer import is_public_ip


@pytest.mark.parametrize("url", [
    "http://127.0.0.1",
    "http://192.168.1.1",
    "http://10.0.0.1",
    "http://169.254.169.254",
    "http://[::1]",
    "javascript:alert(1)",
    "https://testuser:testpassword@example.com",
])
def test_blocked_urls(url):
    assert validate_url(url)["valid"] is False


@pytest.mark.parametrize("hostname", [
    "localhost",
    "admin.localhost",
    "server.local",
    "database.internal",
    "example.test",
    "router.home.arpa",
])
def test_blocked_hostnames(hostname):
    assert check_hostname_security(hostname)["safe"] is False


@pytest.mark.parametrize("ip", [
    "127.0.0.1",
    "192.168.1.1",
    "10.0.0.1",
    "169.254.169.254",
    "::1",
])
def test_blocked_ips(ip):
    assert is_public_ip(ip) is False


def test_valid_public_url():
    assert validate_url("https://example.com")["valid"] is True


def test_public_hostname():
    assert check_hostname_security("example.com")["safe"] is True
