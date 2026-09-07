"""La requalification batch ne couvre que ce que la preuve couvre.

Décision humaine du Release Owner : les qualifications dont le changement est
STRICTEMENT diacritique peuvent être re-liées en un seul lot, sous une seule
identité, avec un seul receipt. Tout le reste est exclu.

Le danger de ce lot est évident : une autorisation formulée pour 86 objets
peut, par une erreur de filtre, en couvrir 89. Chaque test ci-dessous essaie
d'obtenir cette extension.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import diacritic_requalification as req  # noqa: E402


def test_only_accent_only_changes_are_eligible() -> None:
    items = [
        {"fingerprint": "a", "change_class": "ACCENT_ONLY"},
        {"fingerprint": "b", "change_class": "SUBSTANTIVE_CHANGE"},
        {"fingerprint": "c", "change_class": "PREVIOUS_REVISION_UNAVAILABLE"},
        {"fingerprint": "d", "change_class": "UNCHANGED"},
    ]
    assert [i["fingerprint"] for i in req.eligible(items)] == ["a"]


def test_a_digit_change_is_refused() -> None:
    assert req.recompute_change_class("x = 2", "x = 3") == "SUBSTANTIVE_CHANGE"


def test_a_formula_change_is_refused() -> None:
    assert req.recompute_change_class(
        r"$\dfrac{1}{2}$", r"$\dfrac{1}{3}$"
    ) == "SUBSTANTIVE_CHANGE"


def test_a_code_change_is_refused() -> None:
    assert req.recompute_change_class(
        "return None", "return -1"
    ) == "SUBSTANTIVE_CHANGE"


def test_a_non_diacritic_lexical_change_is_refused() -> None:
    assert req.recompute_change_class(
        "la suite est croissante", "la suite est décroissante"
    ) == "SUBSTANTIVE_CHANGE"


def test_an_added_sentence_is_refused() -> None:
    assert req.recompute_change_class(
        "Première phrase.", "Première phrase. Seconde phrase."
    ) == "SUBSTANTIVE_CHANGE"


def test_a_removed_sentence_is_refused() -> None:
    assert req.recompute_change_class(
        "Première phrase. Seconde phrase.", "Première phrase."
    ) == "SUBSTANTIVE_CHANGE"


def test_a_negation_change_is_refused() -> None:
    assert req.recompute_change_class(
        "la fonction est continue", "la fonction n'est pas continue"
    ) == "SUBSTANTIVE_CHANGE"


def test_a_reference_change_is_refused() -> None:
    assert req.recompute_change_class(
        r"\ref{th:1}", r"\ref{th:2}"
    ) == "SUBSTANTIVE_CHANGE"


def test_a_base_letter_change_is_refused() -> None:
    """Changer la lettre de base n'est pas un accent."""
    assert req.recompute_change_class("cote", "cate") == "SUBSTANTIVE_CHANGE"


def test_a_pure_accent_change_is_accepted() -> None:
    assert req.recompute_change_class("cote", "côté") == "ACCENT_ONLY"
    assert req.recompute_change_class(
        "problemes resolus", "problèmes résolus"
    ) == "ACCENT_ONLY"


def test_the_batch_refuses_a_fingerprint_outside_its_list() -> None:
    """Un objet hors de la liste ne peut pas hériter de l'autorisation."""
    receipt = {"qualification_ids": ["a", "b"]}
    assert req.covered_by(receipt, "a") is True
    assert req.covered_by(receipt, "z") is False


def test_the_receipt_carries_every_field_the_decision_named() -> None:
    exiges = {
        "REVIEWER_IDENTITY",
        "DECISION",
        "QUALIFICATION_COUNT",
        "QUALIFICATION_IDS_DIGEST",
        "OLD_PEDAGOGICAL_DIGESTS_DIGEST",
        "NEW_PEDAGOGICAL_DIGESTS_DIGEST",
        "DIACRITIC_FORENSICS_EVIDENCE_DIGEST",
    }
    assert exiges <= set(req.RECEIPT_FIELDS)


def test_the_receipt_digest_covers_the_list_not_just_the_count() -> None:
    """Deux lots de même taille mais de contenu différent doivent différer."""
    a = req.identifiers_digest(["x", "y"])
    b = req.identifiers_digest(["x", "z"])
    assert a != b
    assert req.identifiers_digest(["y", "x"]) == a, "l'ordre ne doit pas compter"


