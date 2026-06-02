#!/usr/bin/env python3
"""
ingest.py — Find all .txt and .doc/.docx files on this machine,
extract their text, and vectorize + store them in local Weaviate.

Usage:
    pip install weaviate-client python-docx
    python3 ingest.py [--root /path/to/search] [--dry-run]
"""

import os
import sys
import uuid
import hashlib
import argparse
import weaviate
import weaviate.classes as wvc
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

WEAVIATE_URL = "http://localhost:8080"
OLLAMA_URL = "http://ollama:11434"  # seen from the HOST (not inside Docker)
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "LocalDocument"
SEARCH_ROOT = Path.home()  # change to "/" to scan entire disk
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".cache",
    "proc",
    "sys",
    "dev",
    "run",
    "snap",
}
TARGET_EXTS = {".txt", ".doc", ".docx", ".py"}
BATCH_SIZE = 1


# ── Helpers ───────────────────────────────────────────────────────────────────


def find_files(root: Path) -> list[Path]:
    """Walk the filesystem and return all matching files."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Prune directories we never want to descend into
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        ]
        for fname in filenames:
            if Path(fname).suffix.lower() in TARGET_EXTS:
                found.append(Path(dirpath) / fname)
    return found


def extract_text(path: Path) -> str | None:
    """Return plain text from .txt, .doc, or .docx files."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".txt":
            return path.read_text(errors="replace")
        
        if suffix == ".py":
            return path.read_text(errors="replace")

        elif suffix in (".doc", ".docx"):
            # python-docx only handles .docx natively.
            # For legacy .doc we try antiword (if installed) then fall back.
            if suffix == ".docx":
                from docx import Document

                doc = Document(path)
                return "\n".join(p.text for p in doc.paragraphs)
            else:
                # Try antiword (apt install antiword)
                import subprocess

                result = subprocess.run(
                    ["antiword", str(path)], capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout
                # Last resort: read as binary and decode printable chars
                raw = path.read_bytes()
                return raw.decode("latin-1", errors="replace")

    except Exception as e:
        print(f"  [WARN] Could not read {path}: {e}")
        return None


def stable_uuid(path: Path) -> str:
    """Generate a deterministic UUID from the file path so re-runs are idempotent."""
    digest = hashlib.md5(str(path).encode()).hexdigest()
    return str(uuid.UUID(digest))


# ── Weaviate setup ────────────────────────────────────────────────────────────


def ensure_collection(client: weaviate.WeaviateClient):
    """Create the collection if it doesn't exist."""
    if client.collections.exists(COLLECTION):
        print(f"Collection '{COLLECTION}' already exists — skipping creation.")
        return

    client.collections.create(
        name=COLLECTION,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_ollama(
            api_endpoint=OLLAMA_URL,
            model=EMBED_MODEL,
        ),
        properties=[
            wvc.config.Property(
                name="file_path",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="file_name",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="extension",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(
                name="char_count",
                data_type=wvc.config.DataType.INT,
                skip_vectorization=True,
            ),
        ],
    )
    print(f"Collection '{COLLECTION}' created.")


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Vectorize local documents into Weaviate."
    )
    parser.add_argument(
        "--root",
        default=str(SEARCH_ROOT),
        help="Root directory to search (default: $HOME)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Find files but do not ingest them"
    )
    args = parser.parse_args()

    root = Path(args.root)
    print(f"Scanning for {TARGET_EXTS} files under: {root}")

    files = find_files(root)
    print(f"Found {len(files)} files.\n")

    # Write the file list to disk for reference
    list_path = Path("found_files.txt")
    list_path.write_text("\n".join(str(f) for f in files))
    print(f"File list saved to: {list_path.resolve()}\n")

    if args.dry_run:
        for f in files:
            print(f)
        print("\nDry run complete — nothing was ingested.")
        return

    # Connect to Weaviate
    client = weaviate.connect_to_local(host="localhost", port=8080, grpc_port=50051)
    try:
        ensure_collection(client)
        collection = client.collections.get(COLLECTION)

        total, skipped, errors = 0, 0, 0

        # Batch insert
        with collection.batch.fixed_size(batch_size=BATCH_SIZE) as batch:
            for i, path in enumerate(files, 1):
                print(f"[{i}/{len(files)}] {path}", end="  ")

                text = extract_text(path)
                if not text or not text.strip():
                    print("→ skipped (empty)")
                    skipped += 1
                    continue

                obj_uuid = stable_uuid(path)
                batch.add_object(
                    uuid=obj_uuid,
                    properties={
                        "file_path": str(path),
                        "file_name": path.name,
                        "extension": path.suffix.lower(),
                        "content": text[:2_000],  # cap at 50k chars
                        "char_count": len(text),
                    },
                )
                print(f"→ queued ({len(text):,} chars)")
                total += 1

        # Check for batch errors
        if collection.batch.failed_objects:
            errors = len(collection.batch.failed_objects)
            print(f"\n[WARN] {errors} objects failed to ingest.")
            for fo in collection.batch.failed_objects[:5]:
                print(f"  {fo.original_uuid}: {fo.message}")

        print(f"\n✓ Done. Ingested: {total}  Skipped: {skipped}  Errors: {errors}")
        print(f"  Query your documents at: {WEAVIATE_URL}/v1/graphql")

    finally:
        client.close()


if __name__ == "__main__":
    main()
