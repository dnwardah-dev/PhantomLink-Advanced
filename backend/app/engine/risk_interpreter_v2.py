"""Conservative interpretation of experimental URL evidence."""

from app.engine.scoring_engine_v2 import score_structural_evidence
from app.engine.domain_intelligence import analyze_domain_impersonation


STRONGER_CONTEXT_CODES = {
    "BRAND_AUTH_CONTEXT",
    "BRAND_LOOKALIKE_PATTERN",
}

STRUCTURAL_DECEPTION_CODES = {
    "URL_USERINFO_PRESENT",
    "IP_BASED_HOSTNAME",
}


def interpret_url_evidence(url: str) -> dict:
    structural = score_structural_evidence(url)
    domain_signals = analyze_domain_impersonation(url)

    structural_codes = {
        signal["code"]
        for signal in structural["signals"]
    }

    domain_codes = {
        signal["code"]
        for signal in domain_signals
    }

    contextual = sorted(
        domain_codes & STRONGER_CONTEXT_CODES
    )

    deceptive_structure = sorted(
        structural_codes & STRUCTURAL_DECEPTION_CODES
    )

    if contextual or deceptive_structure:
        category = "ADDITIONAL_REVIEW"
        message = (
            "Ditemukan indikator yang memerlukan pemeriksaan "
            "lebih lanjut. Belum cukup untuk memastikan phishing."
        )
    elif structural["signal_count"] > 0 or domain_signals:
        category = "STRUCTURAL_OBSERVATION"
        message = (
            "Ditemukan karakteristik URL yang tidak biasa, "
            "tetapi belum ada bukti kuat bahwa URL berbahaya."
        )
    else:
        category = "INSUFFICIENT_EVIDENCE"
        message = (
            "Belum ditemukan indikator dari modul ini. "
            "Hal tersebut tidak membuktikan URL aman."
        )

    return {
        "engine": "V2_EVIDENCE_INTERPRETER_EXPERIMENTAL",
        "category": category,
        "message": message,
        "structural_priority_score": (
            structural["investigation_priority_score"]
        ),
        "structural_signals": structural["signals"],
        "domain_signals": domain_signals,
        "contextual_indicators": contextual,
        "deceptive_structure_indicators": deceptive_structure,
        "is_phishing_verdict": False,
        "is_probability": False,
        "limitations": [
            "No website content was inspected.",
            "Domain impersonation rules are incomplete.",
            "An absence of signals does not establish safety.",
            "Structural score does not represent phishing probability.",
        ],
    }
