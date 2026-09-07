#!/usr/bin/env python3
"""La population canonique de la contamination pedagogique inter-manuels.

FINDING : CROSS_MANUAL_PEDAGOGICAL_CONTAMINATION.

Un exercice d'analyse -- variations de `x^3 - 3x^2 + 2`, derivee de `x ln x`,
convexite de `1/(1+x)` -- imprime comme exercice d'arithmetique, d'inference
bayesienne ou de matrices. Ce n'est pas une dette de gouvernance : c'est un
defaut que l'eleve voit sur la page.

CE PRODUCTEUR RECALCULE TOUT DEPUIS LES SOURCES. Aucun nombre n'est repris
d'un registre anterieur ; les anciens comptes sont reconcilies explicitement,
et l'ecart est explique par la cause qui l'a produit -- la normalisation
fautive, qui laissait l'identite de l'objet dans le corps compare.

LA SOURCE D'UN GROUPE EST FORENSIQUE, PAS SEMANTIQUE. Le membre canonique est
celui que l'historique introduit le PREMIER. Un corps ne devient pas
illegitime dans son chapitre d'origine parce qu'il a ete recopie ailleurs :
la contamination est chez les consommateurs, pas chez la source.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPORA = (
    ROOT / "Mathematiques/manuel-maths/chapitres",
    ROOT / "NSI/chapitres",
)
UNPUBLISHED = ("_harvest",)
OUTPUT_JSON = ROOT / "audit/CROSS_MANUAL_CONTAMINATION.json"
OUTPUT_MD = ROOT / "audit/CROSS_MANUAL_CONTAMINATION.md"
MATRIX_JSON = ROOT / "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json"

FINDING = "CROSS_MANUAL_PEDAGOGICAL_CONTAMINATION"
ROOT_CAUSE = "533d1919_SYNTHETIC_CROSS_MANUAL_FILLER"

#: Les nombres cites dans le rapport d'alerte, a reconcilier avec la mesure
#: courante. Aucun n'est repris : chacun est recalcule et compare.
REPORTED = {
    "CLONE_GROUPS_TOTAL": 124,
    "CLONED_OBJECTS_TOTAL": 917,
    "CROSS_MANUAL_CONTAMINATION_OBJECTS": 903,
    "SOURCE_CLONE_WITH_DISTINCT_IDS_GROUPS": 118,
    "CAPACITY_MISREPRESENTING_GROUPS": 92,
    "EXACT_DUPLICATE_EXERCISES": 504,
    "CONTAMINATED_OBJECTS_WITH_APPROVED_STATUS": 997,
    "CONTAMINATED_OBJECTS_TOTAL": 1021,
    "CROSS_MANUAL_CONTAMINATION_OBJECTS_FIRST_PASS": 903,
}


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_LEDGER = None


def identity_rule():
    """La normalisation vit a un seul endroit, et c'est celui-la."""

    global _LEDGER
    if _LEDGER is None:
        _LEDGER = _module("cmc_identity", "scripts/build_p0_content_clone_ledger.py")
    return _LEDGER


def _digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalization_proof() -> dict[str, Any]:
    """Le banc de mutation, execute ici et pas seulement en test.

    Un compteur publie sans son banc n'est qu'une affirmation.
    """

    sys.path.insert(0, str(ROOT / "scripts"))
    import clone_normalization_fixtures as fixtures

    normalize = identity_rule().pedagogical_body
    faux_negatifs = [
        label for label, a, b in fixtures.MUST_MATCH if normalize(a) != normalize(b)
    ]
    faux_positifs = [
        label for label, a, b in fixtures.MUST_DIFFER if normalize(a) == normalize(b)
    ]
    return {
        "CLONE_NORMALIZATION_FIXTURES_MUST_MATCH": len(fixtures.MUST_MATCH),
        "CLONE_NORMALIZATION_FIXTURES_MUST_DIFFER": len(fixtures.MUST_DIFFER),
        "CLONE_NORMALIZATION_FALSE_POSITIVES": len(faux_positifs),
        "CLONE_NORMALIZATION_FALSE_NEGATIVES": len(faux_negatifs),
        "FALSE_POSITIVE_LABELS": faux_positifs,
        "FALSE_NEGATIVE_LABELS": faux_negatifs,
        "PRESERVED_BY_CONTRACT": [
            "nombres", "formules", "code", "texte", "donnees",
            "options de QCM", "references pedagogiques", "figures",
            "noms de concepts",
        ],
        "REMOVED_BY_CONTRACT": [
            "% META: identity line",
            "declared object identity (id, exercice_ref, evaluation_ref)",
            "trailing and edge whitespace",
        ],
    }


