"""Le lot doit perdre un objet dès qu'on lui fait subir autre chose qu'un accent.

Les tests unitaires prouvent que la fonction de classement distingue les cas.
Ceux-ci prouvent la même chose de bout en bout, sur le corpus réel : on mute un
fichier réellement couvert par le lot, on relance le tri complet, et on exige
que l'objet en sorte.

Chaque mutation est restaurée quoi qu'il arrive.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_diacritic_requalification_batch as batch  # noqa: E402

RECEIPT = ROOT / "audit/DIACRITIC_REQUALIFICATION_BATCH_RECEIPT.json"


@pytest.fixture(scope="module")
def cible():
    """Un objet réellement couvert par le lot, et son chemin."""
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    entry = receipt["covered"][0]
    return entry["fingerprint"], ROOT / entry["source"]


@pytest.fixture
def restaure():
    saved: list[tuple[Path, bytes]] = []

    def _garder(path: Path) -> None:
        saved.append((path, path.read_bytes()))

    yield _garder
    for path, content in saved:
        path.write_bytes(content)


def _couvert(fingerprint: str) -> bool:
    return fingerprint in {
        e["fingerprint"] for e in batch.assess(ROOT)["covered"]
    }


def test_the_target_is_covered_before_any_mutation(cible) -> None:
    fingerprint, _ = cible
    assert _couvert(fingerprint), "sans cela les mutations ne prouveraient rien"


@pytest.mark.parametrize(
    "recherche,remplacement,nom",
    [
        ("\\item", "\\item[1]", "ajout de marqueur"),
        ("e", "e ", "espace inséré"),
    ],
)
def test_a_structural_edit_drops_the_object(
    cible, restaure, recherche, remplacement, nom
) -> None:
    fingerprint, path = cible
    restaure(path)
    texte = path.read_text(encoding="utf-8")
    if recherche not in texte:
        pytest.skip(f"motif absent de la cible : {nom}")
    path.write_text(texte.replace(recherche, remplacement, 1), encoding="utf-8")
    assert not _couvert(fingerprint), nom


def test_an_added_sentence_drops_the_object(cible, restaure) -> None:
    fingerprint, path = cible
    restaure(path)
    texte = path.read_text(encoding="utf-8")
    path.write_text(texte + "\nUne phrase ajoutée après coup.\n", encoding="utf-8")
    assert not _couvert(fingerprint)


def test_a_removed_line_drops_the_object(cible, restaure) -> None:
    fingerprint, path = cible
    restaure(path)
    lignes = path.read_text(encoding="utf-8").split("\n")
    assert len(lignes) > 4
    path.write_text("\n".join(lignes[:-2]), encoding="utf-8")
    assert not _couvert(fingerprint)


def test_a_digit_change_drops_the_object(cible, restaure) -> None:
    fingerprint, path = cible
    restaure(path)
    texte = path.read_text(encoding="utf-8")
    for chiffre in "123456789":
        if chiffre in texte:
            suivant = str((int(chiffre) % 9) + 1)
            path.write_text(texte.replace(chiffre, suivant, 1), encoding="utf-8")
            assert not _couvert(fingerprint)
            return
    pytest.skip("aucun chiffre dans la cible")


def test_a_status_promotion_drops_the_object(cible, restaure) -> None:
    """Re-lier ne promeut rien : un statut promu sort du lot."""
    fingerprint, path = cible
    restaure(path)
    texte = path.read_text(encoding="utf-8")
    assert '"status": "needs_review"' in texte or '"status":"needs_review"' in texte
    path.write_text(
        texte.replace("needs_review", "approved", 1), encoding="utf-8"
    )
    assert not _couvert(fingerprint)


def test_the_object_returns_to_the_batch_once_restored(cible) -> None:
    """La fixture de restauration fait bien son travail."""
    fingerprint, _ = cible
    assert _couvert(fingerprint)
