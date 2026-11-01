"""Conservative URL-to-evidence mapping for PhantomLink V2."""

from urllib.parse import urlsplit


SUPPORTED_RULES = {
    "HOSTNAME_CONTAINS_HYPHEN",
    "HOSTNAME_CONTAINS_DIGITS",
}


def build_url_evidence_map(
    normalized_url: str,
    evidence_trace: list[dict],
) -> list[dict]:
    """Map supported evidence codes to observable hostname characters."""

    hostname = (urlsplit(normalized_url).hostname or "").lower()
    mappings = []

    for record in evidence_trace:
        if not isinstance(record, dict):
            continue

        code = record.get("signal_code")
        evidence_id = record.get("evidence_id")

        if not isinstance(evidence_id, str) or not evidence_id:
            continue

        if record.get("source") != "structural":
            continue

        if code not in SUPPORTED_RULES:
            continue

        if code == "HOSTNAME_CONTAINS_HYPHEN":
            spans = [
                {"start": index, "end": index + 1}
                for index, char in enumerate(hostname)
                if char == "-"
            ]

        elif code == "HOSTNAME_CONTAINS_DIGITS":
            spans = [
                {"start": index, "end": index + 1}
                for index, char in enumerate(hostname)
                if char in "0123456789"
            ]

        else:
            spans = []

        if not spans:
            continue

        mappings.append({
            "evidence_id": evidence_id,
            "signal_code": code,
            "component": "hostname",
            "component_value": hostname,
            "spans": spans,
            "mapping_type": "DIRECT_CHARACTER_MATCH",
            "is_phishing_verdict": False,
        })

    return mappings
