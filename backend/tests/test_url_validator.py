import unittest

from app.services.url_validator import (
    validate_url,
    URLValidationError,
)


class TestURLValidator(unittest.TestCase):

    def test_valid_https(self):
        url = "https://example.com/login"
        self.assertEqual(validate_url(url), url)

    def test_valid_http(self):
        url = "http://example.com"
        self.assertEqual(validate_url(url), url)

    def test_javascript_scheme(self):
        with self.assertRaises(URLValidationError):
            validate_url("javascript:alert(1)")

    def test_localhost(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://localhost/admin")

    def test_loopback_ip(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://127.0.0.1/admin")

    def test_private_ip(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://192.168.1.1/admin")

    def test_embedded_credentials(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://google.com@evil.example/login")

    def test_unsupported_scheme(self):
        with self.assertRaises(URLValidationError):
            validate_url("file:///etc/passwd")

    def test_url_too_long(self):
        with self.assertRaises(URLValidationError):
            validate_url("https://example.com/" + "a" * 2100)

    def test_empty_url(self):
        with self.assertRaises(URLValidationError):
            validate_url("")


if __name__ == "__main__":
    unittest.main()
