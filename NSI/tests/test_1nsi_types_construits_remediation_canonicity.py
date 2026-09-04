"""Unicite de la remediation de 1NSI-TYPES-CONSTRUITS.

Le chapitre portait six objets de remediation aux corps rigoureusement
identiques : le document canonique, qui traite R1 a R5 et declare les cinq
capacites, et cinq copies n'en declarant qu'une chacune. La machine y lisait
cinq remediations distinctes, donc une couverture de role acquise pour C1 a C5
alors qu'un seul document existait — un faux credit de capacite.

Ces tests ferment la porte : deux objets du chapitre ne peuvent pas partager un
corps tout en revendiquant des capacites differentes.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# INT-004 est ferme : les cinq copies ont ete retirees (0ca6f92b) et les deux
# registres d'attente 1NSI re-observes par le mecanisme canonique. Ces tests
# sont desormais des invariants permanents, sans dette temporaire.
COPIES_RETIREES = [f"1NSI-TC-REMED-0{n}" for n in range(1, 6)]

CHAPITRE = "1NSI-TYPES-CONSTRUITS"
RACINE = Path(__file__).resolve().parents[1] / "chapitres" / CHAPITRE
CANONIQUE = "1NSI-TC-REM"
CAPACITES = {f"{CHAPITRE}-C{n}" for n in range(1, 6)}
SEUIL_CORPS = 120  # en deca, un corps est trop court pour qu'une collision fasse sens


def _meta(path: Path) -> dict:
    trouve = re.search(r"% META:\s*(\{.*\})\s*$", path.read_text(encoding="utf-8").split("\n")[0])
    return json.loads(trouve.group(1)) if trouve else {}


def _corps(path: Path) -> str:
    lignes = path.read_text(encoding="utf-8").split("\n")
    return "\n".join(l for l in lignes if not l.startswith("% META:")).strip()


def _objets() -> list[tuple[str, Path, frozenset[str], str]]:
    sortie = []
    for path in sorted(RACINE.rglob("*.tex")):
        meta = _meta(path)
        corps = _corps(path)
        sortie.append(
            (
                meta.get("id", path.stem),
                path,
                frozenset(meta.get("capacites") or []),
                hashlib.sha256(corps.encode()).hexdigest() if len(corps) >= SEUIL_CORPS else "",
            )
        )
    return sortie


def test_aucun_clone_revendiquant_des_capacites_differentes():
    """Un corps partage entre deux capacites differentes est un faux credit."""
    par_corps: dict[str, list[tuple[str, frozenset[str]]]] = {}
    for objet_id, _, capacites, digest in _objets():
        if digest:
            par_corps.setdefault(digest, []).append((objet_id, capacites))
    fautifs = {
        digest: membres
        for digest, membres in par_corps.items()
        if len(membres) > 1 and len({c for _, c in membres}) > 1
    }
    assert fautifs == {}, f"clones revendiquant des capacites differentes : {fautifs}"


def test_une_seule_remediation_par_corps():
    """Deux fichiers de remediation ne doivent pas porter le meme corps."""
    digests: dict[str, list[str]] = {}
    for objet_id, path, _, digest in _objets():
        if path.parent.name == "remediation" and digest:
            digests.setdefault(digest, []).append(objet_id)
    doublons = {d: ids for d, ids in digests.items() if len(ids) > 1}
    assert doublons == {}, f"remediations en doublon : {doublons}"


def test_le_document_canonique_couvre_les_cinq_capacites():
    """La couverture de role de la remediation repose sur ce seul document."""
    fichiers = {objet_id: (path, caps) for objet_id, path, caps, _ in _objets()}
    assert CANONIQUE in fichiers, f"{CANONIQUE} absent"
    path, capacites = fichiers[CANONIQUE]
    assert capacites == CAPACITES, f"{CANONIQUE} declare {sorted(capacites)}"
    texte = path.read_text(encoding="utf-8")
    for numero in range(1, 6):
        assert re.search(rf"R{numero}\b.*\(C{numero}\)", texte), (
            f"{CANONIQUE} : section R{numero} traitant C{numero} introuvable"
        )


def test_chaque_capacite_garde_une_remediation():
    """Le retrait des copies ne doit laisser aucune capacite sans remediation."""
    couvertes: set[str] = set()
    for _, path, capacites, _ in _objets():
        if path.parent.name == "remediation":
            couvertes |= capacites
    assert CAPACITES <= couvertes, f"capacites sans remediation : {sorted(CAPACITES - couvertes)}"


def test_les_cinq_copies_redondantes_sont_absentes():
    """INT-004 : les cinq copies ne doivent jamais revenir."""
    presents = {objet_id for objet_id, _, _, _ in _objets()}
    revenus = sorted(set(COPIES_RETIREES) & presents)
    assert revenus == [], f"copies redondantes reapparues : {revenus}"
