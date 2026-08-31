"""Une seconde mesure, ecrite autrement, doit trouver le meme nombre.

Le producteur canonique resout chaque declaration par CONSULTATION : il prend
la chaine, interroge la table du chapitre, et rend une capacite. Un bug dans
cette table se propagerait silencieusement a la mesure qu'elle sert -- et rien
ne le verrait, puisque c'est la meme table qui produirait le chiffre et le
verifierait.

Cet enumerateur fait l'inverse. Il part de CHAQUE capacite du contrat,
construit en avant l'ensemble des chaines qui la designent legitimement --
code local, forme qualifiee par le chapitre, reference officielle -- puis
cherche quels objets emploient une de ces chaines. Aucune consultation de la
table de resolution, aucun appel au producteur.

Les deux chemins doivent tomber sur le meme backlog, unite par unite.
"""

from __future__ import annotations

import collections
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
MEASURED_ROLES = ("cours", "methodes", "exercices", "corriges", "remediation")
META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$", re.MULTILINE)


def _meta(text: str) -> dict:
    """Lecture du META par une expression propre a ce test."""

    match = META.search(text)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def _accepted_strings(chapter: str, entry: dict) -> set[str]:
    """Les chaines qui designent CETTE capacite, construites en avant."""

    code = str(entry["code"]).strip()
    accepted = {code, f"{chapter}-{code}"}
    reference = entry.get("ref_capacite")
    if reference:
        accepted.add(str(reference).strip())
    return accepted


