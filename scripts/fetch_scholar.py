#!/usr/bin/env python3
"""Fetch Google Scholar profile data and update site data files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from update_publications import (
    SCHOLAR_USER,
    compute_metrics,
    publication_to_json_entry,
)
from update_scholar import SCHOLAR_URL, build_scholar_data, write_scholar_yml


def build_paper_link(author_pub_id: str) -> str:
    if not author_pub_id:
        return ""
    return (
        "https://scholar.google.com/citations"
        f"?view_op=view_citation&hl=en&user={SCHOLAR_USER}"
        f"&sortby=pubdate&citation_for_view={author_pub_id}"
    )


def scholarly_publication_to_entry(pub: dict) -> dict:
    bib = pub.get("bib") or {}
    return publication_to_json_entry(
        {
            "title": bib.get("title") or "",
            "authors": bib.get("author") or "",
            "journal": bib.get("journal") or bib.get("citation") or "",
            "year": str(bib.get("pub_year") or "").strip(),
            "citations": int(pub.get("num_citations") or 0),
            "paper_url": build_paper_link(pub.get("author_pub_id") or ""),
        }
    )


def fetch_author(scholar_id: str) -> dict:
    from scholarly import scholarly

    author = scholarly.search_author_id(scholar_id)
    return scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])


def author_to_scholar_data(author: dict) -> dict:
    cites_per_year = author.get("cites_per_year") or {}
    by_year = [
        {"year": int(year), "count": int(count)}
        for year, count in sorted(cites_per_year.items(), key=lambda item: int(item[0]))
    ]
    metrics = {
        "citations_all": int(author.get("citedby") or 0),
        "citations_since_2021": int(author.get("citedby5y") or author.get("citedby") or 0),
        "h_index_all": int(author.get("hindex") or 0),
        "h_index_since_2021": int(author.get("hindex5y") or author.get("hindex") or 0),
        "i10_index_all": int(author.get("i10index") or 0),
        "i10_index_since_2021": int(author.get("i10index5y") or author.get("i10index") or 0),
    }
    return build_scholar_data(metrics, by_year, source="scholarly")


def update_publications_from_author(author: dict, output_path: str | Path) -> None:
    output_file = Path(output_path)
    publications = [scholarly_publication_to_entry(pub) for pub in author.get("publications") or []]

    existing = {}
    if output_file.exists():
        existing = json.loads(output_file.read_text(encoding="utf-8"))

    if not existing:
        existing = {
            "profile": {
                "scholar_id": SCHOLAR_USER,
                "scholar_url": (
                    f"https://scholar.google.com/citations?hl=en&user={SCHOLAR_USER}"
                    "&view_op=list_works&sortby=pubdate"
                ),
                "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            "publications": [],
            "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
        }

    by_key = {}
    for pub in existing.get("publications") or []:
        key = (" ".join((pub.get("title") or "").split()).lower(), (pub.get("year") or "").strip())
        by_key[key] = pub

    merged = []
    seen_keys = set()
    for entry in publications:
        key = (" ".join((entry.get("title") or "").split()).lower(), (entry.get("year") or "").strip())
        if key in by_key:
            old = by_key[key]
            entry["citations"] = entry.get("citations") or old.get("citations") or 0
            if not entry.get("links", {}).get("paper") and old.get("links", {}).get("paper"):
                entry.setdefault("links", {})["paper"] = old["links"]["paper"]
            if old.get("links", {}).get("code") is not None:
                entry.setdefault("links", {})["code"] = old["links"]["code"]
        merged.append(entry)
        seen_keys.add(key)

    for key, pub in by_key.items():
        if key not in seen_keys:
            merged.append(pub)

    def sort_key(pub: dict) -> tuple:
        year = pub.get("year") or ""
        year_val = -int(year) if str(year).isdigit() else 0
        return (year_val, (pub.get("title") or "").lower())

    merged.sort(key=sort_key)
    existing["publications"] = merged
    existing["metrics"] = compute_metrics(merged)
    existing["profile"] = existing.get("profile") or {}
    existing["profile"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing["profile"]["scholar_id"] = SCHOLAR_USER

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_and_update(
    scholar_id: str = SCHOLAR_USER,
    scholar_output: str = "_data/scholar.yml",
    publications_output: str = "data/publications.json",
) -> None:
    author = fetch_author(scholar_id)
    scholar_data = author_to_scholar_data(author)
    write_scholar_yml(scholar_data, scholar_output)
    update_publications_from_author(author, publications_output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Google Scholar data and update site files.")
    parser.add_argument("--scholar-id", default=SCHOLAR_USER, help="Google Scholar user ID")
    parser.add_argument("--scholar-output", default="_data/scholar.yml", help="Output scholar YAML path")
    parser.add_argument(
        "--publications-output",
        default="data/publications.json",
        help="Output publications JSON path",
    )
    args = parser.parse_args()

    try:
        fetch_and_update(
            scholar_id=args.scholar_id,
            scholar_output=args.scholar_output,
            publications_output=args.publications_output,
        )
    except Exception as exc:
        print(f"Scholar fetch failed: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {args.scholar_output} and {args.publications_output} from Google Scholar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