# --- Le lot déposé, et ce qu'il ne couvre pas ------------------------------

import json  # noqa: E402

RECEIPT = ROOT / "audit/DIACRITIC_REQUALIFICATION_BATCH_RECEIPT.json"
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"


@pytest.fixture(scope="module")
def receipt():
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_the_receipt_approves_nothing(receipt) -> None:
    assert receipt["approves_no_content"] is True
    assert receipt["promotes_no_status"] is True
    assert receipt["REVIEWER_IDENTITY"] == "abenrhouma"
    assert receipt["DECISION"] == req.DECISION


def test_the_count_matches_the_list(receipt) -> None:
    assert receipt["QUALIFICATION_COUNT"] == len(receipt["qualification_ids"])
    assert receipt["QUALIFICATION_COUNT"] == len(receipt["covered"])
    assert receipt["QUALIFICATION_IDS_DIGEST"] == req.identifiers_digest(
        receipt["qualification_ids"]
    )


def test_every_covered_item_was_accent_only(receipt) -> None:
    for entry in receipt["covered"]:
        assert entry["recomputed_change_class"] == req.ACCENT_ONLY, entry


def test_the_nominative_trigo_decision_is_not_overridden(receipt) -> None:
    """Une décision humaine ne s'annule pas par une autre, en silence.

    Trois qualifications remplissent la condition diacritique mais relèvent de
    la décision nominative du 2026-08-23 sur les extensions facultatives de
    1SPE-TRIGONOMETRIE, qui stipule `invalidate_on_source_change: true`. Les
    re-lier reviendrait à défaire cette décision sans que personne l'ait
    demandé.
    """
    exclues = {
        e["fingerprint"]: e["refus"] for e in receipt["excluded"]
    }
    trigo = {"70dfcb9ea3d7e1ec", "baf25a2d0a53d6dc", "dc0025fc58dc2e34"}
    assert trigo <= set(exclues)
    for fingerprint in trigo:
        assert any("autre décision humaine" in r for r in exclues[fingerprint])
        assert fingerprint not in set(receipt["qualification_ids"])


def test_the_three_substantive_changes_are_excluded(receipt) -> None:
    adgk = {"74aacd756bac15f4", "b0b81c9742c416e1", "ed9e59a472a9e4a5"}
    exclues = {e["fingerprint"] for e in receipt["excluded"]}
    assert adgk <= exclues
    assert not (adgk & set(receipt["qualification_ids"]))


def test_the_dispositions_changed_only_where_the_receipt_says(receipt) -> None:
    """Ni un enregistrement de plus, ni un champ de plus."""
    import subprocess

    import yaml

    avant = yaml.safe_load(
        subprocess.run(
            ["git", "show", "HEAD:audit/ANOMALY_DISPOSITIONS.yaml"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    )["dispositions"]
    apres = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))["dispositions"]

    assert set(avant) == set(apres), "aucune disposition ajoutée ni retirée"
    modifiees = {f for f in avant if avant[f] != apres[f]}
    couvertes = set(receipt["qualification_ids"])
    # Selon que le lot est déjà commité ou non, l'ensemble modifié est soit
    # vide, soit exactement celui du receipt. Jamais autre chose.
    assert modifiees in (set(), couvertes), sorted(modifiees - couvertes)[:5]
    for fingerprint in modifiees:
        champs = {
            k for k in set(avant[fingerprint]) | set(apres[fingerprint])
            if avant[fingerprint].get(k) != apres[fingerprint].get(k)
        }
        assert champs == {"method_source_sha", "requalification"}, (
            fingerprint, champs,
        )


def test_every_relinked_record_keeps_its_provenance(receipt) -> None:
    """L'ancienne empreinte reste inscrite : la neutralité reste vérifiable."""
    import yaml

    records = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))["dispositions"]
    for entry in receipt["covered"]:
        record = records[entry["fingerprint"]]
        requal = record.get("requalification")
        assert requal, entry["fingerprint"]
        assert requal["change_class"] == req.ACCENT_ONLY
        assert requal["reviewer_identity"] == "abenrhouma"
        assert requal["previous_method_source_sha"] == \
            entry["previous_method_source_sha"]
        assert record["method_source_sha"] == entry["current_method_source_sha"]
