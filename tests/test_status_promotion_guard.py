from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import scripts.check_status_promotion_guard as guard


CAPACITY_ID = "P-TABLE-01"
QUOTE = "Importer un CSV consiste à lire chaque ligne et séparer les champs."


def validated_capacity() -> dict[str, object]:
    evidence = {
        "present": True,
        "file": "preuve.md",
        "anchor": "#preuve",
        "quote": QUOTE,
        "teaches": True,
    }
    evidence_practice = {
        "present": True,
        "file": "preuve.md",
        "anchor": "#preuve",
        "quote": "Exercice : importer une table CSV et afficher les colonnes.",
        "teaches": True,
    }
    evidence_correction = {
        "present": True,
        "file": "preuve_corrige.md",
        "anchor": "#corrigé-preuve",
        "quote": "Corrigé : la table est importée avec csv.reader et contient 5 lignes.",
        "teaches": True,
    }
    return {
        "capacity_id": CAPACITY_ID,
        "official_label": "Importer une table depuis un fichier texte tabulé ou un fichier CSV.",
        "proof_course": evidence,
        "proof_practice": evidence_practice,
        "proof_correction": evidence_correction,
        "verdict": "validated_pedagogy",
        "justification": "Les trois preuves sont ancrées, citées et marquées enseignantes.",
        "scientific_flags": [],
    }


def write_valid_verdict(root: Path) -> dict[str, object]:
    (root / "preuve.md").write_text(
        f"# Preuve\n\n{QUOTE}\n\n"
        "Exercice : importer une table CSV et afficher les colonnes.\n",
        encoding="utf-8",
    )
    (root / "preuve_corrige.md").write_text(
        "# Corrigé preuve\n\n"
        "## Corrigé preuve\n\n"
        "Corrigé : la table est importée avec csv.reader et contient 5 lignes.\n",
        encoding="utf-8",
    )
    capacity = validated_capacity()
    verdict = {
        "schema_version": "1.0.0",
        "unit": "P05",
        "level": "premiere",
        "judged_at": "2026-06-28T20:00:00Z",
        "judge_model": "system-a",
        "author_model": "system-b",
        "capacities": [capacity],
    }
    review_dir = root / "substance_reviews"
    review_dir.mkdir()
    (review_dir / "P05_substance_review.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return capacity


def write_confirmation(root: Path, capacity: dict[str, object]) -> None:
    payload = {
        "capacite_id": CAPACITY_ID,
        "verdict_hash": guard.canonical_verdict_hash(capacity),
        "relecteur": "lecteur-humain",
        "date": "2026-06-28",
        "marqueur": "confirmation_humaine_lot1",
    }
    (root / "reviewer_confirmation_P_TABLE_01.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_canonical_verdict_hash_is_reproducible_and_sensitive() -> None:
    verdict = {"b": 2, "a": {"z": True, "m": "x"}}
    same = {"a": {"m": "x", "z": True}, "b": 2}
    changed = {"a": {"m": "x", "z": False}, "b": 2}
    expected = hashlib.sha256(
        json.dumps(verdict, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
    ).hexdigest()

    assert guard.canonical_verdict_hash(verdict) == expected
    assert guard.canonical_verdict_hash(same) == expected
    assert guard.canonical_verdict_hash(changed) != expected


def test_fraudulent_87a22a2_fixture_is_rejected_without_proof(tmp_path: Path) -> None:
    (tmp_path / "coverage.md").write_text(
        "# Fixture commit 87a22a2\n\n15 capacities: validated_pedagogy\n",
        encoding="utf-8",
    )

    result = guard.analyze_status_promotions(tmp_path)

    assert any("validated_pedagogy" in error for error in result.errors)


def test_covered_positive_without_system_a_verdict_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "coverage.md").write_text(f"{CAPACITY_ID} covered: 1\n", encoding="utf-8")

    result = guard.analyze_status_promotions(tmp_path)

    assert any("covered > 0" in error for error in result.errors)


def test_published_positive_without_human_confirmation_is_rejected(tmp_path: Path) -> None:
    write_valid_verdict(tmp_path)
    (tmp_path / "manifest.csv").write_text(f"id,capacity,published\n1,{CAPACITY_ID},1\n", encoding="utf-8")

    result = guard.analyze_status_promotions(tmp_path)

    assert any("confirmation" in error for error in result.errors)


def test_promoted_status_with_valid_system_a_and_confirmation_is_accepted(tmp_path: Path) -> None:
    capacity = write_valid_verdict(tmp_path)
    write_confirmation(tmp_path, capacity)
    (tmp_path / "coverage.md").write_text(f"{CAPACITY_ID} validated_pedagogy\n", encoding="utf-8")

    result = guard.analyze_status_promotions(tmp_path)

    assert result.errors == []


def test_quality_gate_and_ci_include_status_promotion_guard() -> None:
    import scripts.check_quality_gates as check_quality_gates

    commands = {" ".join(command) for command in check_quality_gates.CORE_CHECKS}
    assert "-m scripts.check_status_promotion_guard" in commands
    assert "check_status_promotion_guard" in (ROOT / ".github/workflows/ci.yml").read_text(
        encoding="utf-8"
    )
