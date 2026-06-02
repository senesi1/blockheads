# Local Weaviate Document Vectorizer

Stands up a local Weaviate vector database in Docker, scans your filesystem
for `.txt` and `.doc`/`.docx` files, and ingests them with local embeddings
via Ollama — no API keys required.

---

## Prerequisites

```bash
# Docker + Docker Compose
sudo apt install docker.io docker-compose-plugin

# Python 3.11+
sudo apt install python3 python3-pip

# For legacy .doc (Word 97-2003) files — optional
sudo apt install antiword

# Python libraries
pip install weaviate-client python-docx
```

---

## Step 1 — Start Weaviate + Ollama

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Start both containers in the background
2. Pull the `nomic-embed-text` embedding model into Ollama (~274 MB, once only)
3. Wait until Weaviate is healthy at http://localhost:8080

---

## Step 2 — Ingest your documents

### Dry run first (just find files, don't ingest)

```bash
python3 ingest.py --dry-run
```

This prints every matching file and writes the full list to `found_files.txt`.

### Full ingestion (scans $HOME by default)

```bash
python3 ingest.py
```

To scan a different directory (e.g. your entire disk):

```bash
python3 ingest.py --root /
```

The script is **idempotent** — re-running it won't create duplicate entries
because each file gets a deterministic UUID based on its path.

---

## What gets created

| Item | Details |
|------|---------|
| Docker volume `weaviate_data` | Persists your Weaviate database across restarts |
| Docker volume `ollama_data`   | Caches the embedding model across restarts |
| Weaviate collection `LocalDocument` | One object per file |
| `found_files.txt`             | Plain-text list of all files found |

### Object schema

Each document in Weaviate has these fields:

| Property | Type | Vectorized? |
|----------|------|-------------|
| `file_path` | text | No |
| `file_name` | text | No |
| `extension` | text | No |
| `content`   | text | **Yes** |
| `char_count`| int  | No |

---

## Querying your documents

### Semantic search (via GraphQL)

```bash
curl -s http://localhost:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "{
      Get {
        LocalDocument(
          nearText: { concepts: [\"project budget\"] }
          limit: 5
        ) {
          file_name
          file_path
          _additional { distance }
        }
      }
    }"
  }' | python3 -m json.tool
```

### List all ingested documents

```bash
curl -s "http://localhost:8080/v1/objects?class=LocalDocument&limit=100" \
  | python3 -m json.tool
```

---

## Stopping and restarting

```bash
# Stop (data is preserved in volumes)
docker compose down

# Restart later
docker compose up -d
```

> ⚠️ Always use `docker compose down` (not `docker rm -f`) so Weaviate can
> flush its in-memory state to disk cleanly.
