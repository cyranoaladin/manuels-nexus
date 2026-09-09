"""INT-005 : la fiche de diagnostics porte les capacites du QCM dont elle derive."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SCRIPT = RACINE / "scripts" / "build_qcm_tex.py"


def _module():
    spec = importlib.util.spec_from_file_location("build_qcm_tex_int005", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _donnees(**extra) -> dict:
    return {
        "chapitre": "1NSI-X",
        "titre": "Faire le point",
        "questions": [
            {
                "id": "Q1",
                "capacite": "C1",
                "enonce": "Question ?",
                "options": {"A": "oui", "B": "non"},
                "correcte": "A",
                "diagnostics": {"B": {"erreur": "Confusion.", "renvoi": "C1"}},
            }
        ],
        "_source": "chapitres/1NSI-X/qcm/1NSI-X-QCM.json",
        "_statut_diagnostics": "needs_review",
        **extra,
    }


def _meta(rendu: str) -> dict:
    premiere = rendu.splitlines()[0]
    assert premiere.startswith("% META: ")
    return json.loads(premiere[len("% META: ") :])


def test_the_diagnostics_sheet_carries_the_qcm_capacities() -> None:
    module = _module()
    capacites = ["1NSI-X-C1", "1NSI-X-C2"]
    meta = _meta(module.rendre_diagnostics(_donnees(_capacites=capacites), "1NSI-X-QCM-DIAG"))
    assert meta["type_objet"] == "qcm_diagnostics"
    assert meta["capacites"] == capacites
    assert meta["genere_depuis"] == "chapitres/1NSI-X/qcm/1NSI-X-QCM.json"
    assert meta["status"] == "needs_review"
    # Meme ordre de cles que l'en-tete du QCM : capacites avant genere_depuis.
    assert list(meta) == ["id", "chapitre", "type_objet", "capacites", "genere_depuis", "status"]


def test_a_qcm_without_declared_capacities_yields_no_capacities_key() -> None:
    """Les QCM de mathematiques n'en portent pas : la fiche non plus."""

    module = _module()
    meta = _meta(module.rendre_diagnostics(_donnees(), "1SPE-X-QCM-DIAG"))
    assert "capacites" not in meta
    meta = _meta(module.rendre_diagnostics(_donnees(_capacites=None), "1SPE-X-QCM-DIAG"))
    assert "capacites" not in meta


def test_the_qcm_and_its_sheet_agree_on_the_same_capacities() -> None:
    module = _module()
    donnees = _donnees(_capacites=["1NSI-X-C1"], _identifiant="1NSI-X-QCM")
    qcm = _meta(module.rendre(donnees))
    sheet = _meta(module.rendre_diagnostics(donnees, "1NSI-X-QCM-DIAG"))
    assert qcm["capacites"] == sheet["capacites"] == ["1NSI-X-C1"]
