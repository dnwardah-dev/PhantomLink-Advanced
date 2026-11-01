EXPLANATIONS = {
    "SUSPICIOUS_KEYWORD": {
        "title": "Suspicious URL Keyword",
        "reason": (
            "URL contains terms commonly associated with "
            "account verification, urgency, or phishing attempts."
        ),
        "action": (
            "Avoid entering passwords or OTPs until the website "
            "has been verified through an official channel."
        ),
    },
    "NO_HTTPS": {
        "title": "Unencrypted HTTP Connection",
        "reason": (
            "The URL uses HTTP rather than HTTPS, which does not "
            "provide transport encryption."
        ),
        "action": (
            "Avoid submitting sensitive information over HTTP."
        ),
    },
    "IP_ADDRESS_HOST": {
        "title": "IP Address Used as Hostname",
        "reason": (
            "The URL uses a direct IP address instead of "
            "a conventional domain name."
        ),
        "action": (
            "Verify the destination and avoid sharing personal data "
            "with unfamiliar IP-based websites."
        ),
    },
    "LONG_URL": {
        "title": "Unusually Long URL",
        "reason": (
            "A lengthy URL can make suspicious parameters "
            "or misleading paths harder to notice."
        ),
        "action": (
            "Inspect the hostname carefully and avoid following "
            "untrusted links."
        ),
    },
    "MULTIPLE_SUBDOMAINS": {
        "title": "Complex Subdomain Structure",
        "reason": (
            "Multiple subdomains can make the actual registered "
            "domain harder to identify."
        ),
        "action": (
            "Check the registered domain rather than trusting "
            "familiar-looking words elsewhere in the URL."
        ),
    },
}


KEYWORD_EXPLANATIONS = {
    "verify": {
        "title": "Account Verification Keyword",
        "reason": (
            "The URL contains the word 'verify'. "
            "This term is sometimes used in phishing links to "
            "encourage users to verify their identity or account."
        ),
        "action": (
            "Open the official website independently instead of "
            "following an unexpected verification link."
        ),
    },
    "account": {
        "title": "Account-Related Keyword",
        "reason": (
            "The URL contains the word 'account'. "
            "Account-related paths are common on legitimate websites "
            "but can also appear in phishing attempts."
        ),
        "action": (
            "Check the actual domain before entering your "
            "username, password, or verification code."
        ),
    },
}


def explain_indicators(indicators):
    import re

    explanations = []

    for indicator in indicators:
        code = indicator.get("code", "UNKNOWN")
        info = EXPLANATIONS.get(code)

        if info is None:
            info = {
                "title": code,
                "reason": (
                    "The analysis engine flagged this URL pattern. "
                    "A detailed explanation is not yet available."
                ),
                "action": (
                    "Verify the URL independently before sharing "
                    "sensitive information."
                ),
            }

        # Use the keyword explicitly reported by the analyzer.
        if code == "SUSPICIOUS_KEYWORD":
            evidence_text = str(indicator.get("explanation", ""))
            match = re.fullmatch(
                r"URL contains the keyword ['\"]([A-Za-z0-9_-]+)['\"]",
                evidence_text,
            )

            if match:
                keyword = match.group(1).lower()
                info = KEYWORD_EXPLANATIONS.get(keyword, info)

        explanations.append({
            "code": code,
            "points": indicator.get("points", 0),
            "title": info["title"],
            "reason": info["reason"],
            "action": info["action"],
        })

    return explanations
