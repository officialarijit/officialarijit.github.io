#!/usr/bin/env python3
"""Read publications from publications.txt (Google Scholar HTML fragment) and update data/publications.json."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime


SCHOLAR_USER = "4re6DoEAAAAJ"


def _normalize_title(s: str) -> str:
    """Normalize title for matching: strip, collapse spaces, lower."""
    return " ".join(s.split()).lower().strip()


def parse_publications_html(html: str) -> list[dict]:
    """
    Parse Google Scholar table HTML (tbody with tr.gsc_a_tr) into list of publication dicts
    with keys: title, authors, journal, year, citations, paper_url.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("tr.gsc_a_tr")
    out = []

    for tr in rows:
        # Title and link
        a_title = tr.select_one("td.gsc_a_t a.gsc_a_at")
        if not a_title:
            continue
        title = (a_title.get_text() or "").strip()
        href = a_title.get("href") or ""
        paper_url = build_paper_link(href)

        # Two gs_gray divs: authors, then journal/venue
        grays = tr.select("td.gsc_a_t div.gs_gray")
        authors = (grays[0].get_text() or "").strip() if len(grays) > 0 else ""
        journal_node = grays[1] if len(grays) > 1 else None
        journal = ""
        year_from_journal = ""
        if journal_node:
            # Year often in <span class="gs_oph">, 2024</span>
            gs_oph = journal_node.select_one("span.gs_oph")
            if gs_oph:
                year_from_journal = (gs_oph.get_text() or "").strip().strip(",").strip()
            journal = (journal_node.get_text() or "").strip()

        # Year column
        year_span = tr.select_one("td.gsc_a_y span.gsc_a_h")
        year = (year_span.get_text() or "").strip() if year_span else year_from_journal
        if not year:
            year = ""
        # Normalize year (e.g. ", 2024" -> "2024")
        year = re.sub(r"^\D+", "", year).strip() or ""

        # Citations
        cit_a = tr.select_one("td.gsc_a_c a.gsc_a_ac")
        citations = 0
        if cit_a:
            raw = (cit_a.get_text() or "").strip()
            if raw.isdigit():
                citations = int(raw)

        out.append({
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "citations": citations,
            "paper_url": paper_url,
        })
    return out


def build_paper_link(href: str) -> str:
    """Build full scholar citation URL from anchor href."""
    if not href:
        return ""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://scholar.google.com{href}"
    return href


def compute_metrics(publications: list[dict]) -> dict:
    """Compute total_citations, h_index, i10_index from publication list."""
    citations = sorted((p.get("citations") or 0) for p in publications)
    citations_desc = sorted(citations, reverse=True)
    total = sum(citations)
    h = 0
    for i, c in enumerate(citations_desc, 1):
        if c >= i:
            h = i
        else:
            break
    i10 = sum(1 for c in citations if c >= 10)
    return {"total_citations": total, "h_index": h, "i10_index": i10}


def publication_to_json_entry(p: dict) -> dict:
    """Convert parsed entry to JSON shape expected by the site (with links.paper, links.code)."""
    return {
        "year": p.get("year") or "",
        "title": p.get("title") or "",
        "authors": p.get("authors") or "",
        "journal": p.get("journal") or "",
        "citations": p.get("citations") or 0,
        "links": {
            "paper": p.get("paper_url") or "",
            "code": None,
        },
    }


def update_from_publications_fragment(
    input_path: str = "publications.txt",
    output_path: str = "data/publications.json",
    merge: bool = True,
    recompute_metrics: bool = True,
) -> None:
    """
    Read Google Scholar HTML fragment from input_path, parse it, and update output_path JSON.

    - If merge is True: load existing JSON, match publications by title+year, update
      citations/links from fragment, and append new entries. Profile and unmatched
      existing entries are preserved.
    - If merge is False: replace publications list entirely with parsed data (profile
      and metrics are still taken from existing file when possible).
    - If recompute_metrics is True: set metrics from current citation counts.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    raw = input_file.read_text(encoding="utf-8", errors="replace")
    parsed = parse_publications_html(raw)
    new_entries = [publication_to_json_entry(p) for p in parsed]

    existing = {}
    if output_file.exists() and merge:
        existing_data = json.loads(output_file.read_text(encoding="utf-8"))
        existing = existing_data
    else:
        existing = {
            "profile": {
                "scholar_id": SCHOLAR_USER,
                "scholar_url": f"https://scholar.google.com/citations?hl=en&user={SCHOLAR_USER}&view_op=list_works&sortby=pubdate",
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
            },
            "publications": [],
            "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
        }

    def _sort_key(p):
        y = p.get("year") or ""
        year_val = -int(y) if y.isdigit() else 0
        return (year_val, (p.get("title") or "").lower())

    if merge and existing.get("publications"):
        # Match by normalized title + year; keep order from new list, then append unseen existing
        by_key = {}
        for pub in existing["publications"]:
            key = (_normalize_title(pub.get("title") or ""), (pub.get("year") or "").strip())
            by_key[key] = pub

        merged = []
        seen_keys = set()
        for entry in new_entries:
            key = (_normalize_title(entry.get("title") or ""), (entry.get("year") or "").strip())
            if key in by_key:
                old = by_key[key]
                # Prefer new citation count and paper link
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
        merged.sort(key=_sort_key)
        publications = merged
    else:
        # Replace with new list; sort by year desc
        publications = sorted(new_entries, key=_sort_key)

    if recompute_metrics:
        existing["metrics"] = compute_metrics(publications)

    existing["profile"] = existing.get("profile") or {}
    existing["profile"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d")
    existing["publications"] = publications

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update publications.json from publications.txt (Google Scholar HTML).")
    parser.add_argument("--input", "-i", default="publications.txt", help="Path to publications.txt (HTML fragment)")
    parser.add_argument("--output", "-o", default="data/publications.json", help="Path to output JSON")
    parser.add_argument("--no-merge", action="store_true", help="Replace publications instead of merging")
    parser.add_argument("--no-metrics", action="store_true", help="Do not recompute metrics")
    args = parser.parse_args()
    update_from_publications_fragment(
        input_path=args.input,
        output_path=args.output,
        merge=not args.no_merge,
        recompute_metrics=not args.no_metrics,
    )
    print(f"Updated {args.output} from {args.input}.")
