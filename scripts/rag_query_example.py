#!/usr/bin/env python3
"""Show the reference RAG query without reading or printing secrets."""

from __future__ import annotations


def main() -> int:
    print(
        """curl -sS "$RAG_API_BASE_URL" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $RAG_API_KEY" \\
  -d '{
    "q": "Importer une table depuis un fichier CSV",
    "collection": "nsi_corpus",
    "k": 5,
    "include_documents": true
  }'"""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
