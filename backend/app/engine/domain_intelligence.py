"""Offline domain impersonation signal detection.

Results are investigation leads, not phishing verdicts.
No network requests are performed.
"""

import re
from urllib.parse import urlsplit


BRAND_DOMAINS = {
    "paypal": {"paypal.com"},
    "google": {"google.com"},
    "microsoft": {"microsoft.com"},
    "instagram": {"instagram.com"},
}

BRAND_CONTEXT = {
    "login", "secure", "verify", "verification",
    "account", "support", "update", "security",
    "confirm", "signin",
}


def analyze_domain_impersonation(url: str) -> list[dict]:
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("HTTP or HTTPS URL required")

    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        raise ValueError("Valid hostname required")

    signals = []

    for brand, official_domains in BRAND_DOMAINS.items():
        if any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in official_domains
        ):
            continue

        labels = hostname.split(".")
        tokens = set()

        for label in labels:
            tokens.update(re.split(r"[^a-z0-9]+", label))

        tokens.discard("")

        # Brand combined with authentication-related wording.
        context_match = brand in tokens and bool(
            tokens & BRAND_CONTEXT
        )

        if context_match:
            signals.append({
                "code": "BRAND_AUTH_CONTEXT",
                "brand": brand,
                "confidence": "MEDIUM",
                "description": (
                    "A brand name and authentication-related "
                    "language appear in an unrelated hostname."
                ),
            })
        elif brand in tokens:
            signals.append({
                "code": "BRAND_NAME_IN_UNRELATED_HOSTNAME",
                "brand": brand,
                "confidence": "LOW",
                "description": (
                    "A brand name appears outside its configured "
                    "official domain."
                ),
            })

        # Limited character-substitution examples.
        lookalike = brand.replace("l", "1").replace("o", "0")

        if lookalike != brand and lookalike in tokens:
            signals.append({
                "code": "BRAND_LOOKALIKE_PATTERN",
                "brand": brand,
                "confidence": "MEDIUM",
                "description": (
                    "The hostname contains a simple lookalike "
                    "version of a configured brand."
                ),
            })

    return signals