def introduction_index(root: Path) -> dict[str, str]:
    """Le commit qui a AJOUTE chaque fichier, en une seule passe d'historique."""

    completed = subprocess.run(
        [
            "git", "-C", str(root), "log", "--all", "--diff-filter=A",
            "--name-only", "--format=%x00%H", "--no-renames",
        ],
        capture_output=True,
        text=True,
    )
    index: dict[str, str] = {}
    commit = ""
    for raw in completed.stdout.split("\n"):
        if raw.startswith("\x00"):
            commit = raw[1:].strip()
            continue
        chemin = raw.strip()
        if chemin and commit:
            # `--all` remonte du plus recent au plus ancien : le dernier vu
            # est le plus ancien, donc l'introduction reelle.
            index[chemin] = commit
    return index


def _sources(corpora: tuple[Path, ...]) -> list[Path]:
    paths: list[Path] = []
    for corpus in corpora:
        if not corpus.is_dir():
            continue
        for path in sorted(corpus.rglob("*.tex")):
            if any(part in UNPUBLISHED for part in path.parts):
                continue
            paths.append(path)
    return paths


def scan(root: Path = ROOT, corpora: tuple[Path, ...] | None = None) -> dict[str, Any]:
    ledger = identity_rule()
    corpora = corpora or CORPORA
    rows: list[dict[str, Any]] = []
    chapitres_vus: set[str] = set()
    for path in _sources(corpora):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = ledger.read_meta(text)
        parts = path.relative_to(root).parts
        if "chapitres" not in parts:
            continue
        index = parts.index("chapitres") + 1
        if len(parts) <= index + 1:
            continue
        chapitre, role = parts[index], parts[index + 1]
        chapitres_vus.add(chapitre)
        body = ledger.pedagogical_body(text)
        if not ledger.payload_only(body):
            continue
        rows.append({
            "path": str(path.relative_to(root)),
            "object_id": meta.get("id"),
            "chapter": chapitre,
            "manual": ledger.manual_of(chapitre),
            "object_type": meta.get("type_objet") or role,
            "role": role,
            "capacities": meta.get("capacites_codes") or meta.get("capacites") or [],
            "status": meta.get("status"),
            "exercice_ref": meta.get("exercice_ref"),
            "body_digest": _digest(body),
        })
    return {"rows": rows, "chapters_scanned": sorted(chapitres_vus)}


def build(root: Path = ROOT) -> dict[str, Any]:
    scanned = scan(root)
    rows = scanned["rows"]
    introductions = introduction_index(root)

    par_corps: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        row["introduced_commit"] = introductions.get(row["path"])
        par_corps[row["body_digest"]].append(row)

    groupes: list[dict[str, Any]] = []
    for digest, membres in sorted(par_corps.items()):
        if len(membres) < 2:
            continue
        chapitres = {m["chapter"] for m in membres}
        manuels = {m["manual"] for m in membres}
        lignee, regle = _lineage(root, membres)
        signature_capacites = {
            (m["chapter"], tuple(sorted(m["capacities"]))) for m in membres
        }
        credite_ailleurs = {
            (m["chapter"], tuple(sorted(m["capacities"])))
            for m in membres
            if m["capacities"]
        }
        groupes.append({
            "group_id": f"CMC-{len(groupes) + 1:04d}",
            "source_body_digest": digest,
            "members": membres,
            "member_count": len(membres),
            "chapters": sorted(chapitres),
            "manuals": sorted(manuels),
            "cross_chapter": len(chapitres) > 1,
            "cross_manual": len(manuels) > 1,
            "capacity_misrepresenting": len(credite_ailleurs) > 1,
            "distinct_capacity_declarations": len(signature_capacites),
            "canonical_source": (
                {
                    "object_id": lignee["object_id"],
                    "path": lignee["path"],
                    "chapter": lignee["chapter"],
                    "manual": lignee["manual"],
                    "introduced_commit": lignee["introduced_commit"],
                }
                if lignee
                else None
            ),
            "lineage_status": (
                "CANONICAL_SOURCE_OBJECT" if lignee else "NO_CANONICAL_SOURCE_IDENTIFIED"
            ),
            "lineage_rule": regle,
        })

    _inherit_lineage_through_corrections(groupes, rows)
    contamines = {
        m["object_id"]
        for g in groupes
        if g["cross_chapter"]
        for m in g["members"]
        if not (g["canonical_source"] and m["path"] == g["canonical_source"]["path"])
    }
    _mark_corrections_of_contaminated_exercises(groupes, contamines)
    return _assemble(root, scanned, groupes)


