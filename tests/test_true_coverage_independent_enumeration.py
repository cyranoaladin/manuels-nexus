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
CORE_META_ROLES = ("cours", "methodes", "exercices", "corriges", "remediation")
TEX_META_ROLES = CORE_META_ROLES + ("evaluations",)
MEASURED_ROLES = CORE_META_ROLES + ("qcm", "evaluations")
ROLE_OBJECT_TYPES = {
    "cours": {"cours"},
    "methodes": {"methode"},
    "exercices": {"exercice"},
    "corriges": {"corrige", "correction"},
    "remediation": {"remediation"},
    "evaluations": {"evaluation"},
}
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


def _independent_declared_strings(
    chapter: str, meta: dict, capacities: list[dict]
) -> tuple[set[str], list[str]]:
    """Resolve fields forward from the contract without the canonical resolver."""

    accepted_by_code = {
        str(entry["code"]).strip(): _accepted_strings(chapter, entry)
        for entry in capacities
    }
    resolved_fields: list[tuple[str, set[str], set[str]]] = []
    errors: list[str] = []
    for key in ("capacites_codes", "capacites"):
        if key not in meta or meta.get(key) is None:
            continue
        values = meta[key]
        if not isinstance(values, list):
            errors.append(f"{chapter}/INVALID_FIELD:{key}")
            continue
        raw: set[str] = set()
        for value in values:
            if not isinstance(value, str):
                errors.append(f"{chapter}/INVALID_CAPACITY_TYPE:{key}")
                continue
            normalised = value.strip()
            if not normalised:
                errors.append(f"{chapter}/EMPTY_CAPACITY:{key}")
                continue
            raw.add(normalised)
        codes: set[str] = set()
        for value in sorted(raw):
            candidates = {
                code for code, accepted in accepted_by_code.items() if value in accepted
            }
            if len(candidates) != 1:
                errors.append(f"{chapter}/{value or 'EMPTY_CAPACITY'}")
            else:
                codes |= candidates
        resolved_fields.append((key, raw, codes))
    if errors:
        return set(), errors
    if len(resolved_fields) > 1 and any(
        codes != resolved_fields[0][2]
        for _key, _raw, codes in resolved_fields[1:]
    ):
        return set(), [f"{chapter}/AMBIGUOUS_META_CAPACITY_FIELDS"]
    return set().union(*(raw for _key, raw, _codes in resolved_fields)), []


def _single_qcm_source(paths: list[Path], chapter: str) -> list[Path]:
    if len(paths) > 1:
        raise AssertionError(f"{chapter}: MULTIPLE_QCM_SOURCES")
    return paths


def _independent_qcm_capacity(
    chapter: str, value: object, accepted: set[str]
) -> tuple[str | None, list[str]]:
    """Valide une déclaration QCM sans coercition de type ni best effort."""

    if not isinstance(value, str):
        return None, [f"{chapter}/INVALID_QCM_CAPACITY_TYPE"]
    raw = value.strip()
    if not raw:
        return None, [f"{chapter}/EMPTY_QCM_CAPACITY"]
    if raw not in accepted:
        return None, [f"{chapter}/{raw}"]
    return raw, []


