"""Régression de couverture de la démarche de projet en Terminale NSI."""

import json
from pathlib import Path

import yaml


NSI_ROOT = Path(__file__).resolve().parents[1]
CHAPTER_ID = "TNSI-PROJET"
CHAPTER = NSI_ROOT / "chapitres" / CHAPTER_ID


def test_tnsi_project_unit_is_canonical_and_assembled():
    manifest = json.loads(
        (NSI_ROOT / "manifests/books/TNSI.json").read_text(encoding="utf-8")
    )
    chapter_ids = [chapter["id"] for chapter in manifest["chapters"]]

    assert chapter_ids.count(CHAPTER_ID) == 1
    assert chapter_ids[-1] == CHAPTER_ID
    assert (CHAPTER / "contrat.yaml").is_file()
    assert (CHAPTER / "projet/TNSI-PROJET-ANNUEL.tex").is_file()


def test_tnsi_project_contract_materialises_at_least_one_quarter_of_schedule():
    contract = yaml.safe_load((CHAPTER / "contrat.yaml").read_text(encoding="utf-8"))

    assert contract["chapitre"] == CHAPTER_ID
    assert contract["niveau"] == "TNSI"
    assert contract["statut"] == "needs_review"
    official = contract["programme_officiel"]
    assert official["NOR"] == "MENE1921247A"
    assert official["part_minimale"] == 0.25
    assert official["volume_projet_reference_h"] >= (
        official["volume_annuel_reference_h"] * official["part_minimale"]
    )
    assert min(contract["temps_estime_h"].values()) >= official["volume_projet_reference_h"]


def test_tnsi_project_unit_contains_operational_contract_and_exam_boundary():
    source = (CHAPTER / "projet/TNSI-PROJET-ANNUEL.tex").read_text(encoding="utf-8")

    required_markers = {
        "MENE1921247A",
        "au moins 25\\,\\%",
        "Prérequis",
        "Livrables obligatoires",
        "Jalons communs",
        "Grille d'évaluation",
        "Programme d'enseignement",
        "Définition de l'épreuve",
        "MENE2516123N",
        "ne remplace pas l'épreuve pratique",
    }
    missing = sorted(marker for marker in required_markers if marker not in source)
    assert missing == []