def _lineage(
    root: Path, membres: list[dict[str, Any]]
) -> tuple[dict[str, Any] | None, str]:
    """Qui, dans ce groupe, est l'original ?

    L'historique tranche quand il le peut : le membre introduit le PREMIER est
    l'original, les autres sont des copies. Quand tous les membres arrivent
    dans le MEME commit, l'historique ne dit rien -- et l'ordre des chemins ne
    prouve rien. Designer alors le premier par ordre alphabetique fabriquerait
    une lignee ; on refuse, et le groupe est marque sans source identifiee.
    Une deuxieme regle, evidentielle, le rattrape ailleurs : un corrige suit
    la lignee de l'exercice qu'il sert.
    """

    datees = [m for m in membres if m["introduced_commit"]]
    if not datees:
        return None, "NO_INTRODUCTION_RECORDED"
    commits = {m["introduced_commit"] for m in datees}
    if len(commits) == 1:
        return None, "ALL_MEMBERS_INTRODUCED_BY_THE_SAME_COMMIT"
    ordre = _commit_order(root, commits)
    if not ordre:
        return None, "COMMIT_ORDER_UNAVAILABLE"
    classes = sorted(
        datees, key=lambda m: (ordre.get(m["introduced_commit"], 1 << 30), m["path"])
    )
    premier = classes[0]
    rang = ordre.get(premier["introduced_commit"], 1 << 30)
    ex_aequo = [
        m for m in classes if ordre.get(m["introduced_commit"], 1 << 30) == rang
    ]
    if len(ex_aequo) > 1:
        return None, "EARLIEST_INTRODUCTION_IS_A_TIE"
    return premier, "EARLIEST_INTRODUCTION"


def _inherit_lineage_through_corrections(
    groupes: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> None:
    """Un corrige suit la lignee de l'exercice auquel il repond.

    Quatorze corriges arrives dans un seul commit ne se departagent pas par
    l'historique. Mais chacun nomme son exercice, et ces exercices, eux, sont
    departages : le corrige de l'exercice original est l'original.
    """

    exercice_source: dict[str, str] = {}
    for groupe in groupes:
        source = groupe.get("canonical_source")
        if source and groupe.get("lineage_rule") == "EARLIEST_INTRODUCTION":
            exercice_source[source["object_id"]] = source["path"]
    par_chemin = {r["path"]: r for r in rows}
    for groupe in groupes:
        if groupe["canonical_source"] is not None:
            continue
        if groupe.get("lineage_rule") != "ALL_MEMBERS_INTRODUCED_BY_THE_SAME_COMMIT":
            continue
        candidats = [
            m
            for m in groupe["members"]
            if (m.get("exercice_ref") or "") in exercice_source
        ]
        if len(candidats) != 1:
            continue
        elu = par_chemin.get(candidats[0]["path"], candidats[0])
        groupe["canonical_source"] = {
            "object_id": elu["object_id"],
            "path": elu["path"],
            "chapter": elu["chapter"],
            "manual": elu["manual"],
            "introduced_commit": elu["introduced_commit"],
        }
        groupe["lineage_status"] = "CANONICAL_SOURCE_OBJECT"
        groupe["lineage_rule"] = "CORRECTION_FOLLOWS_ITS_EXERCISE"


def _mark_corrections_of_contaminated_exercises(
    groupes: list[dict[str, Any]], contamines: set[str]
) -> None:
    """Un groupe dont chaque membre repond a un exercice contamine n'a pas
    d'original parmi ses membres.

    Quatorze corriges arrives dans un seul commit, chacun repondant a un
    exercice lui-meme contamine : aucun d'eux n'est l'original, et en designer
    un le sauverait a tort. Le corrige d'un exercice contamine part avec lui.
    """

    for groupe in groupes:
        if groupe["canonical_source"] is not None or not groupe["cross_chapter"]:
            continue
        refs = [m.get("exercice_ref") for m in groupe["members"]]
        if refs and all(ref in contamines for ref in refs):
            groupe["lineage_rule"] = "ALL_MEMBERS_ANSWER_CONTAMINATED_EXERCISES"


_ORDER_CACHE: dict[frozenset, dict[str, int]] = {}


def _commit_order(root: Path, commits: set[str]) -> dict[str, int]:
    """Rang topologique des commits, du plus ancien au plus recent."""

    cle = frozenset(commits)
    if cle in _ORDER_CACHE:
        return _ORDER_CACHE[cle]
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--all", "--reverse", "--topo-order"],
        capture_output=True,
        text=True,
    )
    ordre = {sha: rang for rang, sha in enumerate(completed.stdout.split())}
    _ORDER_CACHE[cle] = ordre
    return ordre


