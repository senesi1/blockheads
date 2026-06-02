#!/usr/bin/env bash
# setup.sh — Pull the embedding model and verify Weaviate is up

set -e

echo "==> Starting Weaviate + Ollama..."
docker compose up -d

echo "==> Waiting for Ollama to be ready..."
until curl -s http://localhost:11434 > /dev/null 2>&1; do
  sleep 2
  echo "    ...waiting for Ollama"
done
echo "    Ollama is up."

echo "==> Pulling nomic-embed-text model (this may take a few minutes on first run)..."
docker compose exec ollama ollama pull nomic-embed-text
echo "    Model ready."

echo "==> Waiting for Weaviate to be ready..."
until curl -s http://localhost:8080/v1/.well-known/ready > /dev/null 2>&1; do
  sleep 2
  echo "    ...waiting for Weaviate"
done
echo "    Weaviate is up at http://localhost:8080"

echo ""
echo "All set! Now install Python dependencies and run the ingestion script:"
echo "  pip install weaviate-client python-docx"
echo "  python3 ingest.py"