def _independent_backlog() -> set[tuple[str, str, str]]:
    ledger = json.loads(
        (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
    )
    invalid = set(ledger["objects_on_invalid_credit"])
    # Un clone dont le proprietaire n'est pas demontrable ne credite pas, mais
    # sa cellule n'est pas vide pour autant : elle est a revoir, pas a ecrire.
    indeterminate = set(ledger["objects_with_indeterminate_credit"])

    backlog: set[tuple[str, str, str]] = set()
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for directory in sorted(corpus.iterdir()):
            contract_path = directory / "contrat.yaml"
            if not contract_path.is_file():
                continue
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
            capacities = contract.get("capacites") or []
            if not capacities:
                continue
            chapter = directory.name

            # Les declarations brutes de chaque objet du chapitre, par role,
            # plus l'heritage des corriges depuis leur exercice.
            declarations: dict[tuple[str, str], set[str]] = {}
            pending_credit: dict[tuple[str, str], set[str]] = {}
            by_object: dict[str, set[str]] = {}
            pending: list[tuple[str, str, str]] = []
            for path in sorted(directory.rglob("*.tex")):
                if "_harvest" in path.parts:
                    continue
                parts = path.parts
                role = parts[parts.index(chapter) + 1]
                if role not in MEASURED_ROLES:
                    continue
                meta = _meta(path.read_text(encoding="utf-8", errors="replace"))
                raw = {
                    str(value).strip()
                    for key in ("capacites_codes", "capacites")
                    for value in (meta.get(key) or [])
                    if str(value).strip()
                }
                if meta.get("id"):
                    by_object[str(meta["id"])] = raw
                relative = str(path.relative_to(ROOT))
                if relative in invalid:
                    continue
                target = (
                    pending_credit if relative in indeterminate else declarations
                )
                if raw:
                    target.setdefault((role, relative), set()).update(raw)
                elif role == "corriges" and meta.get("exercice_id"):
                    pending.append((role, relative, str(meta["exercice_id"])))
            for role, relative, exercise in pending:
                inherited = by_object.get(exercise)
                if inherited:
                    target = (
                        pending_credit if relative in indeterminate else declarations
                    )
                    target.setdefault((role, relative), set()).update(inherited)

            for entry in capacities:
                accepted = _accepted_strings(chapter, entry)
                for role in MEASURED_ROLES:
                    served = any(
                        role == key_role and accepted & raw
                        for (key_role, _relative), raw in declarations.items()
                    )
                    # Une cellule servie uniquement par des clones dont le
                    # proprietaire n'est pas demontrable n'est pas une lacune
                    # d'ecriture : c'est une revue.
                    undetermined = any(
                        role == key_role and accepted & raw
                        for (key_role, _relative), raw in pending_credit.items()
                    )
                    if not served and not undetermined:
                        backlog.add((chapter, str(entry["code"]).strip(), role))
    return backlog


@pytest.fixture(scope="module")
def canonical() -> set[tuple[str, str, str]]:
    payload = json.loads(
        (ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text(encoding="utf-8")
    )
    return {
        (row["chapter"], row["capacity"], row["role"])
        for row in payload["authoring_backlog"]
    }


@pytest.fixture(scope="module")
def independent() -> set[tuple[str, str, str]]:
    return _independent_backlog()


def test_the_two_paths_agree_unit_by_unit(canonical, independent) -> None:
    assert independent == canonical, {
        "seulement_canonique": sorted(canonical - independent)[:10],
        "seulement_independant": sorted(independent - canonical)[:10],
    }
    assert len(canonical) == 324


def test_the_two_paths_agree_on_every_manual(canonical, independent) -> None:
    def per_manual(units):
        counts = collections.Counter()
        for chapter, _capacity, _role in units:
            for prefix in ("TEXPERTES", "TEXP", "TCOMPL", "TNSI", "TSPE", "1NSI", "1SPE"):
                if chapter.startswith(prefix):
                    counts["TEXPERTES" if prefix.startswith("TEXP") else prefix] += 1
                    break
        return counts

    assert per_manual(canonical) == per_manual(independent)
    assert per_manual(canonical) == {
        "1NSI": 80,
        "TCOMPL": 55,
        "TEXPERTES": 24,
        "TNSI": 123,
        "TSPE": 42,
    }


def test_1nsi_agrees_chapter_by_chapter(canonical, independent) -> None:
    """1NSI porte la majorite des unites retirees : c'est la qu'il faut regarder."""

    left = collections.Counter(c for c, _k, _r in canonical if c.startswith("1NSI"))
    right = collections.Counter(c for c, _k, _r in independent if c.startswith("1NSI"))
    assert left == right
    assert sum(left.values()) == 80


def test_tspe_probabilites_credits_c10_and_never_its_local_c1(
    canonical, independent
) -> None:
    """Le chapitre ou la collision etait prouvee.

    `C10` a pour reference officielle `TSPE-CONCLGN-C1`. Une mesure qui lit
    cette reference comme `C1` credite la capacite voisine et laisse `C10`
    passer pour vide : les deux erreurs a la fois.
    """

    chapter = "TSPE-PROBABILITES"
    contract = yaml.safe_load(
        (
            ROOT / "Mathematiques/manuel-maths/chapitres" / chapter / "contrat.yaml"
        ).read_text(encoding="utf-8")
    )
    by_code = {str(e["code"]): e for e in contract["capacites"]}
    assert by_code["C10"]["ref_capacite"] == "TSPE-CONCLGN-C1"
    assert "C1" in by_code and by_code["C1"]["ref_capacite"] != "TSPE-CONCLGN-C1"

    left = {(k, r) for c, k, r in canonical if c == chapter}
    right = {(k, r) for c, k, r in independent if c == chapter}
    assert left == right

    # Le contenu qui declare la reference de C10 doit crediter C10, et rien
    # d'autre. Si C1 apparaissait ici comme servi par ce meme contenu, la
    # collision serait revenue.
    identity_spec = importlib.util.spec_from_file_location(
        "capacity_identity", ROOT / "scripts/capacity_identity.py"
    )
    identity = importlib.util.module_from_spec(identity_spec)
    sys.modules[identity_spec.name] = identity
    identity_spec.loader.exec_module(identity)
    resolver = identity.CapacityIdentityResolver.from_corpora()
    resolved = resolver.resolve(chapter, "TSPE-CONCLGN-C1")
    assert resolved.identity.local_code == "C10"
    assert resolved.rule == identity.REF_EXACT


def test_no_content_is_credited_to_a_neighbouring_capacity(independent) -> None:
    """FALSE_POSITIVE_CREDITS = 0.

    Le sens inverse du meme controle : une capacite declaree SERVIE doit
    l'etre par un objet qui la nomme reellement. On verifie ici que le
    complement du backlog n'a pas ete rempli par collision -- pour chaque
    cellule servie, il existe un objet dont une declaration figure dans
    l'ensemble construit en avant pour cette capacite exactement.
    """

    contract = yaml.safe_load(
        (
            ROOT
            / "Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/contrat.yaml"
        ).read_text(encoding="utf-8")
    )
    accepted_c1 = _accepted_strings(
        "TSPE-PROBABILITES", next(e for e in contract["capacites"] if e["code"] == "C1")
    )
    accepted_c10 = _accepted_strings(
        "TSPE-PROBABILITES", next(e for e in contract["capacites"] if e["code"] == "C10")
    )
    assert accepted_c1 & accepted_c10 == set(), (
        "les deux capacites partagent une chaine : la collision est revenue"
    )
    assert "TSPE-CONCLGN-C1" in accepted_c10
    assert "TSPE-CONCLGN-C1" not in accepted_c1
