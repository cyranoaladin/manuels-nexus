#!/usr/bin/env python3
"""Classify one scraped resource according to the local source catalog schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def classify(path: Path, *, source_type: str = "inspiration", collection: str = "rag_education") -> dict[str, Any]:
    return {
        "id": f"src-{path.stem}",
        "title": path.name,
        "url": "",
        "local_path": path.as_posix(),
        "source_type": source_type,
        "license": "a_verifier",
        "copyright_status": "a_qualifier",
        "rgpd_status": "a_auditer_avant_ingestion",
        "level": "a_classifier",
        "theme": "a_classifier",
        "capacity_ids": [],
        "reuse_policy": "classification préalable requise",
        "rag_collection": collection,
        "decision": "a_classifier_avant_ingestion",
        "reviewer": "needs_review",
        "date_review": "needs_review",
        "risk_level": "medium",
        "allowed_actions": ["inspire"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classifie une ressource scrapée sans l'ingérer.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--source-type", default="inspiration")
    parser.add_argument("--collection", default="rag_education")
    args = parser.parse_args()
    print(json.dumps(classify(args.path, source_type=args.source_type, collection=args.collection), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
