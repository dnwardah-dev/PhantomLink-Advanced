"""Validated, offline investigation pipeline for PhantomLink V2."""

from app.services.url_validator import validate_url
from app.services.hostname_canonicalizer import canonical_hostname
from app.engine.risk_interpreter_v2 import interpret_url_evidence
from app.engine.evidence_traceability import build_evidence_trace
from app.engine.url_evidence_mapping import build_url_evidence_map


def analyze_url_v2(raw_url: str) -> dict:
    """Analyze validated URL evidence without making network requests."""

    validated_url = validate_url(raw_url)
    hostname = canonical_hostname(validated_url)

    # Use the canonical hostname for downstream analysis.
    # Preserve path and query in the analyzed URL.
    from urllib.parse import urlsplit, urlunsplit

    parsed = urlsplit(validated_url)

    authority = hostname
    if ":" in hostname:
        authority = f"[{hostname}]"

    if parsed.port is not None:
        authority += f":{parsed.port}"

    normalized_url = urlunsplit((
        parsed.scheme.lower(),
        authority,
        parsed.path,
        parsed.query,
        parsed.fragment,
    ))

    interpretation = interpret_url_evidence(normalized_url)
    evidence_trace = build_evidence_trace(interpretation)
    url_evidence_map = build_url_evidence_map(
        normalized_url, evidence_trace
    )

    return {
        "engine": "PHANTOMLINK_V2_PIPELINE",
        "status": "analyzed",
        "hostname": hostname,
        "interpretation": interpretation,
        "evidence_trace": evidence_trace,
        "url_evidence_map": url_evidence_map,
        "normalized_url": normalized_url,
        "network_requests_performed": False,
        "is_phishing_verdict": False,
    }
