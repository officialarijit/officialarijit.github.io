#!/usr/bin/env python3
"""
Google Scholar Publications Updater
This script helps you update your publications.json file with data from Google Scholar.

The script uses the 'scholarly' library for reliable Google Scholar access,
with a fallback to direct scraping if needed.

Usage:
    # Simple mode (default): parse publications.txt (Google Scholar HTML fragment)
    python update_publications.py
    # or specify paths / options
    python update_publications.py --input publications.txt --output data/publications.json [--replace] [--no-metrics]

    # Other import modes (optional):
    python update_publications.py --from-html path/to/scholar_list_works.html [--merge]
    python update_publications.py --from-bibtex path/to/publications.bib [--merge]
    python update_publications.py --homepage-html path/to/homepage.html

Requirements:
    pip install -r requirements.txt
    # or
    pip install requests beautifulsoup4 scholarly
"""

import json
import re
import time
import argparse
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os

import requests
from bs4 import BeautifulSoup

VERBOSE = False
TOR_ENABLED = False
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = ""

try:
    from scholarly import scholarly, ProxyGenerator
    SCHOLARLY_AVAILABLE = True
except ImportError:
    try:
        from scholarly import scholarly
        ProxyGenerator = None
        SCHOLARLY_AVAILABLE = True
    except ImportError:
        SCHOLARLY_AVAILABLE = False
        ProxyGenerator = None
        print("⚠️  scholarly library not installed. Some features may be limited.")


def setup_scholarly_with_retry():
    """
    Setup scholarly with various methods to bypass blocks.
    Returns True if setup succeeded, False otherwise.
    """
    if not SCHOLARLY_AVAILABLE:
        return False
    
    try:
        # Method 0: Try Tor if requested
        if ProxyGenerator and TOR_ENABLED:
            try:
                print("   Trying to setup Tor proxy...")
                pg = ProxyGenerator()
                pg.Tor_External(
                    tor_sock_port=TOR_SOCKS_PORT,
                    tor_control_port=TOR_CONTROL_PORT,
                    tor_password=TOR_PASSWORD or None,
                )
                scholarly.use_proxy(pg)
                print("   ✓ Using Tor proxy")
                return True
            except Exception as e:
                print(f"   ⚠️ Tor setup failed: {e}")

        # Method 1: Try with free proxy
        if ProxyGenerator:
            print("   Trying to setup free proxy...")
            pg = ProxyGenerator()
            success = pg.FreeProxies()
            if success:
                scholarly.use_proxy(pg)
                print("   ✓ Using free proxy")
                return True
        
        # Method 2: Try with Tor (if available)
        # Uncomment if you have Tor installed:
        # if ProxyGenerator:
        #     pg = ProxyGenerator()
        #     pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
        #     scholarly.use_proxy(pg)
        #     return True
        
        # Method 3: No proxy (will likely fail but worth a try)
        print("   No proxy available, trying direct connection...")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Proxy setup failed: {e}")
        return True  # Still try without proxy


# --- SerpAPI integration ---
try:
    from serpapi import GoogleSearch  # type: ignore
    SERPAPI_AVAILABLE = True
except Exception:
    SERPAPI_AVAILABLE = False


def _get_serpapi_key(cli_key: str | None) -> str | None:
    key = cli_key or os.getenv("SERPAPI_API_KEY")
    if not key:
        print("⚠️  SERPAPI_API_KEY not set. Provide --serpapi-key or set env var.")
    return key


def fetch_publications_with_serpapi(scholar_id: str, api_key: str) -> list[dict] | None:
    if not SERPAPI_AVAILABLE:
        print("⚠️  SerpAPI client not installed. Run: pip install google-search-results")
        return None
    try:
        publications = []
        start = 0
        page = 1
        while True:
            params = {
                "engine": "google_scholar_author",
                "author_id": scholar_id,
                "api_key": api_key,
                "hl": "en",
                "sort": "pb",  # sort by pubdate
                "num": 100,
                "start": start,
            }
            search = GoogleSearch(params)
            result = search.get_dict()
            articles = (result or {}).get("articles", [])
            if not articles:
                break
            for art in articles:
                title = art.get("title", "")
                year = str(art.get("year", "") or "").strip()
                cited_by = (art.get("cited_by") or {}).get("value", 0) or 0
                publication = art.get("publication", "") or ""
                # authors may be list of dicts or string depending on SerpAPI version
                authors_field = art.get("authors")
                if isinstance(authors_field, list):
                    authors = ", ".join([a.get("name", "") for a in authors_field if isinstance(a, dict)])
                else:
                    authors = authors_field or ""
                link = art.get("link") or (art.get("resources", [{}])[0].get("link") if art.get("resources") else None)
                pub_obj = {
                    "year": year,
                    "title": title,
                    "authors": authors,
                    "journal": publication,
                    "citations": int(cited_by),
                    "links": {"paper": link, "code": None},
                }
                if title and year:
                    publications.append(pub_obj)
            if len(articles) < 100:
                break
            start += 100
            page += 1
            time.sleep(0.5)
        return publications or None
    except Exception as e:
        print(f"❌ SerpAPI publications fetch failed: {e}")
        if VERBOSE:
            import traceback
            traceback.print_exc()
        return None


def compute_metrics_from_publications(publications: list[dict]) -> dict:
    citations_list = sorted([int(p.get("citations", 0) or 0) for p in publications], reverse=True)
    total = sum(citations_list)
    h = 0
    for i, c in enumerate(citations_list, 1):
        if c >= i:
            h = i
        else:
            break
    i10 = sum(1 for c in citations_list if c >= 10)
    return {"total_citations": total, "h_index": h, "i10_index": i10}

def normalize_title(title: str) -> str:
    """Normalize a title string for comparison/merging."""
    if not title:
        return ""
    lowered = title.lower().strip()
    # Remove non-alphanumeric except spaces
    return re.sub(r"[^a-z0-9\s]", "", lowered)


