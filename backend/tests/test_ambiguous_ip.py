import unittest

from app.services.url_validator import (
    validate_url,
    URLValidationError,
)


class TestAmbiguousIPProtection(unittest.TestCase):

    def test_decimal_ip(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://2130706433/admin")

    def test_shortened_ipv4(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://127.1/admin")

    def test_octal_style_ipv4(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://0177.0.0.1/admin")

    def test_hexadecimal_ipv4(self):
        with self.assertRaises(URLValidationError):
            validate_url("http://0x7f000001/admin")


if __name__ == "__main__":
    unittest.main()
