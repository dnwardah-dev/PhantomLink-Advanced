"""Offline lexical URL signals for PhantomLink V2.

Signals are observations, not definitive phishing verdicts.
No DNS lookup or HTTP request is performed here.
"""

import re
from urllib.parse import urlsplit, unquote


SENSITIVE_TERMS = {
    "verify",
    "password",
    "account",
    "suspended",
    "confirm",
    "urgent",
    "login",
    "security",
    "reset",
}

HIGH_PRESSURE_TERMS = {
    "urgent",
    "suspended",
    "immediately",
    "expired",
}

REWARD_TERMS = {
    "free-gift",
    "claim-prize",
    "winner",
    "reward",
}


def tokenize_url_part(value: str) -> set[str]:
    """Extract normalized tokens from a URL component."""
    decoded = unquote(value).lower()

    return {
        token
        for token in re.split(r"[^a-z0-9]+", decoded)
        if token
    }


def analyze_url_signals(url: str) -> list[dict]:
    """Return descriptive lexical signals without assigning a risk score."""
    if not isinstance(url, str):
        raise ValueError("URL must be a string")

    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Expected a validated HTTP or HTTPS URL")

    hostname = parsed.hostname.lower()
    path_tokens = tokenize_url_part(parsed.path)
    query_tokens = tokenize_url_part(parsed.query)

    signals = []

    if parsed.scheme.lower() == "http":
        signals.append({
            "code": "NO_HTTPS",
            "category": "transport",
            "confidence": "LOW",
            "description": "The URL uses HTTP rather than HTTPS.",
        })

    sensitive = sorted(
        (path_tokens | query_tokens) & SENSITIVE_TERMS
    )

    if sensitive:
        signals.append({
            "code": "SENSITIVE_TERMS",
            "category": "language",
            "confidence": "LOW",
            "description": "Account or security-related terms appear in the URL.",
            "matches": sensitive,
        })

    pressure = sorted(
        (path_tokens | query_tokens) & HIGH_PRESSURE_TERMS
    )

    if pressure:
        signals.append({
            "code": "URGENCY_LANGUAGE",
            "category": "social_engineering",
            "confidence": "LOW",
            "description": "The URL contains urgency-related language.",
            "matches": pressure,
        })

    rewards = sorted(
        (path_tokens | query_tokens) & REWARD_TERMS
    )

    if rewards:
        signals.append({
            "code": "REWARD_LANGUAGE",
            "category": "social_engineering",
            "confidence": "LOW",
            "description": "The URL contains reward-related language.",
            "matches": rewards,
        })

    if len(url) > 100:
        signals.append({
            "code": "LONG_URL",
            "category": "structure",
            "confidence": "LOW",
            "description": "URL length exceeds 100 characters.",
        })

    if hostname.count(".") >= 4:
        signals.append({
            "code": "DEEP_HOSTNAME",
            "category": "structure",
            "confidence": "LOW",
            "description": "Hostname contains multiple dot-separated labels.",
        })

    return signals