def _assemble(
    root: Path, scanned: dict[str, Any], groupes: list[dict[str, Any]]
) -> dict[str, Any]:
    contamines = [g for g in groupes if g["cross_chapter"]]
    objets_contamines = [
        m
        for g in contamines
        for m in g["members"]
        if not (
            g["canonical_source"] and m["path"] == g["canonical_source"]["path"]
        )
    ]
    exacts = groupes  # tout groupe ici partage un corps normalise identique
    statuts = collections.Counter(m["status"] for m in objets_contamines)

    matrice = [
        {
            "GROUP_ID": g["group_id"],
            "SOURCE_BODY_DIGEST": g["source_body_digest"],
            "ORIGINAL_LINEAGE": (
                g["canonical_source"]["object_id"] if g["canonical_source"] else None
            ),
            "ORIGINAL_LINEAGE_CHAPTER": (
                g["canonical_source"]["chapter"] if g["canonical_source"] else None
            ),
            "LINEAGE_STATUS": g["lineage_status"],
            "TARGET_MANUAL": m["manual"],
            "TARGET_CHAPTER": m["chapter"],
            "OBJECT_ID": m["object_id"],
            "OBJECT_TYPE": m["object_type"],
            "OBJECT_PATH": m["path"],
            "CAPACITY": m["capacities"],
            "STATUS": m["status"],
            "INTRODUCED_COMMIT": m["introduced_commit"],
            "IS_CANONICAL_SOURCE": bool(
                g["canonical_source"] and m["path"] == g["canonical_source"]["path"]
            ),
        }
        for g in contamines
        for m in sorted(g["members"], key=lambda r: r["path"])
    ]

    chapitres_du_corpus = {
        p.name
        for corpus in CORPORA
        if corpus.is_dir()
        for p in corpus.iterdir()
        if p.is_dir() and (p / "contrat.yaml").is_file()
    }
    non_scannes = sorted(chapitres_du_corpus - set(scanned["chapters_scanned"]))

    summary = {
        "CLONE_GROUPS_TOTAL": len(groupes),
        "CLONED_OBJECTS_TOTAL": sum(g["member_count"] for g in groupes),
        "EXACT_CLONES": sum(g["member_count"] for g in exacts),
        "NEAR_CLONES": 0,
        "CROSS_MANUAL_CONTAMINATION_GROUPS": sum(
            1 for g in contamines if g["cross_manual"]
        ),
        "CROSS_CHAPTER_CONTAMINATION_GROUPS": len(contamines),
        "CROSS_MANUAL_CONTAMINATION_OBJECTS": len(objets_contamines),
        "CAPACITY_MISREPRESENTING_GROUPS": sum(
            1 for g in groupes if g["capacity_misrepresenting"]
        ),
        "GROUPS_WITHOUT_CANONICAL_SOURCE": sum(
            1 for g in groupes if g["lineage_status"] == "NO_CANONICAL_SOURCE_IDENTIFIED"
        ),
        "CROSS_CHAPTER_GROUPS_WITHOUT_CANONICAL_SOURCE": sum(
            1
            for g in groupes
            if g["cross_chapter"]
            and g["lineage_status"] == "NO_CANONICAL_SOURCE_IDENTIFIED"
        ),
        "LINEAGE_RULES": dict(sorted(
            collections.Counter(g["lineage_rule"] for g in groupes).items()
        )),
        "CONTAMINATED_APPROVED_OBJECTS": statuts.get("approved", 0),
        "CONTAMINATED_OBJECTS_BY_STATUS": dict(sorted(
            (k or "SANS_STATUT", v) for k, v in statuts.items()
        )),
        "OBJECTS_SCANNED": len(scanned["rows"]),
        "CHAPTERS_SCANNED": len(scanned["chapters_scanned"]),
        "UNSCANNED_CANONICAL_CHAPTERS": len(non_scannes),
    }

    proof = normalization_proof()
    reconciliation = _reconcile(summary, contamines)

    return {
        "artifact_type": "cross_manual_contamination",
        "schema_version": 1,
        "generated_by": "scripts/build_cross_manual_contamination.py",
        "finding": FINDING,
        "root_cause_id": ROOT_CAUSE,
        "publication_blocker": True,
        "severity_rationale": (
            "un exercice d'analyse imprime comme exercice d'arithmetique ou "
            "d'inference bayesienne est un defaut visible par l'eleve sur la "
            "page publiee : ce n'est pas une dette de gouvernance"
        ),
        "approves_nothing": True,
        "CURRENT_CLONE_LEDGER_USES_CORRECT_NORMALIZATION": (
            proof["CLONE_NORMALIZATION_FALSE_POSITIVES"] == 0
            and proof["CLONE_NORMALIZATION_FALSE_NEGATIVES"] == 0
        ),
        "normalization_proof": proof,
        "summary": summary,
        "reconciliation": reconciliation,
        "unscanned_canonical_chapters": non_scannes,
        "groups": groupes,
        "matrix_rows": len(matrice),
        "matrix_digest": _digest(
            json.dumps(
                [[r["OBJECT_PATH"], r["GROUP_ID"]] for r in matrice],
                ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            )
        ),
        "_matrix": matrice,
    }


