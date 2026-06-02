#!/usr/bin/env python3
"""
download_gutenberg.py — Bulk download plain-text books from Project Gutenberg.

Usage:
    pip install requests
    python3 download_gutenberg.py [--count 2000] [--out ./gutenberg]

Books are saved as <id>.txt in the output folder.
Already-downloaded books are skipped on re-runs.
"""

import os
import time
import argparse
import requests
from pathlib import Path

# Gutenberg's CDN mirror — no crawling restrictions for bulk access
MIRROR = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"

# Fallback URL pattern (older books may use this)
MIRROR_ALT = "https://www.gutenberg.org/files/{id}/{id}-0.txt"
MIRROR_ALT2 = "https://www.gutenberg.org/files/{id}/{id}.txt"

HEADERS = {
    "User-Agent": "GutenbergBulkDownloader/1.0 (personal research; contact: local-user)"
}

# Gutenberg has ~70,000 books; IDs are roughly 1–75000 but many gaps exist
DEFAULT_COUNT = 2000
DELAY_SECONDS = 1.0   # be polite — 1 request per second


def download_book(book_id: int, out_dir: Path, session: requests.Session) -> str:
    """Try to download a single book. Returns 'ok', 'skip', or 'miss'."""
    out_path = out_dir / f"{book_id}.txt"

    if out_path.exists():
        return "skip"

    urls = [
        MIRROR.format(id=book_id),
        MIRROR_ALT.format(id=book_id),
        MIRROR_ALT2.format(id=book_id),
    ]

    for url in urls:
        try:
            resp = session.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.text) > 500:
                out_path.write_text(resp.text, encoding="utf-8", errors="replace")
                return "ok"
        except requests.RequestException:
            continue

    return "miss"


def main():
    parser = argparse.ArgumentParser(description="Bulk-download Gutenberg books.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT,
                        help=f"Number of books to download (default: {DEFAULT_COUNT})")
    parser.add_argument("--out", default="./gutenberg",
                        help="Output directory (default: ./gutenberg)")
    parser.add_argument("--start", type=int, default=1,
                        help="Starting book ID (default: 1)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading up to {args.count} books → {out_dir.resolve()}")
    print(f"Starting at book ID {args.start}, delay {DELAY_SECONDS}s between requests.\n")

    ok = skipped = missed = 0
    book_id = args.start

    with requests.Session() as session:
        while ok + skipped < args.count:
            status = download_book(book_id, out_dir, session)

            if status == "ok":
                ok += 1
                print(f"  [{ok:>4} downloaded] ID {book_id} ✓")
                time.sleep(DELAY_SECONDS)
            elif status == "skip":
                skipped += 1
            elif status == "miss":
                missed += 1

            book_id += 1

            # Safety: don't run forever if IDs are exhausted
            if book_id > 80_000:
                print("Reached end of known Gutenberg ID range.")
                break

    print(f"\n✓ Done.")
    print(f"  Downloaded : {ok}")
    print(f"  Skipped    : {skipped}  (already on disk)")
    print(f"  Not found  : {missed}  (gaps in ID range)")
    print(f"  Saved to   : {out_dir.resolve()}")


if __name__ == "__main__":
    main()
