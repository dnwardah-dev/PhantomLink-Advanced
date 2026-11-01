"""Offline registrable-domain overlap audit."""

import csv
import json
from pathlib import Path

import tldextract


# Use the bundled suffix snapshot, not a live HTTP download.
extractor = tldextract.TLDExtract(suffix_list_urls=())


def registrable_domain(hostname: str) -> str:
    result = extractor(hostname)

    if result.domain and result.suffix:
        return f"{result.domain}.{result.suffix}"

    return hostname.lower().rstrip(".")


def load_domains(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = csv.DictReader(file)
        return {
            registrable_domain(row["hostname"])
            for row in rows
            if row.get("hostname")
        }


def audit_domain_overlap(
    phishing_path: Path,
    candidate_path: Path,
    output_path: Path,
) -> dict:
    phishing_domains = load_domains(phishing_path)
    candidate_domains = load_domains(candidate_path)

    overlap = sorted(phishing_domains & candidate_domains)

    report = {
        "phishing_registrable_domains": len(phishing_domains),
        "candidate_registrable_domains": len(candidate_domains),
        "overlapping_registrable_domains": len(overlap),
        "overlap_examples": overlap[:20],
        "note": (
            "This audit detects cross-dataset domain overlap. "
            "It does not yet create train/test splits or verify "
            "legitimate labels."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report
