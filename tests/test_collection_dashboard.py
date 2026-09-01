from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/collection_dashboard.py"
JSON_TARGET = ROOT / "ETAT_COLLECTION_2026_2027.json"
MD_TARGET = ROOT / "ETAT_COLLECTION_2026_2027.md"


def _module():
    spec = importlib.util.spec_from_file_location("collection_dashboard", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dashboard_is_explicitly_legacy_and_exactly_scoped() -> None:
    module = _module()
    payload = module.construire()
    matrix = json.loads(
        (ROOT / "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json").read_text(
            encoding="utf-8"
        )
    )
    expected = sorted(row["chapter"] for row in matrix["chapters"])

    assert payload["authority"] == "NON_AUTHORITATIVE_LEGACY_DIAGNOSTIC"
    assert payload["authoritative_successor"] == (
        "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json"
    )
    assert payload["authoritative_release_verdict"] == "NOT_PROVIDED"
    assert payload["chapter_ids"] == expected
    assert payload["chapter_ids_digest"].startswith("sha256:")
    assert payload["collection"]["chapitres_total"] == len(expected) == 52
    assert payload["manuels"]["TNSI"]["chapitres_total"] == 7

    rendered = json.dumps(payload, ensure_ascii=False)
    markdown = module.rendre_markdown(payload)
    assert "RELEASE_CANDIDATE" not in rendered
    assert "prêts pour release" not in markdown
    assert "Manuels prêts pour release" not in markdown
    assert "NON AUTORITAIRE" in markdown


def test_committed_dashboard_is_reproducible() -> None:
    module = _module()
    assert module.main(["--check"]) == 0
    payload = module.construire()
    assert json.loads(JSON_TARGET.read_text(encoding="utf-8")) == payload
    assert MD_TARGET.read_text(encoding="utf-8") == module.rendre_markdown(payload)
