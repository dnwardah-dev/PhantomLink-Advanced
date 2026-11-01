"""Traceable, non-verdict evidence records for PhantomLink V2."""

import hashlib


def build_evidence_trace(interpretation: dict) -> list[dict]:
    """Convert V2 signals into individually traceable evidence records."""

    records = []
    seen = set()

    sources = (
        ("structural", interpretation.get("structural_signals", [])),
        ("domain", interpretation.get("domain_signals", [])),
    )

    for source, signals in sources:
        for signal in signals:
            if not isinstance(signal, dict):
                continue

            code = signal.get("code")
            evidence = signal.get("evidence")

            if not isinstance(evidence, str) or not evidence.strip():
                evidence = signal.get("description")

            if not isinstance(code, str) or not code.strip():
                continue

            if not isinstance(evidence, str) or not evidence.strip():
                continue

            identity = (source, code, evidence)

            if identity in seen:
                continue

            seen.add(identity)

            fingerprint = hashlib.sha256(
                repr(identity).encode("utf-8")
            ).hexdigest()[:16]

            records.append({
                "evidence_id": f"EV-{fingerprint}",
                "source": source,
                "signal_code": code,
                "observed_evidence": evidence,
                "confidence": signal.get("confidence", "UNSPECIFIED"),
                "explanation": signal.get(
                    "explanation",
                    "This signal describes an observed URL characteristic."
                ),
                "limitation": (
                    "This observation alone does not prove phishing "
                    "or establish that the website is unsafe."
                ),
                "is_phishing_verdict": False,
            })

    return records
