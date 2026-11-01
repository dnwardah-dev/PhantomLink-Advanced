"""Offline dataset cleaning for URL investigation research."""

import csv
import json
from pathlib import Path
from urllib.parse import urlsplit


def normalize_url(url: str) -> str | None:
    try:
        parsed = urlsplit(url.strip())

        if parsed.scheme.lower() not in ("http", "https"):
            return None

        hostname = (parsed.hostname or "").lower().rstrip(".")
        if not hostname:
            return None

        port = parsed.port
        authority = hostname if port is None else f"{hostname}:{port}"

        if ":" in hostname and not hostname.startswith("["):
            authority = f"[{hostname}]" + (
                f":{port}" if port is not None else ""
            )

        path = parsed.path or "/"

        return (
            f"{parsed.scheme.lower()}://{authority}"
            f"{path}"
            + (f"?{parsed.query}" if parsed.query else "")
        )

    except (ValueError, AttributeError):
        return None


def read_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required = {"url", "label", "source"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing required columns in {path}")

        rows = []

        for row in reader:
            normalized = normalize_url(row["url"] or "")

            if normalized is None:
                continue

            rows.append({
                "url": normalized,
                "hostname": urlsplit(normalized).hostname,
                "label": row["label"],
                "source": row["source"],
            })

        return rows


def unique_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    unique = []

    for row in rows:
        if row["url"] not in seen:
            seen.add(row["url"])
            unique.append(row)

    return unique


def clean_datasets(
    phishing_path: Path,
    candidate_path: Path,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    phishing = unique_rows(read_dataset(phishing_path))
    candidates = unique_rows(read_dataset(candidate_path))

    phishing_hosts = {row["hostname"] for row in phishing}
    candidate_hosts = {row["hostname"] for row in candidates}

    overlaps = phishing_hosts & candidate_hosts

    clean_phishing = [
        row for row in phishing
        if row["hostname"] not in overlaps
    ]

    clean_candidates = [
        row for row in candidates
        if row["hostname"] not in overlaps
    ]

    for filename, rows in [
        ("phishing_clean.csv", clean_phishing),
        ("legitimate_candidates_clean.csv", clean_candidates),
    ]:
        output = output_dir / filename

        with output.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["url", "hostname", "label", "source"],
            )
            writer.writeheader()
            writer.writerows(rows)

    report = {
        "phishing_unique": len(phishing),
        "legitimate_candidates_unique": len(candidates),
        "overlapping_hostnames": len(overlaps),
        "phishing_after_cleaning": len(clean_phishing),
        "legitimate_candidates_after_cleaning": len(clean_candidates),
        "limitations": [
            "Candidate legitimate labels are not verified.",
            "Exact hostname overlap removal does not prevent "
            "cross-subdomain or registrable-domain leakage.",
            "No phishing URLs were visited.",
        ],
    }

    (output_dir / "cleaning_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report