def merge_publication_lists(existing_list, new_list):
    """
    Merge two publications lists by normalized title.
    - Updates citations if new has higher value
    - Fills missing authors/journal/links from new
    - Keeps year from existing unless new provides a valid year
    Returns merged list sorted by year desc.
    """
    existing_by_title = {normalize_title(p.get("title", "")): dict(p) for p in (existing_list or [])}
    for pub in new_list or []:
        key = normalize_title(pub.get("title", ""))
        if not key:
            continue
        if key in existing_by_title:
            cur = existing_by_title[key]
            # Update citations to max
            cur["citations"] = max(int(cur.get("citations", 0) or 0), int(pub.get("citations", 0) or 0))
            # Prefer non-empty fields
            for field in ("authors", "journal"):
                if not cur.get(field) and pub.get(field):
                    cur[field] = pub[field]
            # Update year if current missing/invalid and new is valid
            if (not cur.get("year")) or (not re.match(r"^\d{4}$", str(cur.get("year")))):
                if pub.get("year") and re.match(r"^\d{4}$", str(pub.get("year"))):
                    cur["year"] = str(pub.get("year"))
            # Merge links
            cur_links = cur.get("links", {}) or {}
            new_links = pub.get("links", {}) or {}
            cur_links.setdefault("paper", new_links.get("paper"))
            cur_links.setdefault("code", new_links.get("code"))
            cur["links"] = cur_links
            existing_by_title[key] = cur
        else:
            existing_by_title[key] = dict(pub)
    merged = list(existing_by_title.values())
    # Clean and sort
    merged = clean_publications_data(merged)
    return merged


def parse_publications_from_saved_html(html_content: str):
    """Parse publications from a saved Google Scholar publications page HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    pubs = []
    rows = soup.select("tr.gsc_a_tr") or soup.select(".gsc_a_tr") or []
    for row in rows:
        pub = parse_publication_entry(row, soup)
        if pub and pub.get("title"):
            pubs.append(pub)
    # Deduplicate
    seen = set()
    unique = []
    for p in pubs:
        t = normalize_title(p["title"]) 
        if t not in seen:
            seen.add(t)
            unique.append(p)
    return unique


def parse_metrics_from_homepage_html(html_content: str):
    """Parse metrics (total citations, h-index, i10-index) from saved Scholar homepage HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    metrics = {}
    cells = soup.find_all("td", class_="gsc_rsb_std")
    if cells:
        try:
            if len(cells) >= 1:
                metrics["total_citations"] = int(re.search(r"(\d+)", cells[0].get_text(strip=True)).group(1))
            if len(cells) >= 2:
                metrics["h_index"] = int(re.search(r"(\d+)", cells[1].get_text(strip=True)).group(1))
            if len(cells) >= 3:
                metrics["i10_index"] = int(re.search(r"(\d+)", cells[2].get_text(strip=True)).group(1))
        except Exception:
            pass
    if not metrics:
        # Fallback: search text
        text = soup.get_text(" ")
        m = re.search(r"Citations\s*(\d+)", text, re.I)
        if m:
            metrics["total_citations"] = int(m.group(1))
        m = re.search(r"h-index\s*(\d+)", text, re.I)
        if m:
            metrics["h_index"] = int(m.group(1))
        m = re.search(r"i10-index\s*(\d+)", text, re.I)
        if m:
            metrics["i10_index"] = int(m.group(1))
    return metrics or None


def parse_publications_from_bibtex(bibtex_text: str):
    """Very lightweight BibTeX parser for common fields."""
    entries = re.split(r"@\w+\s*\{", bibtex_text)[1:]
    pubs = []
    for raw in entries:
        body = raw.split("}", 1)[-1] if "}" in raw else raw
        get = lambda field: _extract_bib_field(raw, field)
        title = get("title")
        year = get("year")
        authors = get("author")
        journal = get("journal") or get("booktitle") or ""
        url = get("url") or None
        if title and year:
            pubs.append({
                "year": str(year),
                "title": title,
                "authors": authors or "",
                "journal": journal or "",
                "citations": 0,
                "links": {"paper": url, "code": None}
            })
    return pubs


def _extract_bib_field(raw: str, field: str) -> str:
    """Extract a BibTeX field value as plain text."""
    m = re.search(r"\b" + re.escape(field) + r"\s*=\s*(\{([^{}]*)\}|\"([^\"]*)\")", raw, re.I)
    if not m:
        return ""
    val = m.group(2) or m.group(3) or ""
    return val.strip().strip("{}")