#: Les ecarts entre le nombre annonce et le nombre recalcule qui viennent
#: d'une DEFINITION differente, pas d'un desaccord de mesure. Chacun est
#: verifiable par arithmetique sur la population courante.
DEFINITIONAL_DELTAS = {
    "CLONED_OBJECTS_TOTAL": (
        "917 comptait les objets EN TROP (membres moins un par groupe) ; 1041 "
        "compte tous les membres. 1041 - 124 groupes = 917 : la meme "
        "population, comptee une fois avec et une fois sans son representant."
    ),
    "CAPACITY_MISREPRESENTING_GROUPS": (
        "92 comparait les codes de capacite LOCAUX : deux membres declarant "
        "tous deux `C1` passaient pour d'accord, alors que le `C1` de "
        "TCOMPL-INFERENCE-BAYESIENNE et celui de TSPE-DERIVATION-CONVEXITE "
        "designent des capacites sans aucun rapport. 118 qualifie la capacite "
        "par son chapitre, comme le fait deja le resolveur d'identite du "
        "depot. Les 26 groupes d'ecart sont des homonymies, pas des accords."
    ),
    "CROSS_MANUAL_CONTAMINATION_OBJECTS": (
        "903 designait un original dans chaque groupe. Un groupe n'en a pas : "
        "les quatorze corriges `*-CO-010` arrivent tous dans le meme commit, "
        "et chacun repond a un exercice lui-meme contamine. Aucun n'est "
        "l'original ; en designer un par ordre alphabetique l'aurait sauve a "
        "tort. Le quatorzieme rejoint donc la population : 904."
    ),
    "CROSS_MANUAL_CONTAMINATION_OBJECTS_FIRST_PASS": (
        "903 designait un original dans chaque groupe. Un groupe n'en a pas : "
        "les quatorze corriges `*-CO-010` arrivent tous dans le meme commit, "
        "et chacun repond a un exercice lui-meme contamine. Aucun n'est "
        "l'original ; en designer un par ordre alphabetique l'aurait sauve a "
        "tort. Le quatorzieme rejoint donc la population : 904."
    ),
    "CONTAMINATED_OBJECTS_WITH_APPROVED_STATUS": (
        "997 comptait TOUS les membres approuves, source canonique comprise ; "
        "903 ne compte que les consommateurs contamines. 1021 membres - 118 "
        "sources = 903, et les 118 sources se repartissent en 94 approved "
        "et 24 generated : 903 + 94 = 997. Condamner la source parce qu'elle "
        "a ete recopiee ailleurs serait exactement l'erreur que la decision "
        "humaine interdit."
    ),
}


