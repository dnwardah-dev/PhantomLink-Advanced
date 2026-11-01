import unittest

from app.services.url_validator import (
    validate_url,
    URLValidationError,
)


class TestAdvancedURLSecurity(unittest.TestCase):

    def test_ipv6_loopback(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://[::1]/admin")

    def test_private_ipv6(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://[fd00::1]/admin")

    def test_link_local_ip(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_encoded_authority(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://example%2ecom/login")

    def test_backslash(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://example.com\\@evil.example")

    def test_invalid_port(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://example.com:99999")

    def test_control_character(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://example.com/\nadmin")


if __name__ == "__main__":
    unittest.main()
