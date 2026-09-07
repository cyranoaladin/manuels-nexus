"""La maturité produit ne doit pas être mesurée par un reçu de build.

`RELEASE_READY` exige un HEAD gelé, un build final, un manifeste et une
approbation humaine — toutes choses interdites tant que le contenu bouge. S'en
servir pour mesurer l'avancement rendait tout livrable éternellement « non
prêt » quel que soit le travail accompli. `DEVELOPMENT_READY` mesure ce qui
progresse ; `RELEASE_READY` conserve ses exigences intactes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_release_deliverable_readiness as readiness  # noqa: E402


@pytest.fixture(scope="module")
def payload():
    return readiness.build()


def test_development_readiness_never_requires_a_build_receipt(payload) -> None:
    assert payload["summary"]["CURRENT_BUILD_RECEIPTS_REQUIRED_DURING_DEVELOPMENT"] is False
    for row in payload["deliverables"]:
        assert "receipt" not in row["axes"]


def test_release_readiness_keeps_all_of_its_requirements(payload) -> None:
    """Aucun gate de release n'est affaibli par la nouvelle métrique."""
    assert payload["summary"]["RELEASE_READY"] == 0
    for row in payload["deliverables"]:
        assert row["release_ready"] is False
        assert set(row["release_ready_blocked_by"]) == {
            "FROZEN_HEAD", "FINAL_BUILD", "CURRENT_MANIFEST",
            "REPRODUCIBILITY", "PREFLIGHT", "HUMAN_APPROVAL",
        }


def test_the_twenty_four_required_deliverables_are_measured(payload) -> None:
    assert payload["summary"]["REQUIRED_RELEASE_DELIVERABLES"] == 24
    assert len(payload["deliverables"]) == 24


def test_a_deliverable_is_ready_only_when_every_axis_is_green(payload) -> None:
    for row in payload["deliverables"]:
        assert row["development_ready"] == all(row["axes"].values()), row["deliverable_id"]


def test_the_remaining_gaps_are_content_gaps(payload) -> None:
    """Chaque livrable non prêt l'est faute de contenu, pas faute d'outil."""
    not_ready = {
        row["deliverable_id"]: [axis for axis, ok in row["axes"].items() if not ok]
        for row in payload["deliverables"] if not row["development_ready"]
    }
    assert not_ready, "il reste des livrables à compléter"
    for deliverable, missing in not_ready.items():
        assert "content" in missing, deliverable
    # Les axes purement outillés sont fermés pour tout le monde.
    for row in payload["deliverables"]:
        assert row["axes"]["programme"], row["deliverable_id"]
        assert row["axes"]["science"], row["deliverable_id"]


def test_the_build_matcher_ignores_in_progress_work_directories(tmp_path: Path) -> None:
    """Le PDF d'un build en cours vit dans un répertoire caché : il ne compte pas."""
    root = tmp_path / "build"
    (root / "MANUEL_X" / ".MANUEL_X_eleve-abcdef").mkdir(parents=True)
    (root / "MANUEL_X" / ".MANUEL_X_eleve-abcdef" / "MANUEL_X_eleve.pdf").write_bytes(b"%PDF")
    original = dict(readiness.BUILD_ROOTS)
    try:
        readiness.BUILD_ROOTS.clear()
        readiness.BUILD_ROOTS["test"] = root
        assert readiness._development_build("X", "eleve")["present"] is False
        (root / "MANUEL_X" / "MANUEL_X_eleve.pdf").write_bytes(b"%PDF")
        assert readiness._development_build("X", "eleve")["present"] is True
    finally:
        readiness.BUILD_ROOTS.clear()
        readiness.BUILD_ROOTS.update(original)


def test_the_matcher_tolerates_hyphenated_build_directories() -> None:
    """Le scope écrit `TSPE_2026_2027`, le répertoire de build `TSPE_2026-2027`."""
    assert readiness._normalise("MANUEL_TSPE_2026-2027").endswith(
        readiness._normalise("TSPE_2026_2027")
    )


# --- Le contrôle de fuite élève ne doit pas confondre un adjectif ------------

