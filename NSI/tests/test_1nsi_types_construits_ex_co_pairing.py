"""Reparation des liens EX/CO de 1NSI-TYPES-CONSTRUITS — tests cibles.

Les 55 corriges du chapitre ne portaient aucun champ de lien. L'autorite de la
relation est la declaration explicite du corps, `\\begin{corrige}{<EX-ID>}` ;
le suffixe numerique, le radical du nom de fichier et la capacite partagee ne
sont jamais des preuves suffisantes.

La regle de classement rejouee ici est celle de scripts/build_ex_co_graph.py :
un corrige sans reference, ou dont la reference ne resout pas vers un exercice
du chapitre, est un ORPHAN_CO.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

CHAPITRE = "1NSI-TYPES-CONSTRUITS"
RACINE = Path(__file__).resolve().parents[1] / "chapitres" / CHAPITRE
CLES_DE_LIEN = ("exercice_id", "exercice_ref")


def _meta(path: Path) -> dict:
    premiere = path.read_text(encoding="utf-8").split("\n")[0]
    trouve = re.search(r"% META:\s*(\{.*\})\s*$", premiere)
    assert trouve, f"{path.name} : en-tete META absent"
    return json.loads(trouve.group(1))


def _corps(path: Path) -> str:
    lignes = path.read_text(encoding="utf-8").split("\n")
    return "\n".join(l for l in lignes if not l.startswith("% META:")).strip()


def _declaration_du_corps(path: Path) -> list[str]:
    return sorted(set(re.findall(r"\\begin\{corrige\}\{([^}]*)\}", path.read_text(encoding="utf-8"))))


def _references(meta: dict) -> list[str]:
    return sorted(
        {str(meta[k]).strip() for k in CLES_DE_LIEN if isinstance(meta.get(k), str) and meta[k].strip()}
    )


@pytest.fixture(scope="module")
def exercices() -> dict[str, dict]:
    return {_meta(p)["id"]: _meta(p) for p in sorted((RACINE / "exercices").glob("*.tex"))}


@pytest.fixture(scope="module")
def corriges() -> list[Path]:
    fichiers = sorted((RACINE / "corriges").glob("*.tex"))
    assert fichiers, "aucun corrige lu"
    return fichiers


def test_chaque_corrige_porte_exactement_une_reference(corriges):
    """Le lien explicite existe, et il est unique : deux references valent MISMATCHED_CONTENT."""
    sans = [p.name for p in corriges if not _references(_meta(p))]
    multiples = [p.name for p in corriges if len(_references(_meta(p))) > 1]
    assert sans == [], f"corriges sans reference (ORPHAN_CO) : {sans}"
    assert multiples == [], f"corriges a references multiples : {multiples}"


def test_la_reference_reproduit_la_declaration_du_corps(corriges):
    """La METAdonnee ne doit jamais contredire l'autorite qui l'a produite."""
    for p in corriges:
        declare = _declaration_du_corps(p)
        assert len(declare) == 1, f"{p.name} : declaration de corps ambigue {declare}"
        assert _references(_meta(p)) == declare, (
            f"{p.name} : META {_references(_meta(p))} != corps {declare}"
        )


def test_la_cible_est_un_exercice_du_meme_chapitre(corriges, exercices):
    """Mauvais type de cible et mauvais chapitre echouent, comme chez le producteur."""
    for p in corriges:
        (reference,) = _references(_meta(p))
        cible = exercices.get(reference)
        assert cible is not None, f"{p.name} : cible {reference} introuvable (ORPHAN_CO)"
        assert cible["type_objet"] == "exercice", f"{p.name} : cible de type {cible['type_objet']}"
        assert cible["chapitre"] == CHAPITRE, f"{p.name} : cible hors chapitre"


def test_aucun_champ_de_lien_concurrent(corriges):
    """`exercice_ref` est le nom canonique du corpus ; `exercice_id` ne doit pas coexister."""
    concurrents = [p.name for p in corriges if "exercice_id" in _meta(p)]
    assert concurrents == [], f"champ non canonique encore present : {concurrents}"


def test_appariement_bijectif(corriges, exercices):
    """Un exercice, un corrige : ni exercice orphelin, ni corrige en double."""
    cibles = [_references(_meta(p))[0] for p in corriges]
    assert len(cibles) == len(set(cibles)), "deux corriges visent le meme exercice"
    assert set(cibles) == set(exercices), (
        f"exercices sans corrige : {sorted(set(exercices) - set(cibles))}"
    )


def test_le_corps_pedagogique_est_intact():
    """La reparation est declarative : les digests de corps sont ceux de la carte."""
    carte = json.loads(
        (RACINE.parents[2] / "audit" / "1nsi-local"
         / "TYPES_CONSTRUITS_EX_CO_LINK_REPAIR_MAP.json").read_text(encoding="utf-8")
    )
    import hashlib
    for ligne in carte["rows"]:
        chemin = RACINE.parents[2] / ligne["correction_path"]
        actuel = hashlib.sha256(_corps(chemin).encode()).hexdigest()
        assert actuel == ligne["body_sha256"], f"{chemin.name} : corps pedagogique modifie"
