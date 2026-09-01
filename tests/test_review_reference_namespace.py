r"""Un renvoi de QCM ne doit jamais etre montre sans son espace de noms.

`M7` designe une methode du chapitre ; `R5` designe un PREREQUIS du contrat --
« Python : variables, boucle for, boucle while », herite de SNT -- servi par la
fiche `FR-R5`. Ce n'est ni la capacite `C5`, ni l'objet de remediation `RE-C5`.

Presente a un expert sous le seul intitule « remediation_reference », la lettre
R se lit comme un objet de remediation. Un dossier qui aplatit deux espaces de
noms fait signer une chose pour une autre : c'est pourquoi la resolution
precede toute signature humaine.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"


@pytest.fixture(scope="module")
def resolver():
    spec = importlib.util.spec_from_file_location(
        "review_reference_namespace", ROOT / "scripts/review_reference_namespace.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_a_prerequisite_is_never_presented_as_a_capacity(resolver) -> None:
    (row,) = resolver.resolve("R5", CHAPTER)
    assert row["namespace"] == resolver.PREREQUIS
    assert row["code"] == "R5"
    assert "Python" in row["label"]
    assert row["object_id"] == "1SPE-SUITES-FR-R5"
    assert "n'est pas C5" in row["note"]


def test_a_method_resolves_to_the_chapter_method_object(resolver) -> None:
    (row,) = resolver.resolve("M7, Modele B, etape 1", CHAPTER)
    assert row["namespace"] == resolver.METHODE
    assert row["object_id"] == "1SPE-SUITES-ME-007"


def test_a_mixed_reference_keeps_both_namespaces_apart(resolver) -> None:
    rows = resolver.resolve("M5, Methode A ; R3", CHAPTER)
    assert [r["namespace"] for r in rows] == [resolver.METHODE, resolver.PREREQUIS]


def test_an_unknown_code_is_never_guessed(resolver) -> None:
    """Echec ferme : un code que ni l'un ni l'autre espace ne reconnait."""
    assert resolver.resolve("Z9", CHAPTER) == []
    (row,) = resolver.resolve("R9", CHAPTER)
    assert row["namespace"] == resolver.UNKNOWN


def test_the_namespaces_come_from_the_chapter_not_from_a_table(
    resolver, tmp_path: Path
) -> None:
    """Les prerequis sont lus au contrat du chapitre, pas dans une table figee.

    Un chapitre fictif declarant un R1 different doit rendre CE libelle : si le
    module portait une table, il rendrait celui de 1SPE-SUITES.
    """
    chapter = tmp_path / "1SPE-FICTIF"
    (chapter / "remediation").mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        "prerequis:\n"
        '  - { code: R1, libelle: "Geometrie du triangle", chapitre_origine: "2GT" }\n',
        encoding="utf-8",
    )
    (row,) = resolver.resolve("R1", chapter)
    assert row["namespace"] == resolver.PREREQUIS
    assert row["label"] == "Geometrie du triangle"
    # La fiche de remediation n'existe pas ici : rien n'est invente.
    assert row["object_id"] is None


def test_every_packet_reference_is_resolved_before_human_signature() -> None:
    for name in (
        "1SPE_SUITES_EXPERT_MATHEMATIQUE_NEUTRAL_REVIEW_PACKET.json",
        "1SPE_SUITES_EXPERT_PROGRAMME_PEDAGOGIE_NEUTRAL_REVIEW_PACKET.json",
    ):
        packet = json.loads((ROOT / "audit" / name).read_text(encoding="utf-8"))
        for question in packet["qcm_review_material"]["questions"]:
            for diagnostic in question.get("diagnostics") or []:
                if not isinstance(diagnostic.get("remediation_reference"), str):
                    continue
                resolved = diagnostic.get("resolved_references")
                assert resolved is not None, question["question_id"]
                for row in resolved:
                    assert row["namespace"] in {"METHODE", "PREREQUIS", "UNKNOWN"}
