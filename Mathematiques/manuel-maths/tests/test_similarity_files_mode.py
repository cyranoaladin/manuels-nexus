"""Régression du gate anti-similarité sans PostgreSQL (mode fichiers)."""
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import similarity_check  # noqa: E402


def test_iter_source_chunks_reads_json_without_database(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus" / "SRC-TEST" / "document"
    corpus.mkdir(parents=True)
    (corpus / "chunk-001.json").write_text(
        json.dumps(
            {
                "id": "chunk-001",
                "content_md": "Une ressource originale sur les suites numériques.",
                "theme": "SUITES",
                "tier": "T1",
                "usage_policy": "adaptation_attribution",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(similarity_check, "CORPUS_DIR", tmp_path / "corpus", raising=False)
    monkeypatch.setattr(similarity_check, "STORAGE_MODE", "fichiers", raising=False)
    monkeypatch.setattr(
        similarity_check,
        "db_connect",
        lambda: (_ for _ in ()).throw(AssertionError("PostgreSQL ne doit pas être appelé")),
    )

    chunks = list(similarity_check.iter_source_chunks("SUITES"))

    assert chunks == [("chunk-001", "Une ressource originale sur les suites numériques.", "T1", "adaptation_attribution")]
