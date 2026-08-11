from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

import scripts.check_substance_anchors as check_substance_anchors
import scripts.substance_judge as substance_judge


CAPACITY = {
    "id": "P-TABLE-01",
    "intitule": "Importer une table depuis un fichier texte tabulé ou un fichier CSV.",
    "rubrique": "Traitement de données en tables",
    "contenu": "Indexation de tables",
    "niveau": "premiere",
}


def write_source(root: Path, body: str) -> Path:
    path = root / "cours.md"
    path.write_text(f"# Preuve\n\n{body}\n", encoding="utf-8")
    return path


def hit_for(path: Path) -> dict[str, object]:
    return {
        "metadata": {"path": path.name, "anchor": "#preuve", "document_type": "cours"},
        "score": 0.1,
        "document": path.read_text(encoding="utf-8"),
    }


def test_citation_status_is_case_sensitive_and_whitespace_normalized() -> None:
    # Horizontal whitespace collapse: multiple spaces -> single space -> normalized match
    assert check_substance_anchors.citation_status("Alpha Beta", "Alpha   Beta") == (
        "normalized",
        1.0,
    )
    # Newlines preserved: cross-line join must NOT match (K2-BIS-1)
    assert check_substance_anchors.citation_status("Alpha Beta", "Alpha\n   Beta")[0] == "absent"
    # Case sensitive
    assert check_substance_anchors.citation_status("alpha beta", "Alpha Beta")[0] == "absent"


def test_judge_rejects_hallucinated_quote(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = write_source(tmp_path, "Importer un CSV demande de choisir un séparateur.")
    monkeypatch.setattr(substance_judge, "search_rag", lambda *args, **kwargs: [hit_for(source)])
    monkeypatch.setattr(
        substance_judge,
        "call_llm",
        lambda *args, **kwargs: {
            "taught": True,
            "citation": "Cette phrase n'existe pas dans le fichier.",
            "justification": "citation inventée",
        },
    )

    verdict = substance_judge.judge_capacity({}, CAPACITY, repo_root=tmp_path)

    assert verdict["proof_course"]["present"] is False
    assert verdict["verdict"] == "needs_content"


def test_judge_accepts_quote_with_whitespace_altered(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Horizontal whitespace variant: multiple spaces collapsed (K2-BIS-1: newlines preserved)
    source = write_source(tmp_path, "Importer un CSV   demande de choisir un séparateur.")
    monkeypatch.setattr(substance_judge, "search_rag", lambda *args, **kwargs: [hit_for(source)])
    monkeypatch.setattr(
        substance_judge,
        "call_llm",
        lambda *args, **kwargs: {
            "taught": True,
            "citation": "Importer un CSV demande de choisir un séparateur.",
            "justification": "citation exacte après normalisation des espaces horizontaux",
        },
    )

    verdict = substance_judge.judge_capacity({}, CAPACITY, repo_root=tmp_path)

    assert verdict["proof_course"]["present"] is True
    assert verdict["proof_course"]["quote"] == "Importer un CSV demande de choisir un séparateur."


def test_judge_never_promotes_to_validated_pedagogy(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = write_source(tmp_path, "Importer un CSV demande de choisir un séparateur.")
    monkeypatch.setattr(substance_judge, "search_rag", lambda *args, **kwargs: [hit_for(source)])
    monkeypatch.setattr(
        substance_judge,
        "call_llm",
        lambda *args, **kwargs: {
            "taught": True,
            "citation": "Importer un CSV demande de choisir un séparateur.",
            "justification": "preuve présente",
        },
    )

    verdict = substance_judge.judge_capacity({}, CAPACITY, repo_root=tmp_path)

    assert verdict["verdict"] == "needs_review"


def test_lexical_branch_is_executed() -> None:
    result = substance_judge.veto_deterministe(
        {"taught": True, "citation": "pile file graphe", "justification": ""},
        "Importer une table CSV",
        set(),
    )

    assert result["taught"] is False
    assert result["veto"] == "no_lexical_overlap"


def test_offline_fixture_writes_schema_verdict(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture.json"
    output = tmp_path / "review.json"
    capacity = {
        "capacity_id": "P-TABLE-01",
        "official_label": "Importer une table depuis un fichier texte tabulé ou un fichier CSV.",
        "proof_course": {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False},
        "proof_practice": {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False},
        "proof_correction": {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False},
        "verdict": "needs_content",
        "justification": "Fixture offline sans promotion ni preuve humaine validante.",
        "scientific_flags": ["human_review_required"],
    }
    fixture.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "unit": "P05",
                "level": "premiere",
                "judged_at": "2026-06-28T20:00:00Z",
                "judge_model": "offline-fixture",
                "author_model": "codex-authoring-agent",
                "capacities": [capacity],
            }
        ),
        encoding="utf-8",
    )

    substance_judge.run_from_offline_fixture(fixture, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["capacities"][0]["verdict"] == "needs_content"
    assert payload["capacities"][0]["verdict"] != "validated_pedagogy"


def test_network_calls_are_blocked_by_test_fixture() -> None:
    with pytest.raises(AssertionError, match="network"):
        sock = socket.socket()
        try:
            sock.connect(("127.0.0.1", 9))
        finally:
            sock.close()


def test_makefile_contains_judge_chain() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "\njudge:" in makefile
    assert "scripts.substance_judge" in makefile
    assert "scripts.check_substance_anchors" in makefile


def test_substance_reviews_index_keeps_zero_publication_doctrine() -> None:
    text = (ROOT / "substance_reviews_index.md").read_text(encoding="utf-8")
    assert "covered = 0" in text
    assert "published = 0" in text
    assert "validated_* = 0" in text


def test_make_judge_p05_runs_b_then_a_without_promotion() -> None:
    result = subprocess.run(
        ["make", "judge", "U=P05"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout
    assert "validated_pedagogy" not in result.stdout
    assert "scripts.check_substance_anchors" in result.stdout
