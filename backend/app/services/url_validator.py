import ipaddress
from urllib.parse import urlsplit


class URLValidationError(ValueError):
    """Raised when a URL does not meet security requirements."""


def validate_url(raw_url: str) -> str:
    if not isinstance(raw_url, str):
        raise URLValidationError("URL must be a string.")

    url = raw_url.strip()

    if not url:
        raise URLValidationError("URL cannot be empty.")

    if len(url) > 2048:
        raise URLValidationError("URL exceeds the 2048-character limit.")

    if any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise URLValidationError("URL contains invalid control characters.")

    try:
        parsed = urlsplit(url)
        port = parsed.port
        hostname = parsed.hostname
    except ValueError as exc:
        raise URLValidationError("Invalid URL structure.") from exc

    if parsed.scheme.lower() not in {"http", "https"}:
        raise URLValidationError(
            "Only HTTP and HTTPS URLs are supported."
        )

    if not parsed.netloc or not hostname:
        raise URLValidationError("A valid hostname is required.")

    if parsed.username is not None or parsed.password is not None:
        raise URLValidationError(
            "URLs containing embedded credentials are not allowed."
        )

    if port is not None and not (1 <= port <= 65535):
        raise URLValidationError("Invalid port.")

    if "%" in parsed.netloc:
        raise URLValidationError(
            "Encoded characters in the URL authority are not allowed."
        )

    if "\\" in url:
        raise URLValidationError(
            "Backslashes are not allowed in URLs."
        )

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise URLValidationError(
                "Private, local, and reserved IP addresses are not supported."
            )

    # Reject ambiguous numeric hostnames that network clients may
    # interpret as alternative IPv4 representations.
    labels = hostname.rstrip(".").split(".")

    if all(
        label and (
            label.isascii() and label.isdecimal()
            or label.lower().startswith("0x")
            and len(label) > 2
            and all(c in "0123456789abcdef" for c in label[2:].lower())
        )
        for label in labels
    ):
        raise URLValidationError(
            "Ambiguous numeric IP representations are not supported."
        )

    if hostname.lower() == "localhost" or hostname.lower().endswith(".localhost"):
        raise URLValidationError("Localhost URLs are not supported.")


    # Validate domain names using their ASCII IDNA representation.
    # Keep the original URL unchanged for the existing API contract.
    # IP literals are handled separately by ipaddress above.
    try:
        ipaddress.ip_address(hostname)
        is_ip_literal = True
    except ValueError:
        is_ip_literal = False

    if not is_ip_literal:
        import re

        domain = hostname.rstrip(".")

        if not domain or hostname.count(".") - domain.count(".") > 1:
            raise URLValidationError("Invalid hostname.")

        try:
            ascii_domain = domain.encode("idna").decode("ascii").lower()
        except UnicodeError as exc:
            raise URLValidationError(
                "Invalid internationalized hostname."
            ) from exc

        if len(ascii_domain) > 253:
            raise URLValidationError("Hostname is too long.")

        for label in ascii_domain.split("."):
            if not 1 <= len(label) <= 63:
                raise URLValidationError(
                    "Invalid DNS label length."
                )

            if not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
                label,
            ):
                raise URLValidationError(
                    "Hostname contains invalid DNS characters."
                )


    return url
