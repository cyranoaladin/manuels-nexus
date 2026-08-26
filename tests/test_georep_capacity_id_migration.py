"""Tests de la migration des identifiants de capacite 1SPE-GEOMETRIE-REPEREE.

Decision humaine du 2026-08-27 : le referentiel canonique ne declare que les
identifiants longs 1SPE-GEOMETRIE-REPEREE-C1..C5. La forme courte
1SPE-GEOREP-C1..C5 disparait du graphe de consommateurs actifs, sans alias
runtime : Git seul porte l'historique.

Attention au motif : 1SPE-GEOREP-C capture aussi les identifiants d'OBJETS
(1SPE-GEOREP-CO-001, -CR-*, ...), qui eux ne sont pas migres. Seule une
reference de CAPACITE est visee, d'ou la borne (?![0-9A-Za-z-]).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import human_review_governance as g  # noqa: E402

CHAPTER = "1SPE-GEOMETRIE-REPEREE"
CHAPTER_DIR = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / CHAPTER
REFERENTIEL = (
    ROOT / "Mathematiques" / "manuel-maths" / "referentiel"
    / "capacites_1SPE_GEOMETRIE_REPEREE.json"
)
FORENSICS = ROOT / "audit" / "1SPE_GEOREP_CAPACITY_ID_MIGRATION_FORENSICS.json"

#: Une reference de CAPACITE, jamais un identifiant d'objet.
LEGACY = re.compile(r"1SPE-GEOREP-C[1-5](?![0-9A-Za-z-])")
CANONICAL = re.compile(r"1SPE-GEOMETRIE-REPEREE-C[1-5](?![0-9])")
#: Commit precedant immediatement la migration.
PRE_MIGRATION = "10c55309"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def _declared_ids() -> set[str]:
    payload = json.loads(REFERENTIEL.read_text(encoding="utf-8"))
    return {entry["id"] for entry in payload["capacites"]}


# -- A : chaque ancien identifiant a exactement un nouvel identifiant --------


def test_A_each_legacy_id_maps_to_exactly_one_canonical_id() -> None:
    mapping = json.loads(FORENSICS.read_text(encoding="utf-8"))["mapping"]
    assert len(mapping) == 5
    olds = [row["old_id"] for row in mapping]
    news = [row["new_id"] for row in mapping]
    assert len(set(olds)) == len(set(news)) == 5
    for row in mapping:
        index = row["old_id"].rsplit("C", 1)[1]
        assert row["new_id"] == f"1SPE-GEOMETRIE-REPEREE-C{index}"
        assert row["authority_declares_new_id"] is True
        assert row["authority_declares_old_id"] is False


# -- B : un ancien identifiant dans un objet de production => FAIL -----------


def test_B_no_production_object_still_carries_a_legacy_capacity_ref() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(CHAPTER_DIR.rglob("*"))
        if path.is_file()
        and path.suffix in {".tex", ".json", ".yaml"}
        and LEGACY.search(path.read_text(encoding="utf-8", errors="replace"))
    ]
    assert offenders == [], offenders


def test_B_the_repository_keeps_legacy_refs_only_in_the_migration_ledger() -> None:
    tracked = [
        line
        for line in _git("grep", "-lE", r"1SPE-GEOREP-C[1-5]([^0-9A-Za-z-]|$)", "--", ".").splitlines()
        if line
    ]
    assert tracked == ["audit/1SPE_GEOREP_CAPACITY_ID_MIGRATION_FORENSICS.json"]


def test_B_object_identifiers_are_not_renamed() -> None:
    """Seules les capacites migrent : les identifiants d'objets restent courts."""

    objects = sorted(path.name for path in (CHAPTER_DIR / "exercices").glob("*.tex"))
    assert objects, "le chapitre doit porter des exercices"
    assert all(name.startswith("1SPE-GEOREP-EX-") for name in objects)


# -- C : le nouvel identifiant est present partout ---------------------------


def test_C_contract_objects_and_referentiel_agree() -> None:
    declared = _declared_ids()
    assert declared == {f"1SPE-GEOMETRIE-REPEREE-C{index}" for index in range(1, 6)}

    contract = yaml.safe_load((CHAPTER_DIR / "contrat.yaml").read_text(encoding="utf-8"))
    assert {entry["ref_capacite"] for entry in contract["capacites"]} == declared

    used: set[str] = set()
    for path in CHAPTER_DIR.rglob("*.tex"):
        used |= set(CANONICAL.findall(path.read_text(encoding="utf-8", errors="replace")))
    assert used, "les objets doivent referencer des capacites canoniques"
    assert used <= declared


# -- D : un chapitre voisin est inchange -------------------------------------


def test_D_a_non_georep_chapter_is_untouched() -> None:
    changed = _git("diff", "--name-only", PRE_MIGRATION, "HEAD", "--",
                   "Mathematiques/manuel-maths/chapitres").split()
    foreign = [
        path
        for path in changed
        if f"/chapitres/{CHAPTER}/" not in path
        and "1SPE-VARIABLES-ALEATOIRES" not in path
    ]
    assert foreign == [], foreign