def _independent_cells() -> tuple[dict[tuple[str, str, str], str], list[str]]:
    ledger = json.loads(
        (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
    )
    invalid = set(ledger["objects_on_invalid_credit"])
    # Un clone dont le proprietaire n'est pas demontrable ne credite pas, mais
    # sa cellule n'est pas vide pour autant : elle est a revoir, pas a ecrire.
    indeterminate = set(ledger["objects_with_indeterminate_credit"])

    cells: dict[tuple[str, str, str], str] = {}
    unknown: list[str] = []
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
            accepted_collection = set().union(
                *(_accepted_strings(chapter, entry) for entry in capacities)
            )

            # Les declarations brutes de chaque objet du chapitre, par role,
            # plus l'heritage des corriges depuis leur exercice.
            declarations: dict[tuple[str, str], set[str]] = {}
            pending_credit: dict[tuple[str, str], set[str]] = {}
            by_object: dict[str, tuple[set[str], str, str, str, str]] = {}
            pending: list[tuple[str, str, str, str, set[str]]] = []
            for path in sorted(directory.rglob("*.tex")):
                if "_harvest" in path.parts:
                    continue
                parts = path.parts
                role = parts[parts.index(chapter) + 1]
                if role not in TEX_META_ROLES:
                    continue
                meta = _meta(path.read_text(encoding="utf-8", errors="replace"))
                if str(meta.get("type_objet") or "").strip() not in ROLE_OBJECT_TYPES[role]:
                    continue
                raw, declaration_errors = _independent_declared_strings(
                    chapter, meta, capacities
                )
                unknown.extend(declaration_errors)
                relative = str(path.relative_to(ROOT))
                credit_state = (
                    "INVALID"
                    if relative in invalid
                    else "INDETERMINATE"
                    if relative in indeterminate
                    else "VALID"
                )
                if meta.get("id"):
                    by_object[str(meta["id"])] = (
                        raw,
                        credit_state,
                        chapter,
                        role,
                        str(meta.get("type_objet") or "").strip(),
                    )
                if relative in invalid:
                    continue
                target = (
                    pending_credit if relative in indeterminate else declarations
                )
                reference = {
                    str(meta[key]).strip()
                    for key in ("exercice_id", "exercice_ref")
                    if meta.get(key)
                }
                if role == "corriges" and reference:
                    if len(reference) != 1:
                        raise AssertionError(
                            f"{relative}: heritage exercice contradictoire"
                        )
                    pending.append(
                        (role, relative, next(iter(reference)), chapter, raw)
                    )
                elif raw:
                    target.setdefault((role, relative), set()).update(raw)

            # Chemin indépendant du producteur : les chaînes des questions
            # sont rapprochées de l'ensemble construit en avant depuis le
            # contrat, sans appel au resolver.
            qcm_paths = _single_qcm_source(
                sorted((directory / "qcm").glob("*-QCM.json")), chapter
            )
            for qcm_path in qcm_paths:
                qcm = json.loads(qcm_path.read_text(encoding="utf-8"))
                if qcm.get("chapitre") != chapter:
                    unknown.append(f"{chapter}/QCM_CHAPTER_MISMATCH")
                    continue
                for question in qcm.get("questions") or []:
                    raw_capacity, capacity_errors = _independent_qcm_capacity(
                        chapter, question.get("capacite"), accepted_collection
                    )
                    unknown.extend(capacity_errors)
                    if raw_capacity is None:
                        continue
                    relative = str(qcm_path.relative_to(ROOT))
                    declarations.setdefault(
                        ("qcm", f"{relative}#{question.get('id')}"), set()
                    ).add(raw_capacity)
            def canonical_codes(raw_values: set[str]) -> set[str]:
                return {
                    str(entry["code"]).strip()
                    for entry in capacities
                    if _accepted_strings(chapter, entry) & raw_values
                }

            for role, relative, exercise, correction_chapter, declared in pending:
                inherited = by_object.get(exercise)
                if inherited:
                    (
                        raw,
                        exercise_state,
                        exercise_chapter,
                        exercise_role,
                        exercise_type,
                    ) = inherited
                    if exercise_chapter != correction_chapter:
                        raise AssertionError(
                            f"{relative}: heritage interchapitres depuis {exercise}"
                        )
                    if exercise_role != "exercices" or exercise_type != "exercice":
                        continue
                    if declared and canonical_codes(declared) != canonical_codes(raw):
                        continue
                    if exercise_state == "INVALID":
                        continue
                    target = (
                        pending_credit
                        if relative in indeterminate
                        or exercise_state == "INDETERMINATE"
                        else declarations
                    )
                    target.setdefault((role, relative), set()).update(declared or raw)

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
                    key = (chapter, str(entry["code"]).strip(), role)
                    cells[key] = (
                        "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
                        if served
                        else "INDETERMINATE_CLONE_CREDIT"
                        if undetermined
                        else "MISSING"
                    )
    return cells, sorted(set(unknown))


@pytest.fixture(scope="module")
def canonical_payload() -> dict:
    return json.loads(
        (ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def canonical_states(canonical_payload) -> dict[tuple[str, str, str], str]:
    return {
        (row["chapter"], row["capacity"], row["role"]): row["state"]
        for row in canonical_payload["rows"]
    }


@pytest.fixture(scope="module")
def canonical(canonical_states) -> set[tuple[str, str, str]]:
    return {key for key, state in canonical_states.items() if state == "MISSING"}


@pytest.fixture(scope="module")
def independent_result() -> tuple[dict[tuple[str, str, str], str], list[str]]:
    return _independent_cells()


@pytest.fixture(scope="module")
def independent(independent_result) -> set[tuple[str, str, str]]:
    states, _unknown = independent_result
    return {key for key, state in states.items() if state == "MISSING"}


def test_the_two_paths_agree_on_every_cell_state(
    canonical_states, independent_result
) -> None:
    independent_states, unknown = independent_result
    canonical_payload = json.loads(
        (ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text(encoding="utf-8")
    )
    canonical_blockers = sorted(
        {
            f"{row['path'].split('/chapitres/', 1)[1].split('/', 1)[0]}/"
            f"{row['reason'].split('le prerequis ', 1)[1].split(' ', 1)[0]}"
            for row in canonical_payload.get("capacity_identity_blockers", [])
            if "le prerequis " in row.get("reason", "")
        }
    )
    assert unknown == canonical_blockers
    assert independent_states == canonical_states, {
        "canonical_only": sorted(set(canonical_states) - set(independent_states))[:10],
        "independent_only": sorted(set(independent_states) - set(canonical_states))[:10],
        "state_mismatches": sorted(
            key
            for key in set(canonical_states) & set(independent_states)
            if canonical_states[key] != independent_states[key]
        )[:10],
    }


def test_false_identity_collision_missing_and_positive_credits_are_zero(
    canonical_states, independent_result
) -> None:
    """Les deux chemins excluent les collisions d'identité, pas les faux sens.

    Cette égalité porte exclusivement sur la résolution déclarative exacte.
    Elle ne relit pas le sens des corps et ne peut donc pas établir
    ``FALSE_POSITIVE_CREDITS = 0`` au niveau sémantique.
    """
    independent_states, _unknown = independent_result
    assert {
        key
        for key, state in canonical_states.items()
        if state == "MISSING" and independent_states.get(key) != "MISSING"
    } == set()
    assert {
        key
        for key, state in canonical_states.items()
        if state == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
        and independent_states.get(key)
        != "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
    } == set()


def test_the_two_paths_agree_unit_by_unit(
    canonical, independent, canonical_payload
) -> None:
    assert independent == canonical, {
        "seulement_canonique": sorted(canonical - independent)[:10],
        "seulement_independant": sorted(independent - canonical)[:10],
    }
    assert len(canonical) == canonical_payload["inventory"]["authoring_units_required"]


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


def test_1nsi_agrees_chapter_by_chapter(canonical, independent) -> None:
    """1NSI porte la majorite des unites retirees : c'est la qu'il faut regarder."""

    left = collections.Counter(c for c, _k, _r in canonical if c.startswith("1NSI"))
    right = collections.Counter(c for c, _k, _r in independent if c.startswith("1NSI"))
    assert left == right
    assert sum(left.values()) == sum(right.values())


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
    """FALSE_IDENTITY_COLLISION_CREDITS = 0 sur le cas C1/C10.

    Le sens inverse du même contrôle prouve seulement qu'une déclaration
    exacte de C10 n'est pas attribuée à C1. La validité sémantique du corps
    reste ``UNKNOWN`` jusqu'au ledger sémantique indépendant.
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


def test_independent_declaration_rejects_prerequisite_in_capacity_field() -> None:
    raw, errors = _independent_declared_strings(
        "1NSI-X",
        {"capacites_codes": ["R1"]},
        [{"code": "C1", "ref_capacite": "P-X-C1"}],
    )
    assert raw == set()
    assert errors == ["1NSI-X/R1"]


def test_independent_declaration_rejects_contradictory_dual_fields() -> None:
    raw, errors = _independent_declared_strings(
        "1NSI-X",
        {"capacites_codes": ["C1"], "capacites": ["P-X-C2"]},
        [
            {"code": "C1", "ref_capacite": "P-X-C1"},
            {"code": "C2", "ref_capacite": "P-X-C2"},
        ],
    )
    assert raw == set()
    assert errors == ["1NSI-X/AMBIGUOUS_META_CAPACITY_FIELDS"]


@pytest.mark.parametrize("value", ["", "   ", 1, {"code": "C1"}])
def test_independent_declaration_rejects_malformed_values(value: object) -> None:
    raw, errors = _independent_declared_strings(
        "1NSI-X",
        {"capacites_codes": [value]},
        [{"code": "C1", "ref_capacite": "P-X-C1"}],
    )
    assert raw == set()
    assert errors


@pytest.mark.parametrize("value", [None, "", "   ", 1, {"code": "C1"}])
def test_independent_qcm_rejects_malformed_capacity_values(value: object) -> None:
    raw, errors = _independent_qcm_capacity(
        "1NSI-X", value, {"C1", "P-X-C1"}
    )
    assert raw is None
    assert errors


def test_independent_qcm_source_selection_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="MULTIPLE_QCM_SOURCES"):
        _single_qcm_source([tmp_path / "a.json", tmp_path / "b.json"], "1NSI-X")
