from urllib.parse import urlsplit
import ipaddress

from app.services.url_analyzer import validate_url


SUSPICIOUS_KEYWORDS = {
    "verify": 15,
    "urgent": 15,
    "password": 20,
    "account": 10,
    "suspended": 20,
    "confirm": 10,
    "free-gift": 20,
    "claim-prize": 20,
}


def analyze_scam_risk(url: str) -> dict:
    validation = validate_url(url)

    if not validation["valid"]:
        return {
            "status": "invalid",
            "risk_score": None,
            "risk_level": "UNASSESSED",
            "indicators": [],
            "reason": validation["reason"],
        }

    parsed = urlsplit(url.strip())
    hostname = parsed.hostname or ""
    score = 0
    indicators = []

    def add_indicator(code, points, explanation):
        nonlocal score
        score += points
        indicators.append({
            "code": code,
            "points": points,
            "explanation": explanation,
        })

    url_text = url.lower()

    for keyword, points in SUSPICIOUS_KEYWORDS.items():
        if keyword in url_text:
            add_indicator(
                "SUSPICIOUS_KEYWORD",
                points,
                f"URL contains the keyword '{keyword}'",
            )

    if len(url) > 100:
        add_indicator(
            "LONG_URL",
            15,
            "URL length exceeds 100 characters",
        )

    try:
        ipaddress.ip_address(hostname)
        add_indicator(
            "IP_HOSTNAME",
            25,
            "URL uses an IP address instead of a domain name",
        )
    except ValueError:
        pass

    if hostname.count(".") >= 4:
        add_indicator(
            "EXCESSIVE_SUBDOMAINS",
            15,
            "URL contains multiple subdomain levels",
        )

    if parsed.scheme.lower() == "http":
        add_indicator(
            "NO_HTTPS",
            10,
            "URL uses HTTP instead of HTTPS",
        )

    score = min(score, 100)

    if score >= 70:
        risk_level = "HIGH"
    elif score >= 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "status": "analyzed",
        "risk_score": score,
        "risk_level": risk_level,
        "indicators": indicators,
        "indicator_count": len(indicators),
        "note": "Heuristic assessment only; not a definitive phishing verdict.",
    }