def test_student_leak_pattern_ignores_the_adjective() -> None:
    """« l'invariant corrigé par une assertion » est un énoncé, pas un corrigé."""
    sys.path.insert(0, str(ROOT / "NSI/scripts"))
    import pdf_integrity

    innocent = "Écrire une fonction qui vérifie l'invariant corrigé par une assertion."
    assert pdf_integrity.BOOK_STUDENT_LEAK.search(innocent) is None
    assert pdf_integrity.BOOK_STUDENT_LEAK.search("Corriger le code pour garantir la terminaison.") is None

    for leak in ("Corrigé\nExercice 1", "  Corrigés\n", "Barème indicatif : 4 points"):
        assert pdf_integrity.BOOK_STUDENT_LEAK.search(leak) is not None, leak


# --- Le contenu se mesure en objets, pas en fichiers déclarés ----------------

def test_content_is_measured_by_real_objects_not_declared_files() -> None:
    """`included_files` compte les contrat.yaml des ouvertures de chapitre.

    Une variante sans le moindre objet en déclarait sept, et la maturité la
    comptait « contenu présent ». C'est ce faux vert qui a produit un 21/24
    au lieu de 18/24.

    `TNSI::amenagee` servait d'exemple vivant tant qu'elle était vide. Elle ne
    l'est plus : les sept extraits sont écrits. Le test fabrique donc le vide
    au lieu de l'emprunter à un livrable qu'on espère remplir — un assemblage
    dont on retire tous les objets ne doit compter aucun contenu, même si ses
    `included_files` restent peuplés de contrats.
    """
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    covered = readiness.content_coverage(inventory, "nsi:manual:TNSI:amenagee", "TNSI")
    assert covered["objects"] > 0

    emptied = json.loads(json.dumps(inventory))
    for manual in emptied["manuals"].values():
        for chapter in manual["chapters"].values():
            for key, items in list(chapter.items()):
                if isinstance(items, list):
                    chapter[key] = [
                        o for o in items
                        if not (isinstance(o, dict) and o.get("source_type") == "amenagee")
                    ]
    empty = readiness.content_coverage(emptied, "nsi:manual:TNSI:amenagee", "TNSI")
    assert empty["objects"] == 0
    assert empty["chapters_covered"] == 0
    assert empty["complete"] is False

    declared = [
        a for a in inventory.get("declared_assemblies", [])
        if a.get("assembly_id") == "nsi:manual:TNSI:amenagee"
    ]
    assert declared, "l'assemblage doit rester déclaré même vidé de ses objets"
    assert declared[0].get("included_files"), (
        "c'est précisément parce que `included_files` reste peuplé que le "
        "comptage doit se faire sur les objets"
    )


def test_a_booklet_covering_part_of_its_chapters_is_not_complete() -> None:
    """Couvrir une partie des chapitres ne suffit pas.

    Ce test prenait `1NSI::livret_methodes` comme exemple vivant d'un livret
    partiel. Il ne l'est plus : les vingt fiches justifiées ont été écrites.
    Continuer à l'exiger partiel reviendrait à interdire de le compléter.

    La partialité est donc fabriquée : on retire d'un inventaire complet les
    objets d'un chapitre, et on vérifie que la couverture le voit.
    """
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))

    full = readiness.content_coverage(inventory, "nsi:manual:1NSI:methodes", "1NSI")
    assert full["chapters_covered"] == full["chapters_total"]
    assert full["complete"] is True

    amputated = json.loads(json.dumps(inventory))
    for manual in amputated["manuals"].values():
        manual["chapters"].pop("1NSI-TABLES", None)
        for chapter_id, chapter in manual["chapters"].items():
            if chapter_id != "1NSI-RESEAUX":
                continue
            for key, items in list(chapter.items()):
                if isinstance(items, list):
                    chapter[key] = [
                        o for o in items
                        if not (isinstance(o, dict) and o.get("source_type") == "methode")
                    ]
    partial = readiness.content_coverage(amputated, "nsi:manual:1NSI:methodes", "1NSI")
    assert partial["objects"] > 0
    assert partial["chapters_covered"] < full["chapters_covered"]
    assert partial["complete"] is False

    reference = readiness.content_coverage(inventory, "math:manual:1SPE:methodes", "1SPE")
    assert reference["complete"] is True


