"""Validate classify_scraped_resource output against sources_catalog.schema.json."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

import scripts.classify_scraped_resource as classify_mod


def test_classify_output_validates_against_schema() -> None:
    schema = json.loads((ROOT / "sources_catalog.schema.json").read_text(encoding="utf-8"))
    item_schema = schema["properties"]["sources"]["items"]
    result = classify_mod.classify(Path("test_resource.md"))
    jsonschema.validate(result, item_schema)