# -- E : 100 % des consommateurs migres --------------------------------------


def test_E_every_declared_consumer_was_migrated() -> None:
    forensics = json.loads(FORENSICS.read_text(encoding="utf-8"))
    total = forensics["totals"]["files"]
    assert total == 54, "le denominateur exact est recalcule avant mutation"
    for entry in forensics["consumers"].values():
        for path in entry["paths"]:
            target = ROOT / path
            if not target.is_file():
                continue
            assert not LEGACY.search(target.read_text(encoding="utf-8", errors="replace")), path


# -- F : aucune identite de capacite dupliquee -------------------------------


def test_F_no_duplicate_capacity_identity() -> None:
    payload = json.loads(REFERENTIEL.read_text(encoding="utf-8"))
    identifiers = [entry["id"] for entry in payload["capacites"]]
    assert len(identifiers) == len(set(identifiers))
    contract = yaml.safe_load((CHAPTER_DIR / "contrat.yaml").read_text(encoding="utf-8"))
    codes = [entry["code"] for entry in contract["capacites"]]
    refs = [entry["ref_capacite"] for entry in contract["capacites"]]
    assert len(codes) == len(set(codes)) == len(refs) == len(set(refs))


# -- G : aucun META orphelin ou casse apres migration ------------------------


def test_G_no_broken_or_orphan_meta_after_migration() -> None:
    scope = g.build_scope(CHAPTER, ROOT)
    assert scope.object_count > 0
    assert scope.unassembled_object_ids() == []
    declared = _declared_ids()
    for entry in scope.objects:
        for capability in entry.capabilities:
            if capability.startswith("1SPE-"):
                assert capability in declared, (entry.object_id, capability)


# -- H : le mapping programme est inchange semantiquement --------------------


def test_H_programme_mapping_is_semantically_unchanged() -> None:
    """Seul le libelle de l'identifiant change, jamais l'atome qu'il rattache."""

    path = "audit/official_program_coverage/1SPE.json"
    before = json.loads(_git("show", f"{PRE_MIGRATION}:{path}"))
    after = json.loads((ROOT / path).read_text(encoding="utf-8"))

    def normalise(rows: list[dict]) -> list[tuple]:
        return [
            (
                row["atom_id"],
                str(row.get("contract_capacity", "")).replace(
                    "1SPE-GEOREP-C", "1SPE-GEOMETRIE-REPEREE-C"
                ),
                row.get("coverage_status"),
                row.get("mandatory"),
            )
            for row in rows
        ]

    assert normalise(before["rows"]) == normalise(after["rows"])


# -- I : l'assemblage eleve/professeur est inchange semantiquement -----------


def test_I_student_and_teacher_assembly_is_unchanged() -> None:
    scope = g.build_scope(CHAPTER, ROOT)
    order = {
        "eleve": [
            entry.object_id
            for entry in sorted(
                (item for item in scope.objects if item.student_index is not None),
                key=lambda item: item.student_index or 0,
            )
        ],
        "professeur": [
            entry.object_id
            for entry in sorted(
                (item for item in scope.objects if item.teacher_index is not None),
                key=lambda item: item.teacher_index or 0,
            )
        ],
    }
    assert order["eleve"], "la variante eleve doit assembler des objets"
    assert set(order["eleve"]) <= set(order["professeur"])
    # Les identifiants d'objets n'ont pas bouge : l'ordre est donc identique a
    # celui d'avant migration, que l'on relit depuis l'arbre precedent.
    listing = _git(
        "ls-tree", "-r", "--name-only", PRE_MIGRATION, "--",
        f"Mathematiques/manuel-maths/chapitres/{CHAPTER}",
    ).split()
    before = {Path(item).name for item in listing if item.endswith(".tex")}
    now = {path.name for path in CHAPTER_DIR.rglob("*.tex")}
    assert before == now, "aucun objet ajoute, retire ni renomme par la migration"


# -- Invariants declares ------------------------------------------------------


@pytest.mark.parametrize(
    "invariant",
    [
        "LEGACY_GEOREP_CAPACITY_REF",
        "BROKEN_CAPACITY_REF",
        "AMBIGUOUS_CAPACITY_ALIAS",
        "RUNTIME_CAPACITY_ALIAS",
    ],
)
def test_the_declared_post_migration_invariants_are_zero(invariant: str) -> None:
    forensics = json.loads(FORENSICS.read_text(encoding="utf-8"))
    assert forensics["post_migration_invariants"][invariant] == 0


def test_no_runtime_alias_was_introduced() -> None:
    """Aucun code ne traduit l'ancien identifiant vers le nouveau."""

    hits = [
        line
        for line in _git(
            "grep", "-lE", r"1SPE-GEOREP-C[1-5]([^0-9A-Za-z-]|$)", "--", "scripts", "tests"
        ).splitlines()
        if line and not line.endswith("test_georep_capacity_id_migration.py")
    ]
    assert hits == [], hits
