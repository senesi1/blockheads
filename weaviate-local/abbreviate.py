#!/usr/bin/env python3
"""
abbreviate.py — Copy all files from a source folder into an output folder,
keeping only the first 5000 words of each file.

Usage:
    python3 abbreviate.py /path/to/gutenberg /path/to/gutenberg_abbreviated
"""

import sys
from pathlib import Path

WORD_LIMIT = 5000


def abbreviate(text: str, word_limit: int = WORD_LIMIT) -> str:
    words = text.split()
    return " ".join(words[:word_limit])


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 abbreviate.py <input_dir> <output_dir>")
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if not src.is_dir():
        print(f"Error: '{src}' is not a directory.")
        sys.exit(1)

    dst.mkdir(parents=True, exist_ok=True)

    files = [p for p in src.rglob("*") if p.is_file()]
    print(f"Found {len(files)} files in {src}\n")

    for i, path in enumerate(files, 1):
        try:
            text = path.read_text(errors="replace")
            abbreviated = abbreviate(text)

            # Preserve relative directory structure in output
            relative = path.relative_to(src)
            out_path = dst / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(abbreviated, encoding="utf-8")

            word_count = len(text.split())
            truncated = word_count > WORD_LIMIT
            print(
                f"[{i}/{len(files)}] {path.name}  →  {word_count:,} words {'(truncated)' if truncated else '(kept in full)'}"
            )

        except Exception as e:
            print(f"[{i}/{len(files)}] {path.name}  →  ERROR: {e}")

    print(f"\n✓ Done. Abbreviated files saved to: {dst.resolve()}")


if __name__ == "__main__":
    main()
