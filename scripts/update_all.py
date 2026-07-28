#!/usr/bin/env python3
"""Update scholar metrics and publications from Google Scholar or local HTML exports."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str]) -> int:
    print("$", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Update all Google Scholar site data.")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip live Scholar fetch")
    args = parser.parse_args()

    if not args.skip_fetch:
        code = run([sys.executable, "scripts/fetch_scholar.py"])
        if code == 0:
            return 0
        print("Live fetch failed; falling back to local HTML exports.", file=sys.stderr)

    citation_txt = ROOT / "citation.txt"
    publications_txt = ROOT / "publications.txt"

    if citation_txt.exists():
        if run([sys.executable, "scripts/update_scholar.py"]) != 0:
            return 1
    else:
        print("No citation.txt found and live fetch failed.", file=sys.stderr)
        return 1

    if publications_txt.exists():
        if run([sys.executable, "scripts/update_publications.py"]) != 0:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