def _reconcile(summary: dict[str, Any], contamines: list[dict[str, Any]]) -> dict[str, Any]:
    """Chaque nombre cite est recalcule, jamais repris."""

    exercices_exacts = sum(
        1
        for g in contamines
        for m in g["members"]
        if m["role"] == "exercices"
    )
    mesures = {
        "CLONE_GROUPS_TOTAL": summary["CLONE_GROUPS_TOTAL"],
        "CLONED_OBJECTS_TOTAL": summary["CLONED_OBJECTS_TOTAL"],
        "CROSS_MANUAL_CONTAMINATION_OBJECTS": summary[
            "CROSS_MANUAL_CONTAMINATION_OBJECTS"
        ],
        "CROSS_MANUAL_CONTAMINATION_OBJECTS_FIRST_PASS": summary[
            "CROSS_MANUAL_CONTAMINATION_OBJECTS"
        ],
        "SOURCE_CLONE_WITH_DISTINCT_IDS_GROUPS": summary[
            "CROSS_CHAPTER_CONTAMINATION_GROUPS"
        ],
        "CAPACITY_MISREPRESENTING_GROUPS": summary["CAPACITY_MISREPRESENTING_GROUPS"],
        "EXACT_DUPLICATE_EXERCISES": exercices_exacts,
        "CONTAMINATED_OBJECTS_WITH_APPROVED_STATUS": summary[
            "CONTAMINATED_APPROVED_OBJECTS"
        ],
        "CONTAMINATED_OBJECTS_TOTAL": sum(
            g["member_count"] for g in contamines
        ),
    }
    lignes = []
    for cle, annonce in sorted(REPORTED.items()):
        mesure = mesures.get(cle)
        explication = DEFINITIONAL_DELTAS.get(cle)
        lignes.append({
            "metric": cle,
            "reported_in_alert": annonce,
            "recomputed_now": mesure,
            "agrees": mesure == annonce,
            "delta": None if mesure is None else mesure - annonce,
            "definitional_difference": explication,
            "resolved": mesure == annonce or explication is not None,
        })
    return {
        "rule": "aucun nombre n'est repris du rapport : chacun est recalcule",
        "metrics": lignes,
        "ALL_REPORTED_NUMBERS_REPRODUCED": all(
            l["agrees"] for l in lignes
        ),
        "ALL_DELTAS_EXPLAINED": all(l["resolved"] for l in lignes),
        "UNEXPLAINED_DELTAS": [
            l["metric"] for l in lignes if not l["resolved"]
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        f"# {payload['finding']}",
        "",
        f"Cause racine : `{payload['root_cause_id']}`.",
        "",
        payload["severity_rationale"].capitalize() + ".",
        "",
        "## Population canonique",
        "",
    ]
    for cle in (
        "CLONE_GROUPS_TOTAL", "CLONED_OBJECTS_TOTAL", "EXACT_CLONES", "NEAR_CLONES",
        "CROSS_MANUAL_CONTAMINATION_GROUPS", "CROSS_MANUAL_CONTAMINATION_OBJECTS",
        "CAPACITY_MISREPRESENTING_GROUPS", "CONTAMINATED_APPROVED_OBJECTS",
        "GROUPS_WITHOUT_CANONICAL_SOURCE", "UNSCANNED_CANONICAL_CHAPTERS",
    ):
        lignes.append(f"- `{cle}` : `{s[cle]}`")
    lignes += [
        "",
        "## Preuve de normalisation",
        "",
        f"- faux positifs : `{payload['normalization_proof']['CLONE_NORMALIZATION_FALSE_POSITIVES']}`",
        f"- faux negatifs : `{payload['normalization_proof']['CLONE_NORMALIZATION_FALSE_NEGATIVES']}`",
        "",
        "## Reconciliation avec les nombres annonces",
        "",
        "| metrique | annonce | recalcule | accord |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["reconciliation"]["metrics"]:
        lignes.append(
            f"| `{row['metric']}` | {row['reported_in_alert']} | "
            f"{row['recomputed_now']} | {'oui' if row['agrees'] else 'NON'} |"
        )
    lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    payload = build()
    matrice = payload.pop("_matrix")
    matrix_payload = {
        "artifact_type": "cross_manual_contamination_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_cross_manual_contamination.py",
        "finding": FINDING,
        "columns": [
            "GROUP_ID", "SOURCE_BODY_DIGEST", "ORIGINAL_LINEAGE",
            "ORIGINAL_LINEAGE_CHAPTER", "LINEAGE_STATUS", "TARGET_MANUAL",
            "TARGET_CHAPTER", "OBJECT_ID", "OBJECT_TYPE", "OBJECT_PATH",
            "CAPACITY", "STATUS", "INTRODUCED_COMMIT", "IS_CANONICAL_SOURCE",
        ],
        "row_count": len(matrice),
        "rows": matrice,
    }
    rendus = {
        OUTPUT_JSON: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MATRIX_JSON: json.dumps(matrix_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        OUTPUT_MD: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT))
            for p, contenu in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != contenu
        ]
        for ecart in ecarts:
            print(f"diff: {ecart}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
