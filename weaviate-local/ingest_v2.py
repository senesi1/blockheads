#!/usr/bin/env python3
"""
ingest.py — Vectorize all text files in a directory into local Weaviate.

Usage:
    python3 ingest.py /path/to/gutenberg
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
OLLAMA_URL = "http://ollama:11434"
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "LocalDocument"
BATCH_SIZE = 50
CHUNK_SIZE = 1500  # characters (~300-400 tokens, safe for nomic-embed-text)
CHUNK_OVERLAP = 200  # overlap so sentences aren't cut off at boundaries
TARGET_EXTS = {".txt", ".doc", ".docx", ".py", ".md"}


# ── Text extraction ───────────────────────────────────────────────────────────


def extract_text(path: Path) -> str | None:
    suffix = path.suffix.lower()
    try:
        if suffix in (".txt", ".py", ".md"):
            return path.read_text(errors="replace")
        elif suffix == ".docx":
            from docx import Document

            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        elif suffix == ".doc":
            import subprocess

            result = subprocess.run(
                ["antiword", str(path)], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            return path.read_bytes().decode("latin-1", errors="replace")
    except Exception as e:
        print(f"  [WARN] Could not read {path}: {e}")
        return None


# ── Chunking ──────────────────────────────────────────────────────────────────


def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ── Weaviate ──────────────────────────────────────────────────────────────────


def stable_uuid(key: str) -> str:
    digest = hashlib.md5(key.encode()).hexdigest()
    return str(uuid.UUID(digest))


def ensure_collection(client: weaviate.WeaviateClient):
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
            wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(
                name="chunk_index",
                data_type=wvc.config.DataType.INT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="chunk_total",
                data_type=wvc.config.DataType.INT,
                skip_vectorization=True,
            ),
        ],
    )
    print(f"Collection '{COLLECTION}' created.")


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Vectorize a directory of documents into Weaviate."
    )
    parser.add_argument("directory", help="Directory to ingest")
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    files = [
        p for p in root.rglob("*") if p.suffix.lower() in TARGET_EXTS and p.is_file()
    ]
    print(f"Found {len(files)} files in {root}\n")

    client = weaviate.connect_to_local(host="localhost", port=8080, grpc_port=50051)
    try:
        ensure_collection(client)
        collection = client.collections.get(COLLECTION)

        total_chunks = 0
        skipped = 0
        errors = 0

        with collection.batch.fixed_size(batch_size=BATCH_SIZE) as batch:
            for i, path in enumerate(files, 1):
                print(f"[{i}/{len(files)}] {path.name}", end="  ")

                text = extract_text(path)
                if not text or not text.strip():
                    print("→ skipped (empty)")
                    skipped += 1
                    continue

                chunks = chunk_text(text)
                print(f"→ {len(chunks)} chunks")

                for idx, chunk in enumerate(chunks):
                    batch.add_object(
                        uuid=stable_uuid(f"{path}::chunk{idx}"),
                        properties={
                            "file_path": str(path),
                            "file_name": path.name,
                            "content": chunk,
                            "chunk_index": idx,
                            "chunk_total": len(chunks),
                        },
                    )
                    total_chunks += 1

        if collection.batch.failed_objects:
            errors = len(collection.batch.failed_objects)
            print(f"\n[WARN] {errors} chunks failed to ingest.")
            for fo in collection.batch.failed_objects[:5]:
                print(f"  {fo.original_uuid}: {fo.message}")

        print(f"\n✓ Done.")
        print(f"  Files processed : {len(files) - skipped}")
        print(f"  Files skipped   : {skipped}")
        print(f"  Chunks ingested : {total_chunks}")
        print(f"  Chunks failed   : {errors}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
