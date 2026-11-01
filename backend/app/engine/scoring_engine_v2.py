"""Experimental explainable structural scoring engine.

Scores are investigation-priority points, NOT phishing probabilities.
No network requests are made.
"""

from app.engine.url_structure_v2 import analyze_url_structure


def score_structural_evidence(url: str) -> dict:
    signals = analyze_url_structure(url)

    # Count distinct signal types, not duplicate occurrences.
    codes = {signal["code"] for signal in signals}
    count = len(codes)

    if count == 0:
        score = 0
        priority = "NO_STRUCTURAL_EVIDENCE"
    elif count == 1:
        score = 10
        priority = "LOW"
    elif count == 2:
        score = 25
        priority = "REVIEW"
    else:
        score = 40
        priority = "ELEVATED_REVIEW"

    return {
        "engine": "V2_STRUCTURAL_EXPERIMENTAL",
        "status": "experimental",
        "investigation_priority_score": score,
        "priority": priority,
        "signal_count": count,
        "signals": signals,
        "is_phishing_verdict": False,
        "is_probability": False,
        "limitations": [
            "Structural patterns alone cannot confirm phishing.",
            "A zero score does not establish website safety.",
            "Weights are provisional and not statistically calibrated.",
            "This engine does not access external websites.",
        ],
    }
