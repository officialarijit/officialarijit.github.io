#!/usr/bin/env python3
"""Parse citation.txt (Google Scholar 'Cited by' HTML export) and update _data/scholar.yml."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

SCHOLAR_USER = "4re6DoEAAAAJ"
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_USER}"


def parse_citation_html(html: str) -> dict:
    """Extract metrics and yearly citation counts from a Scholar HTML fragment."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    cells = [(el.get_text() or "").strip() for el in soup.select("td.gsc_rsb_std")]
    if len(cells) < 6:
        raise ValueError(f"Expected at least 6 metric cells, found {len(cells)}")

    metrics = {
        "citations_all": int(cells[0]),
        "citations_since_2021": int(cells[1]),
        "h_index_all": int(cells[2]),
        "h_index_since_2021": int(cells[3]),
        "i10_index_all": int(cells[4]),
        "i10_index_since_2021": int(cells[5]),
    }

    years = [(el.get_text() or "").strip() for el in soup.select("span.gsc_g_t")]
    counts = [(el.get_text() or "").strip() for el in soup.select("span.gsc_g_al")]
    if len(years) != len(counts):
        raise ValueError(f"Year/count mismatch: {len(years)} years vs {len(counts)} counts")

    by_year = [{"year": int(year), "count": int(count)} for year, count in zip(years, counts)]
    return {"metrics": metrics, "by_year": by_year}


def build_scholar_data(
    metrics: dict,
    by_year: list[dict],
    *,
    source: str,
    scholar_url: str = SCHOLAR_URL,
    last_updated: str | None = None,
) -> dict:
    return {
        "source": source,
        "last_updated": last_updated or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "scholar_url": scholar_url,
        "metrics": metrics,
        "by_year": by_year,
    }


def write_scholar_yml(data: dict, output_path: str | Path) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def update_from_citation_fragment(
    input_path: str = "citation.txt",
    output_path: str = "_data/scholar.yml",
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    raw = input_file.read_text(encoding="utf-8", errors="replace")
    parsed = parse_citation_html(raw)
    data = build_scholar_data(
        parsed["metrics"],
        parsed["by_year"],
        source=input_file.name,
    )
    write_scholar_yml(data, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update _data/scholar.yml from citation.txt (Google Scholar HTML export)."
    )
    parser.add_argument("--input", "-i", default="citation.txt", help="Path to citation.txt")
    parser.add_argument("--output", "-o", default="_data/scholar.yml", help="Path to output YAML")
    args = parser.parse_args()
    update_from_citation_fragment(input_path=args.input, output_path=args.output)
    print(f"Updated {args.output} from {args.input}.")