def test_an_unknown_assembly_is_never_complete() -> None:
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    unknown = readiness.content_coverage(inventory, "nsi:manual:TNSI:ece", "TNSI")
    assert unknown["complete"] is False


def test_the_amenagee_forensics_agree_with_the_readiness_metric() -> None:
    """Les deux mesures doivent dire la même chose, quel que soit le nombre.

    Ce test exigeait zéro objet, l'état qui avait révélé la contradiction entre
    « CONTENT = oui » et un livret vide. Les sept extraits sont écrits ; exiger
    zéro reviendrait à exiger que le livret reste vide. Ce qui doit tenir, et
    qui tenait déjà, c'est l'accord entre le forensique et la maturité.
    """
    import build_tnsi_amenagee_forensics as forensics

    payload = forensics.build()
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    coverage = readiness.content_coverage(inventory, "nsi:manual:TNSI:amenagee", "TNSI")

    assert payload["summary"]["TNSI_AMENAGEE_SOURCE_OBJECTS"] == coverage["objects"]
    if coverage["objects"] == 0:
        assert payload["summary"]["TNSI_AMENAGEE_CLASSIFICATION"] == "EMPTY_VARIANT"
    else:
        assert payload["summary"]["TNSI_AMENAGEE_CLASSIFICATION"] != "EMPTY_VARIANT"


# --- Garde de vérité : le contenu se compte en objets déclarés ---------------

def test_only_inventory_declared_objects_count_as_content() -> None:
    """La source d'autorité est la liste d'objets de l'inventaire.

    Compter les `.tex` d'un assemblage laissait passer des includes techniques ;
    compter ses `included_files` laissait passer les `contrat.yaml`. Seul un
    objet que l'inventaire déclare est du contenu.
    """
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    declared = readiness.pedagogical_object_paths(inventory)
    assert declared, "l'inventaire doit déclarer des objets"
    assert not any(path.endswith("contrat.yaml") for path in declared)
    assert not any(path.endswith(".json") for path in declared)
    assert all(path.endswith(".tex") for path in declared)


def test_a_deliverable_made_only_of_contracts_is_never_content_complete() -> None:
    """Mutation exigée : contrats et configurations seuls ne font pas un produit."""
    inventory = {
        "manuals": {"X": {"chapters": {"X-CH1": {"objects": [
            {"id": "X-CH1-CO-1", "path": "chapitres/X-CH1/cours/a.tex"},
        ]}}}},
        "declared_assemblies": [{
            "assembly_id": "x:manual:X:amenagee",
            "scope": "manual",
            "included_files": [
                "chapitres/X-CH1/contrat.yaml",
                "chapitres/X-CH1/dossier_curation.json",
                "gabarits/common/nexus-manuel.cls",
            ],
        }],
    }
    coverage = readiness.content_coverage(inventory, "x:manual:X:amenagee", "X")
    assert coverage["objects"] == 0
    assert coverage["complete"] is False


def test_a_deliverable_with_one_real_object_per_chapter_is_content_complete() -> None:
    inventory = {
        "manuals": {"X": {"chapters": {
            "X-CH1": {"objects": [{"id": "a", "path": "chapitres/X-CH1/cours/a.tex"}]},
            "X-CH2": {"objects": [{"id": "b", "path": "chapitres/X-CH2/cours/b.tex"}]},
        }}},
        "declared_assemblies": [{
            "assembly_id": "x:manual:X:eleve", "scope": "manual",
            "included_files": [
                "chapitres/X-CH1/contrat.yaml",
                "chapitres/X-CH1/cours/a.tex",
                "chapitres/X-CH2/cours/b.tex",
            ],
        }],
    }
    coverage = readiness.content_coverage(inventory, "x:manual:X:eleve", "X")
    assert coverage["objects"] == 2
    assert coverage["complete"] is True

    # Retirer un chapitre du produit doit suffire à le rendre incomplet.
    inventory["declared_assemblies"][0]["included_files"].remove("chapitres/X-CH2/cours/b.tex")
    assert readiness.content_coverage(inventory, "x:manual:X:eleve", "X")["complete"] is False


def test_development_ready_is_a_pure_function_of_the_axes(payload) -> None:
    for row in payload["deliverables"]:
        assert row["development_ready"] is all(row["axes"].values())
