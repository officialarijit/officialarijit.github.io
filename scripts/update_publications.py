#!/usr/bin/env python3
"""
Google Scholar Publications Updater
This script helps you update your publications.json file with data from Google Scholar.
Due to CORS restrictions, this script provides a way to manually update your publications.

Usage:
    python update_publications.py
    python update_publications.py --auto-update  # For automated execution

Requirements:
    pip install requests beautifulsoup4
"""

import json
import re
import time
import argparse
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def fetch_google_scholar_publications(scholar_id):
    """
    Attempt to fetch publications from Google Scholar with improved parsing.
    """
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
        print("🔄 Fetching publications from Google Scholar...")
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
    Attempt to fetch citation metrics from Google Scholar with improved parsing.
    """
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
        print("🔄 Fetching citation metrics from Google Scholar...")
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
    print("7. Exit")

    choice = input("\nEnter your choice (1-7): ").strip()

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
    args = parser.parse_args()

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
