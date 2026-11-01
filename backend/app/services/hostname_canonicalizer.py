"""Validated canonical hostname representation.

This module never performs network requests.
"""

import ipaddress
import re
from urllib.parse import urlsplit

from app.services.url_validator import validate_url


_LABEL = re.compile(
    r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\Z"
)


def canonical_hostname(raw_url: str) -> str:
    """Return normalized ASCII hostname from a validated URL."""

    validated = validate_url(raw_url)
    hostname = urlsplit(validated).hostname

    if not hostname:
        raise ValueError("Missing hostname.")

    hostname = hostname.rstrip(".").lower()

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return address.compressed.lower()

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Invalid IDN hostname.") from exc

    if not ascii_hostname or len(ascii_hostname) > 253:
        raise ValueError("Invalid hostname length.")

    labels = ascii_hostname.split(".")

    if any(
        not 1 <= len(label) <= 63
        or _LABEL.fullmatch(label) is None
        for label in labels
    ):
        raise ValueError("Invalid DNS hostname labels.")

    return ascii_hostname