def parse_publications_from_text(text: str):
    """
    Parse a simple text export with repeating 4-line blocks:
    title\nauthors\nvenue\n( [citations]\t )year
    Lines without citations will just contain the year.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Drop header lines if present
    if lines and lines[0].lower().startswith("title"):
        # heuristic: first 3 lines are headers
        lines = lines[3:]
    publications = []
    i = 0
    n = len(lines)
    while i + 3 < n:
        title = lines[i]
        authors = lines[i + 1]
        venue = lines[i + 2]
        tail = lines[i + 3]
        i += 4
        citations = 0
        year = ""
        if "\t" in tail:
            parts = tail.split("\t")
            if len(parts) == 2 and parts[1].isdigit():
                try:
                    citations = int(parts[0].strip() or 0)
                except Exception:
                    citations = 0
                year = parts[1].strip()
        elif re.fullmatch(r"\d{4}", tail):
            year = tail
        else:
            # If format unexpected, try to locate a year in tail
            m = re.search(r"(\d{4})", tail)
            if m:
                year = m.group(1)
        if not title or not year:
            continue
        publications.append({
            "year": str(year),
            "title": title,
            "authors": authors or "",
            "journal": venue or "",
            "citations": int(citations or 0),
            "links": {"paper": None, "code": None},
        })
    # Deduplicate by title
    return merge_publication_lists([], publications)


def update_from_publications_fragment(
    input_path: str = "publications.txt",
    output_path: str = "data/publications.json",
    merge: bool = True,
    recompute_metrics: bool = True,
):
    """Parse GS HTML fragment at input_path and update output JSON."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            frag_html = f.read()
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_path}")
        return

    new_pubs = parse_publications_from_saved_html(frag_html)
    if not new_pubs:
        print("⚠️  No publications found in input fragment.")
        return

    existing = load_existing_publications() or {
        "profile": {
            "scholar_id": "4re6DoEAAAAJ",
            "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        },
        "publications": [],
        "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
    }

    if merge:
        updated_pubs = merge_publication_lists(existing.get("publications", []), new_pubs)
    else:
        updated_pubs = clean_publications_data(new_pubs)

    existing["publications"] = updated_pubs

    if recompute_metrics:
        try:
            existing["metrics"] = compute_metrics_from_publications(updated_pubs)
        except Exception:
            pass

    existing["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Save to output_path (respecting default data/publications.json)
    if output_path != "data/publications.json":
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            print(f"✅ Publications saved to {output_path}")
            return
        except Exception as e:
            print(f"❌ Error saving to {output_path}: {e}")

    save_publications(existing)

def fetch_publications_with_scholarly(scholar_id):
    """
    Fetch publications using the scholarly library (more reliable).
    """
    if not SCHOLARLY_AVAILABLE:
        return None
    
    try:
        print("🔄 Fetching publications using scholarly library...")
        print(f"   Looking up Scholar ID: {scholar_id}")
        
        # Setup proxy/retry mechanism
        setup_scholarly_with_retry()
        
        # Add a small delay to be respectful
        time.sleep(2)
        
        # Search for author by ID
        author = scholarly.search_author_id(scholar_id)
        
        if author is None:
            print("⚠️  Author not found with scholarly library")
            return None
        
        print(f"   Found author: {author.get('name', 'Unknown')}")
        
        # Fill the author information with publications
        author = scholarly.fill(author, sections=['publications', 'basics'])
        
        if not author:
            print("⚠️  Could not fill author information")
            return None
        
        publications = []
        pub_list = author.get('publications', [])
        print(f"   Processing {len(pub_list)} publications...")
        
        # Process each publication
        for i, pub in enumerate(pub_list, 1):
            try:
                print(f"   [{i}/{len(pub_list)}] Processing publication...", end='\r')
                
                # Fill publication details
                pub_filled = scholarly.fill(pub)
                
                if not pub_filled:
                    continue
                
                # Extract year
                year = pub_filled.get('bib', {}).get('pub_year', '')
                if not year:
                    # Try to extract from citation
                    citation = pub_filled.get('bib', {}).get('citation', '')
                    year_match = re.search(r'(\d{4})', citation)
                    if year_match:
                        year = year_match.group(1)
                
                # Build publication object
                publication = {
                    "year": str(year),
                    "title": pub_filled.get('bib', {}).get('title', ''),
                    "authors": pub_filled.get('bib', {}).get('author', ''),
                    "journal": pub_filled.get('bib', {}).get('venue', '') or pub_filled.get('bib', {}).get('journal', ''),
                    "citations": pub_filled.get('num_citations', 0),
                    "links": {
                        "paper": pub_filled.get('pub_url') or pub_filled.get('eprint_url'),
                        "code": None  # scholarly doesn't typically provide code links
                    }
                }
                
                if publication['title'] and publication['year']:
                    publications.append(publication)
                    
            except Exception as e:
                print(f"\n⚠️  Error processing publication {i}: {e}")
                continue
        
        print(f"\n✅ Successfully fetched {len(publications)} publications")
        return publications if publications else None
        
    except Exception as e:
        print(f"❌ Error with scholarly library: {e}")
        if VERBOSE:
            import traceback
            traceback.print_exc()
        return None


def fetch_metrics_with_scholarly(scholar_id):
    """
    Fetch citation metrics using the scholarly library (more reliable).
    """
    if not SCHOLARLY_AVAILABLE:
        return None
    
    try:
        print("🔄 Fetching metrics using scholarly library...")
        print(f"   Looking up Scholar ID: {scholar_id}")
        
        # Setup proxy/retry mechanism
        setup_scholarly_with_retry()
        
        # Add a small delay to be respectful
        time.sleep(2)
        
        # Search for author by ID
        author = scholarly.search_author_id(scholar_id)
        
        if author is None:
            print("⚠️  Author not found with scholarly library")
            return None
        
        print(f"   Found author: {author.get('name', 'Unknown')}")
        
        # Fill the author information
        author = scholarly.fill(author, sections=['basics', 'indices'])
        
        if not author:
            print("⚠️  Could not fill author information")
            return None
        
        metrics = {
            "total_citations": author.get('citedby', 0),
            "h_index": author.get('hindex', 0),
            "i10_index": author.get('i10index', 0)
        }
        
        print(f"✅ Found metrics: {metrics}")
        return metrics
        
    except Exception as e:
        print(f"❌ Error fetching metrics with scholarly: {e}")
        if VERBOSE:
            import traceback
            traceback.print_exc()
        return None


def fetch_google_scholar_publications(scholar_id):
    """
    Attempt to fetch publications from Google Scholar.
    Tries scholarly library first, then falls back to direct scraping.
    """
    # Try scholarly library first (more reliable)
    if SCHOLARLY_AVAILABLE:
        publications = fetch_publications_with_scholarly(scholar_id)
        if publications:
            return publications
        print("⚠️  Scholarly library failed, trying fallback method...")
    
    # Fallback to direct scraping
    url = f"https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=list_works&sortby=pubdate"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        print("🔄 Fetching publications from Google Scholar (fallback method)...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Add a small delay to be respectful
        time.sleep(2)
        
        soup = BeautifulSoup(response.content, "html.parser")
        publications = []
        
        # Try multiple selectors for publication entries
        selectors = [
            "tr.gsc_a_tr",
            ".gsc_a_tr",
            "tr[class*='gsc_a']",
            ".gs_r.gs_or.gs_scl"
        ]
        
        pub_entries = []
        for selector in selectors:
            pub_entries = soup.select(selector)
            if pub_entries:
                print(f"✅ Found {len(pub_entries)} publications using selector: {selector}")
                break
        
        if not pub_entries:
            # Fallback: look for any table rows that might contain publications
            pub_entries = soup.find_all("tr")
            print(f"⚠️  Using fallback method, found {len(pub_entries)} potential entries")
        
        for entry in pub_entries:
            try:
                publication = parse_publication_entry(entry, soup)
                if publication and publication.get('title'):
                    publications.append(publication)
            except Exception as e:
                print(f"⚠️  Error parsing entry: {e}")
                continue
        
        # Remove duplicates based on title
        unique_publications = []
        seen_titles = set()
        for pub in publications:
            title_normalized = pub['title'].lower().strip()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_publications.append(pub)
        
        print(f"✅ Successfully parsed {len(unique_publications)} unique publications")
        return unique_publications

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching publications: {e}")
        return None


def parse_publication_entry(entry, soup):
    """
    Parse a single publication entry with multiple fallback methods.
    """
    publication = {
        "year": "",
        "title": "",
        "authors": "",
        "journal": "",
        "citations": 0,
        "links": {"paper": None, "code": None}
    }
    
    # Method 1: Standard Google Scholar structure
    title_elem = entry.find("a", class_="gsc_a_at") or entry.find("a", class_="gs_rt")
    if title_elem:
        publication["title"] = title_elem.get_text(strip=True)
        href = title_elem.get("href")
        if href:
            publication["links"]["paper"] = urljoin("https://scholar.google.com", href)
    
    # Method 2: Alternative title selectors
    if not publication["title"]:
        title_selectors = [
            ".gs_rt a",
            "h3 a",
            ".title a",
            "a[href*='citation']"
        ]
        for selector in title_selectors:
            title_elem = entry.select_one(selector)
            if title_elem:
                publication["title"] = title_elem.get_text(strip=True)
                href = title_elem.get("href")
                if href:
                    publication["links"]["paper"] = urljoin("https://scholar.google.com", href)
                break
    
    # Extract authors and journal info
    gray_elements = entry.find_all("div", class_="gs_gray") or entry.find_all("div", class_="gs_a")
    if gray_elements:
        if len(gray_elements) >= 1:
            publication["authors"] = gray_elements[0].get_text(strip=True)
        if len(gray_elements) >= 2:
            publication["journal"] = gray_elements[1].get_text(strip=True)
    
    # Alternative method for authors/journal
    if not publication["authors"] or not publication["journal"]:
        text_elements = entry.find_all("div", class_="gs_a") or entry.find_all("div", class_="gs_gray")
        if text_elements:
            text_content = " ".join([elem.get_text(strip=True) for elem in text_elements])
            # Try to separate authors and journal
            parts = text_content.split(" - ")
            if len(parts) >= 2:
                publication["authors"] = parts[0].strip()
                publication["journal"] = parts[1].strip()
            else:
                publication["authors"] = text_content
    
    # Extract year
    year_elem = entry.find("span", class_="gsc_a_h") or entry.find("span", class_="gs_oph")
    if year_elem:
        year_text = year_elem.get_text(strip=True)
        year_match = re.search(r'(\d{4})', year_text)
        if year_match:
            publication["year"] = year_match.group(1)
    
    # Extract citations
    citations_elem = entry.find("a", class_="gsc_a_ac") or entry.find("a", class_="gs_fl")
    if citations_elem:
        citations_text = citations_elem.get_text(strip=True)
        citations_match = re.search(r'(\d+)', citations_text)
        if citations_match:
            publication["citations"] = int(citations_match.group(1))
    
    # Alternative citation extraction
    if publication["citations"] == 0:
        citation_selectors = [
            ".gs_fl a[href*='citations']",
            ".gsc_a_ac",
            "a[href*='citation']"
        ]
        for selector in citation_selectors:
            cit_elem = entry.select_one(selector)
            if cit_elem:
                cit_text = cit_elem.get_text(strip=True)
                cit_match = re.search(r'(\d+)', cit_text)
                if cit_match:
                    publication["citations"] = int(cit_match.group(1))
                    break
    
    # Clean up data
    publication["title"] = publication["title"].strip()
    publication["authors"] = publication["authors"].strip()
    publication["journal"] = publication["journal"].strip()
    
    # Validate publication has essential data
    if not publication["title"] or not publication["year"]:
        return None
    
    return publication


def fetch_google_scholar_metrics(scholar_id):
    """
    Attempt to fetch citation metrics from Google Scholar.
    Tries scholarly library first, then falls back to direct scraping.
    """
    # Try scholarly library first (more reliable)
    if SCHOLARLY_AVAILABLE:
        metrics = fetch_metrics_with_scholarly(scholar_id)
        if metrics:
            return metrics
        print("⚠️  Scholarly library failed, trying fallback method...")
    
    # Fallback to direct scraping
    url = f"https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=homepage"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        print("🔄 Fetching citation metrics from Google Scholar (fallback method)...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        time.sleep(2)
        
        soup = BeautifulSoup(response.content, "html.parser")
        metrics = {}
        
        # Method 1: Look for metrics in table cells
        metric_cells = soup.find_all("td", class_="gsc_rsb_std")
        if metric_cells:
            for i, cell in enumerate(metric_cells):
                text = cell.get_text(strip=True)
                number_match = re.search(r'(\d+)', text)
                if number_match:
                    if i == 0:
                        metrics["total_citations"] = int(number_match.group(1))
                    elif i == 1:
                        metrics["h_index"] = int(number_match.group(1))
                    elif i == 2:
                        metrics["i10_index"] = int(number_match.group(1))
        
        # Method 2: Look for metrics in text content
        if not metrics:
            page_text = soup.get_text()
            
            # Total citations
            citations_match = re.search(r'Citations\s*(\d+)', page_text, re.IGNORECASE)
            if citations_match:
                metrics["total_citations"] = int(citations_match.group(1))
            
            # h-index
            h_index_match = re.search(r'h-index\s*(\d+)', page_text, re.IGNORECASE)
            if h_index_match:
                metrics["h_index"] = int(h_index_match.group(1))
            
            # i10-index
            i10_index_match = re.search(r'i10-index\s*(\d+)', page_text, re.IGNORECASE)
            if i10_index_match:
                metrics["i10_index"] = int(i10_index_match.group(1))
        
        # Method 3: Look for metrics in specific divs
        if not metrics:
            metric_divs = soup.find_all("div", class_="gs_rsb_std")
            for div in metric_divs:
                text = div.get_text(strip=True)
                number_match = re.search(r'(\d+)', text)
                if number_match:
                    if "citation" in text.lower():
                        metrics["total_citations"] = int(number_match.group(1))
                    elif "h-index" in text.lower():
                        metrics["h_index"] = int(number_match.group(1))
                    elif "i10" in text.lower():
                        metrics["i10_index"] = int(number_match.group(1))
        
        if metrics:
            print(f"✅ Found metrics: {metrics}")
            return metrics
        else:
            print("⚠️  No metrics found")
            return None

    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")
        return None


def load_existing_publications():
    """Load existing publications from JSON file."""
    try:
        with open("data/publications.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  No existing publications.json found")
        return None
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in publications.json")
        return None


def save_publications(data):
    """Save publications data to JSON file."""
    try:
        with open("data/publications.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Publications saved to data/publications.json")
    except Exception as e:
        print(f"❌ Error saving publications: {e}")


def clean_publications_data(publications):
    """
    Clean and validate publications data.
    """
    cleaned = []
    for pub in publications:
        # Ensure required fields
        if not pub.get('title') or not pub.get('year'):
            continue
        
        # Clean and standardize data
        cleaned_pub = {
            "year": str(pub.get('year', '')).strip(),
            "title": pub.get('title', '').strip(),
            "authors": pub.get('authors', '').strip(),
            "journal": pub.get('journal', '').strip(),
            "citations": int(pub.get('citations', 0)),
            "links": {
                "paper": pub.get('links', {}).get('paper'),
                "code": pub.get('links', {}).get('code')
            }
        }
        
        # Validate year
        if not re.match(r'^\d{4}$', cleaned_pub['year']):
            continue
        
        cleaned.append(cleaned_pub)
    
    # Sort by year (newest first)
    cleaned.sort(key=lambda x: int(x['year']), reverse=True)
    
    return cleaned


def manual_update():
    """Manual update interface."""
    print("\n📝 Manual Publications Update")
    print("=" * 50)

    existing_data = load_existing_publications()

    if existing_data:
        print(f"Found {len(existing_data.get('publications', []))} existing publications")
        print("Current publications:")
        for i, pub in enumerate(existing_data.get("publications", []), 1):
            print(f"{i}. {pub['title'][:60]}... ({pub['year']})")

    print("\nOptions:")
    print("1. Add new publication")
    print("2. Update existing publication")
    print("3. Remove publication")
    print("4. View current publications")
    print("5. Update citation metrics")
    print("6. Clean and validate data")
    print("7. Import from saved Scholar HTML (publications page)")
    print("8. Import from BibTeX file")
    print("9. Import metrics from saved Scholar homepage HTML")
    print("10. Import from simple text file (title/authors/venue/(citations\tyear))")
    print("11. Fetch via SerpAPI (needs SERPAPI_API_KEY)")
    print("12. Exit")

    choice = input("\nEnter your choice (1-12): ").strip()

    if choice == "1":
        add_publication(existing_data)
    elif choice == "2":
        update_publication(existing_data)
    elif choice == "3":
        remove_publication(existing_data)
    elif choice == "4":
        view_publications(existing_data)
    elif choice == "5":
        update_metrics(existing_data)
    elif choice == "6":
        clean_data(existing_data)
    elif choice == "7":
        path = input("Path to saved Google Scholar publications HTML (Enter to use publications.txt): ").strip()
        if not path and os.path.exists("publications.txt"):
            path = "publications.txt"
        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            new_pubs = parse_publications_from_saved_html(html)
            if not new_pubs:
                print("No publications found in the provided HTML file.")
                return
            data = existing_data or {
                "profile": {
                    "scholar_id": "4re6DoEAAAAJ",
                    "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                },
                "publications": [],
                "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
            }
            data["publications"] = merge_publication_lists(data.get("publications", []), new_pubs)
            data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_publications(data)
            print(f"✅ Imported {len(new_pubs)} publications from HTML and merged successfully!")
        except Exception as e:
            print(f"❌ Failed to import from HTML: {e}")
    elif choice == "8":
        path = input("Path to BibTeX file: ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                bib = f.read()
            new_pubs = parse_publications_from_bibtex(bib)
            if not new_pubs:
                print("No publications found in the provided BibTeX file.")
                return
            data = existing_data or {
                "profile": {
                    "scholar_id": "4re6DoEAAAAJ",
                    "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                },
                "publications": [],
                "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
            }
            data["publications"] = merge_publication_lists(data.get("publications", []), new_pubs)
            data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_publications(data)
            print(f"✅ Imported {len(new_pubs)} publications from BibTeX and merged successfully!")
        except Exception as e:
            print(f"❌ Failed to import from BibTeX: {e}")
    elif choice == "9":
        path = input("Path to saved Google Scholar homepage HTML: ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            metrics = parse_metrics_from_homepage_html(html)
            if not metrics:
                print("No metrics found in the provided HTML file.")
                return
            data = existing_data or {
                "profile": {
                    "scholar_id": "4re6DoEAAAAJ",
                    "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                },
                "publications": [],
                "metrics": {},
            }
            data["metrics"] = metrics
            data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_publications(data)
            print("✅ Metrics imported from homepage HTML successfully!")
        except Exception as e:
            print(f"❌ Failed to import metrics: {e}")
    elif choice == "10":
        path = input("Path to publications text file: ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read()
            pubs = parse_publications_from_text(txt)
            if pubs:
                data = existing_data or {
                    "profile": {
                        "scholar_id": "4re6DoEAAAAJ",
                        "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    },
                    "publications": [],
                    "metrics": {},
                }
                data["publications"] = merge_publication_lists(data.get("publications", []), pubs)
                data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                save_publications(data)
                print(f"✅ Imported {len(pubs)} publications from text and merged.")
            else:
                print("⚠️  No publications parsed from text.")
        except Exception as e:
            print(f"❌ Failed to import from text: {e}")
    elif choice == "11":
        api_key = _get_serpapi_key(None)
        if not api_key:
            return
        pubs = fetch_publications_with_serpapi("4re6DoEAAAAJ", api_key)
        if pubs:
            data = existing_data or {
                "profile": {
                    "scholar_id": "4re6DoEAAAAJ",
                    "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                },
                "publications": [],
                "metrics": {},
            }
            data["publications"] = merge_publication_lists(data.get("publications", []), pubs)
            data["metrics"] = compute_metrics_from_publications(data["publications"])
            data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_publications(data)
            print(f"✅ SerpAPI: imported {len(pubs)} publications and updated metrics.")
        else:
            print("⚠️  SerpAPI did not return publications.")
    elif choice == "12":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please try again.")


def clean_data(existing_data):
    """Clean and validate existing data."""
    if not existing_data or not existing_data.get('publications'):
        print("No publications to clean.")
        return
    
    print("\n🧹 Cleaning and validating publications data...")
    
    cleaned_publications = clean_publications_data(existing_data['publications'])
    
    print(f"✅ Cleaned {len(cleaned_publications)} publications")
    print(f"Removed {len(existing_data['publications']) - len(cleaned_publications)} invalid entries")
    
    existing_data['publications'] = cleaned_publications
    existing_data['profile']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    save_publications(existing_data)


def update_metrics(existing_data):
    """Update citation metrics."""
    print("\n📊 Update Citation Metrics")
    print("-" * 30)

    if existing_data and "metrics" in existing_data:
        current_metrics = existing_data["metrics"]
        print("Current metrics:")
        print(f"Total Citations: {current_metrics.get('total_citations', 0)}")
        print(f"h-index: {current_metrics.get('h_index', 0)}")
        print(f"i10-index: {current_metrics.get('i10_index', 0)}")

    print("\nEnter new metrics (press Enter to keep current value):")

    total_citations = input(
        f"Total Citations [{existing_data.get('metrics', {}).get('total_citations', 0)}]: "
    ).strip()
    h_index = input(
        f"h-index [{existing_data.get('metrics', {}).get('h_index', 0)}]: "
    ).strip()
    i10_index = input(
        f"i10-index [{existing_data.get('metrics', {}).get('i10_index', 0)}]: "
    ).strip()

    if not existing_data:
        existing_data = {
            "profile": {
                "scholar_id": "4re6DoEAAAAJ",
                "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
            },
            "publications": [],
            "metrics": {},
        }

    existing_data["metrics"] = {
        "total_citations": int(total_citations)
        if total_citations
        else existing_data.get("metrics", {}).get("total_citations", 0),
        "h_index": int(h_index)
        if h_index
        else existing_data.get("metrics", {}).get("h_index", 0),
        "i10_index": int(i10_index)
        if i10_index
        else existing_data.get("metrics", {}).get("i10_index", 0),
    }

    existing_data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_publications(existing_data)
    print("✅ Metrics updated successfully!")


def add_publication(existing_data):
    """Add a new publication."""
    print("\n📄 Add New Publication")
    print("-" * 30)

    title = input("Title: ").strip()
    authors = input("Authors: ").strip()
    journal = input("Journal: ").strip()
    year = input("Year: ").strip()
    citations = input("Citations (default 0): ").strip() or "0"
    paper_link = input("Paper URL (optional): ").strip() or None
    code_link = input("Code URL (optional): ").strip() or None

    new_publication = {
        "year": year,
        "title": title,
        "authors": authors,
        "journal": journal,
        "citations": int(citations),
        "links": {"paper": paper_link, "code": code_link},
    }

    if not existing_data:
        existing_data = {
            "profile": {
                "scholar_id": "4re6DoEAAAAJ",
                "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
            },
            "publications": [],
            "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
        }

    existing_data["publications"].append(new_publication)
    existing_data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Sort by year (newest first)
    existing_data["publications"].sort(key=lambda x: int(x["year"]), reverse=True)

    save_publications(existing_data)
    print("✅ Publication added successfully!")


def update_publication(existing_data):
    """Update an existing publication."""
    if not existing_data or not existing_data.get("publications"):
        print("No publications to update.")
        return

    print("\n📝 Update Publication")
    print("-" * 30)

    for i, pub in enumerate(existing_data["publications"], 1):
        print(f"{i}. {pub['title'][:60]}... ({pub['year']})")

    try:
        index = int(input("\nEnter publication number to update: ")) - 1
        if 0 <= index < len(existing_data["publications"]):
            pub = existing_data["publications"][index]

            print(f"\nUpdating: {pub['title']}")
            print("(Press Enter to keep current value)")

            title = input(f"Title [{pub['title']}]: ").strip() or pub["title"]
            authors = input(f"Authors [{pub['authors']}]: ").strip() or pub["authors"]
            journal = input(f"Journal [{pub['journal']}]: ").strip() or pub["journal"]
            year = input(f"Year [{pub['year']}]: ").strip() or pub["year"]
            citations = input(f"Citations [{pub['citations']}]: ").strip() or str(
                pub["citations"]
            )

            existing_data["publications"][index] = {
                "year": year,
                "title": title,
                "authors": authors,
                "journal": journal,
                "citations": int(citations),
                "links": pub["links"],
            }

            existing_data["profile"]["last_updated"] = datetime.now().strftime(
                "%Y-%m-%d"
            )
            save_publications(existing_data)
            print("✅ Publication updated successfully!")
        else:
            print("Invalid publication number.")
    except ValueError:
        print("Please enter a valid number.")


def remove_publication(existing_data):
    """Remove a publication."""
    if not existing_data or not existing_data.get("publications"):
        print("No publications to remove.")
        return

    print("\n🗑️ Remove Publication")
    print("-" * 30)

    for i, pub in enumerate(existing_data["publications"], 1):
        print(f"{i}. {pub['title'][:60]}... ({pub['year']})")

    try:
        index = int(input("\nEnter publication number to remove: ")) - 1
        if 0 <= index < len(existing_data["publications"]):
            removed = existing_data["publications"].pop(index)
            print(f"Removed: {removed['title']}")
            existing_data["profile"]["last_updated"] = datetime.now().strftime(
                "%Y-%m-%d"
            )
            save_publications(existing_data)
            print("✅ Publication removed successfully!")
        else:
            print("Invalid publication number.")
    except ValueError:
        print("Please enter a valid number.")


def view_publications(existing_data):
    """View all publications."""
    if not existing_data or not existing_data.get("publications"):
        print("No publications found.")
        return

    print("\n📚 Current Publications")
    print("-" * 50)

    for i, pub in enumerate(existing_data["publications"], 1):
        print(f"\n{i}. {pub['title']}")
        print(f"   Authors: {pub['authors']}")
        print(f"   Journal: {pub['journal']}")
        print(f"   Year: {pub['year']}")
        print(f"   Citations: {pub['citations']}")
        if pub["links"]["paper"]:
            print(f"   Paper: {pub['links']['paper']}")
        if pub["links"]["code"]:
            print(f"   Code: {pub['links']['code']}")

    if existing_data.get("metrics"):
        print("\n📊 Citation Metrics:")
        print(
            f"   Total Citations: {existing_data['metrics'].get('total_citations', 0)}"
        )
        print(f"   h-index: {existing_data['metrics'].get('h_index', 0)}")
        print(f"   i10-index: {existing_data['metrics'].get('i10_index', 0)}")


def main():
    """Main function."""
    print("🔬 Google Scholar Publications Updater")
    print("=" * 50)

    parser = argparse.ArgumentParser(description="Google Scholar Publications Updater")
    parser.add_argument("--auto-update", action="store_true", help="Run the script automatically")
    parser.add_argument("--from-html", dest="from_html", help="Import publications from saved Scholar publications HTML")
    parser.add_argument("--homepage-html", dest="homepage_html", help="Import metrics from saved Scholar homepage HTML")
    parser.add_argument("--from-bibtex", dest="from_bibtex", help="Import publications from BibTeX file")
    parser.add_argument("--from-text", dest="from_text", help="Import publications from simple text export (title/authors/venue/(citations\tyear))")
    parser.add_argument("--from-gs-fragment", dest="from_gs_fragment", nargs="?", const="publications.txt", help="Import publications from Google Scholar HTML fragment (default: publications.txt)")
    parser.add_argument("--merge", action="store_true", help="Merge with existing publications instead of replacing")
    parser.add_argument("--input", "-i", dest="input_path", default="publications.txt", help="Input GS HTML fragment (default: publications.txt)")
    parser.add_argument("--output", "-o", dest="output_path", default="data/publications.json", help="Output JSON path (default: data/publications.json)")
    parser.add_argument("--replace", action="store_true", help="Replace publications instead of merging")
    parser.add_argument("--no-metrics", action="store_true", help="Do not recompute metrics from publications")
    parser.add_argument("--simple", action="store_true", help="Run simple mode: parse input and update output")
    parser.add_argument("--serpapi", action="store_true", help="Use SerpAPI to fetch publications and metrics")
    parser.add_argument("--serpapi-key", dest="serpapi_key", help="SerpAPI API key (or set SERPAPI_API_KEY env var)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed errors and tracebacks")
    # Tor options (free) for scholarly
    parser.add_argument("--use-tor", action="store_true", help="Route scholarly calls via Tor (requires Tor running)")
    parser.add_argument("--tor-socks-port", type=int, default=9050, help="Tor SOCKS port (default 9050)")
    parser.add_argument("--tor-control-port", type=int, default=9051, help="Tor control port (default 9051)")
    parser.add_argument("--tor-password", default="", help="Tor control password if configured")
    args = parser.parse_args()

    # Configure verbosity and Tor
    global VERBOSE
    VERBOSE = bool(args.verbose)
    global TOR_ENABLED, TOR_SOCKS_PORT, TOR_CONTROL_PORT, TOR_PASSWORD
    TOR_ENABLED = bool(args.use_tor)
    TOR_SOCKS_PORT = int(args.tor_socks_port)
    TOR_CONTROL_PORT = int(args.tor_control_port)
    TOR_PASSWORD = str(args.tor_password or "")

    # Simple mode (default if no other modes provided)
    no_other_modes = not any([
        args.auto_update, args.from_html, args.from_bibtex, args.from_text, args.from_gs_fragment,
        args.homepage_html, args.serpapi
    ])
    if args.simple or no_other_modes:
        update_from_publications_fragment(
            input_path=args.input_path,
            output_path=args.output_path,
            merge=not args.replace,
            recompute_metrics=not args.no_metrics,
        )
        return

    # Non-interactive import modes
    if args.from_html or args.from_bibtex or args.homepage_html or args.from_text or args.from_gs_fragment or args.serpapi:
        existing_data = load_existing_publications() or {
            "profile": {
                "scholar_id": "4re6DoEAAAAJ",
                "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
            },
            "publications": [],
            "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
        }

        # SerpAPI fetching (publications + metrics)
        if args.serpapi:
            api_key = _get_serpapi_key(args.serpapi_key)
            if api_key:
                pubs = fetch_publications_with_serpapi(existing_data["profile"]["scholar_id"], api_key)
                if pubs:
                    if args.merge:
                        existing_data["publications"] = merge_publication_lists(existing_data.get("publications", []), pubs)
                    else:
                        existing_data["publications"] = clean_publications_data(pubs)
                    metrics = compute_metrics_from_publications(existing_data["publications"]) if existing_data["publications"] else None
                    if metrics:
                        existing_data["metrics"] = metrics
                    print(f"✅ SerpAPI: imported {len(pubs)} publications and computed metrics")
                else:
                    print("⚠️  SerpAPI did not return publications")

        # Import publications from HTML
        if args.from_html:
            try:
                with open(args.from_html, "r", encoding="utf-8") as f:
                    html = f.read()
                pubs = parse_publications_from_saved_html(html)
                if not pubs:
                    print("⚠️  No publications found in the provided HTML.")
                else:
                    if args.merge:
                        existing_data["publications"] = merge_publication_lists(existing_data.get("publications", []), pubs)
                    else:
                        existing_data["publications"] = clean_publications_data(pubs)
                    print(f"✅ Imported {len(pubs)} publications from HTML")
            except Exception as e:
                print(f"❌ Failed to import from HTML: {e}")

        # Import publications from BibTeX
        if args.from_bibtex:
            try:
                with open(args.from_bibtex, "r", encoding="utf-8") as f:
                    bib = f.read()
                pubs = parse_publications_from_bibtex(bib)
                if not pubs:
                    print("⚠️  No publications found in the provided BibTeX.")
                else:
                    if args.merge:
                        existing_data["publications"] = merge_publication_lists(existing_data.get("publications", []), pubs)
                    else:
                        existing_data["publications"] = clean_publications_data(pubs)
                    print(f"✅ Imported {len(pubs)} publications from BibTeX")
            except Exception as e:
                print(f"❌ Failed to import from BibTeX: {e}")

        # Import publications from plain text
        if args.from_text:
            try:
                with open(args.from_text, "r", encoding="utf-8") as f:
                    txt = f.read()
                pubs = parse_publications_from_text(txt)
                if not pubs:
                    print("⚠️  No publications parsed from the provided text.")
                else:
                    if args.merge:
                        existing_data["publications"] = merge_publication_lists(existing_data.get("publications", []), pubs)
                    else:
                        existing_data["publications"] = clean_publications_data(pubs)
                    print(f"✅ Imported {len(pubs)} publications from text")
            except Exception as e:
                print(f"❌ Failed to import from text: {e}")

        # Import publications from GS HTML fragment
        if args.from_gs_fragment:
            try:
                with open(args.from_gs_fragment, "r", encoding="utf-8") as f:
                    frag_html = f.read()
                pubs = parse_publications_from_saved_html(frag_html)
                if not pubs:
                    print("⚠️  No publications found in the GS fragment.")
                else:
                    if args.merge:
                        existing_data["publications"] = merge_publication_lists(existing_data.get("publications", []), pubs)
                    else:
                        existing_data["publications"] = clean_publications_data(pubs)
                    print(f"✅ Imported {len(pubs)} publications from GS fragment")
            except Exception as e:
                print(f"❌ Failed to import from GS fragment: {e}")

        # Import metrics from homepage HTML
        if args.homepage_html:
            try:
                with open(args.homepage_html, "r", encoding="utf-8") as f:
                    html = f.read()
                metrics = parse_metrics_from_homepage_html(html)
                if metrics:
                    existing_data["metrics"] = metrics
                    print(f"✅ Imported metrics: {metrics}")
                else:
                    print("⚠️  No metrics found in the provided homepage HTML.")
            except Exception as e:
                print(f"❌ Failed to import metrics from HTML: {e}")

        existing_data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_publications(existing_data)
        return

    if args.auto_update:
        print("\n🔄 Running in automated mode...")
        scholar_id = "4re6DoEAAAAJ"  # Your Google Scholar ID
        publications = fetch_google_scholar_publications(scholar_id)
        metrics = fetch_google_scholar_metrics(scholar_id)

        if publications or metrics:
            # Load existing data or create new
            existing_data = load_existing_publications()
            if not existing_data:
                existing_data = {
                    "profile": {
                        "scholar_id": scholar_id,
                        "scholar_url": f"https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=list_works&sortby=pubdate",
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    },
                    "publications": [],
                    "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
                }

            # Update publications if fetched
            if publications:
                print(f"✅ Found {len(publications)} publications")
                existing_data["publications"] = clean_publications_data(publications)
            
            # Update metrics if fetched
            if metrics:
                print(f"✅ Found metrics: {metrics}")
                existing_data["metrics"] = metrics

            existing_data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_publications(existing_data)
        else:
            print("❌ Could not fetch data from Google Scholar")
            print("This is likely due to Google's anti-bot measures.")
            print("Please use the manual update option instead.")
    else:
        scholar_id = "4re6DoEAAAAJ"  # Your Google Scholar ID

        print(f"Scholar ID: {scholar_id}")
        print(
            f"Profile URL: https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=list_works&sortby=pubdate"
        )

        print("\nOptions:")
        print("1. Try to fetch from Google Scholar (improved)")
        print("2. Manual update")
        print("3. Fetch citation metrics only")
        print("4. Clean existing data")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n🔄 Attempting to fetch from Google Scholar...")
            publications = fetch_google_scholar_publications(scholar_id)
            metrics = fetch_google_scholar_metrics(scholar_id)

            if publications or metrics:
                # Load existing data or create new
                existing_data = load_existing_publications()
                if not existing_data:
                    existing_data = {
                        "profile": {
                            "scholar_id": scholar_id,
                            "scholar_url": f"https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=list_works&sortby=pubdate",
                            "last_updated": datetime.now().strftime("%Y-%m-%d"),
                        },
                        "publications": [],
                        "metrics": {"total_citations": 0, "h_index": 0, "i10_index": 0},
                    }

                # Update publications if fetched
                if publications:
                    print(f"✅ Found {len(publications)} publications")
                    existing_data["publications"] = clean_publications_data(publications)
                
                # Update metrics if fetched
                if metrics:
                    print(f"✅ Found metrics: {metrics}")
                    existing_data["metrics"] = metrics

                existing_data["profile"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                save_publications(existing_data)
            else:
                print("❌ Could not fetch data from Google Scholar")
                print("This is likely due to Google's anti-bot measures.")
                print("Please use the manual update option instead.")

        elif choice == "2":
            manual_update()

        elif choice == "3":
            print("\n🔄 Fetching citation metrics...")
            metrics = fetch_google_scholar_metrics(scholar_id)

            if metrics:
                print(f"✅ Found metrics: {metrics}")

                existing_data = load_existing_publications()
                if not existing_data:
                    existing_data = {
                        "profile": {
                            "scholar_id": scholar_id,
                            "scholar_url": f"https://scholar.google.com/citations?hl=en&user={scholar_id}&view_op=list_works&sortby=pubdate",
                            "last_updated": datetime.now().strftime("%Y-%m-%d"),
                        },
                        "publications": [],
                        "metrics": {},
                    }

                existing_data["metrics"] = metrics
                existing_data["profile"]["last_updated"] = datetime.now().strftime(
                    "%Y-%m-%d"
                )
                save_publications(existing_data)
            else:
                print("❌ Could not fetch metrics from Google Scholar")
                print("Please use the manual update option instead.")

        elif choice == "4":
            existing_data = load_existing_publications()
            if existing_data:
                clean_data(existing_data)
            else:
                print("No existing data to clean.")

        elif choice == "5":
            print("Goodbye!")
            return

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
