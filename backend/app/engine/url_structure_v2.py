"""Offline structural URL signals for PhantomLink V2."""

import ipaddress
from urllib.parse import urlsplit


def analyze_url_structure(url: str) -> list[dict]:
    """Return explainable structural signals without making network requests."""

    try:
        parsed = urlsplit(url.strip())

        if parsed.scheme.lower() not in {"http", "https"}:
            return []

        hostname = (parsed.hostname or "").lower().rstrip(".")

        if not hostname:
            return []

    except (AttributeError, ValueError):
        return []

    signals = []

    def add(code: str, evidence: str, confidence: str = "LOW"):
        signals.append({
            "code": code,
            "evidence": evidence,
            "confidence": confidence,
            "source": "URL_STRUCTURE_V2",
        })

    try:
        ipaddress.ip_address(hostname)
        add(
            "IP_BASED_HOSTNAME",
            "URL menggunakan alamat IP sebagai hostname.",
            "MEDIUM",
        )
        return signals
    except ValueError:
        pass

    if len(hostname) >= 30:
        add(
            "LONG_HOSTNAME",
            f"Hostname memiliki {len(hostname)} karakter.",
        )

    if any(character.isdigit() for character in hostname):
        add(
            "HOSTNAME_CONTAINS_DIGITS",
            "Hostname mengandung angka.",
        )

    if "-" in hostname:
        add(
            "HOSTNAME_CONTAINS_HYPHEN",
            "Hostname mengandung tanda hubung.",
        )

    if hostname.count(".") >= 4:
        add(
            "DEEP_SUBDOMAIN_STRUCTURE",
            "Hostname memiliki banyak tingkat subdomain.",
        )

    if "@" in parsed.netloc:
        add(
            "URL_USERINFO_PRESENT",
            "URL menggunakan komponen userinfo sebelum hostname.",
            "MEDIUM",
        )

    return signals
