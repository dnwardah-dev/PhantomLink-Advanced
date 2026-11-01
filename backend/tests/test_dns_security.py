from unittest.mock import patch
import socket

from app.services.dns_checker import check_dns_security


def mock_dns_response(ip):
    return [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))
    ]


def test_dns_public_ip():
    with patch("socket.getaddrinfo", return_value=mock_dns_response("8.8.8.8")):
        result = check_dns_security("example.com")
        assert result["safe"] is True


def test_dns_private_ip():
    with patch("socket.getaddrinfo", return_value=mock_dns_response("192.168.1.1")):
        result = check_dns_security("example.com")
        assert result["safe"] is False


def test_dns_loopback():
    with patch("socket.getaddrinfo", return_value=mock_dns_response("127.0.0.1")):
        result = check_dns_security("example.com")
        assert result["safe"] is False


def test_dns_metadata_ip():
    with patch("socket.getaddrinfo", return_value=mock_dns_response("169.254.169.254")):
        result = check_dns_security("example.com")
        assert result["safe"] is False


def test_dns_resolution_failure():
    with patch("socket.getaddrinfo", side_effect=socket.gaierror):
        result = check_dns_security("example.com")
        assert result["safe"] is False
import socket
from unittest.mock import patch

from app.services.dns_checker import check_dns_security


def test_dns_mixed_public_and_private():
    responses = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.1", 0)),
    ]

    with patch("socket.getaddrinfo", return_value=responses):
        result = check_dns_security("example.com")

    assert result["safe"] is False
    assert "192.168.1.1" in result["resolved_ips"]


def test_dns_multiple_public_ips():
    responses = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0)),
    ]

    with patch("socket.getaddrinfo", return_value=responses):
        result = check_dns_security("example.com")

    assert result["safe"] is True
    assert len(result["resolved_ips"]) == 2
import pytest


@pytest.mark.parametrize("ip,expected_safe", [
    ("::1", False),
    ("fc00::1", False),
    ("fe80::1", False),
    ("2606:4700:4700::1111", True),
])
def test_dns_ipv6_security(ip, expected_safe):
    responses = [
        (socket.AF_INET6, socket.SOCK_STREAM, 6, "", (ip, 0, 0, 0))
    ]

    with patch("socket.getaddrinfo", return_value=responses):
        result = check_dns_security("example.com")

    assert result["safe"] is expected_safe
