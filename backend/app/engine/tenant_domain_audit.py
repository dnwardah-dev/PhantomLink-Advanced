"""Tenant-aware offline domain overlap audit."""

import csv
import json
from pathlib import Path

import tldextract


extractor = tldextract.TLDExtract(
    suffix_list_urls=(),
    include_psl_private_domains=True,
)


def domain_group(hostname: str) -> str:
    hostname = hostname.strip().lower().rstrip(".")
    result = extractor(hostname)

    if result.domain and result.suffix:
        return f"{result.domain}.{result.suffix}"

    return hostname


def load_groups(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        return {
            domain_group(row["hostname"])
            for row in reader
            if row.get("hostname")
        }


def audit_tenant_domains(
    phishing_path: Path,
    candidate_path: Path,
    output_path: Path,
) -> dict:
    phishing = load_groups(phishing_path)
    candidates = load_groups(candidate_path)

    overlap = sorted(phishing & candidates)

    report = {
        "phishing_domain_groups": len(phishing),
        "candidate_domain_groups": len(candidates),
        "overlapping_domain_groups": len(overlap),
        "overlap_examples": overlap[:30],
        "private_suffixes_enabled": True,
        "limitations": [
            "Public Suffix List private section is not exhaustive.",
            "Shared infrastructure can still create label ambiguity.",
            "Legitimate candidate labels remain unverified.",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report
