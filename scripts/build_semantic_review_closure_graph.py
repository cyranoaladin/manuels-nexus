#!/usr/bin/env python3
"""Graphe de cloture semantique de la dette de revue.

QUESTION POSEE. Avant de faire relire 2 537 lignes une par une, sait-on
combien de contenus semantiques DISTINCTS elles representent ? Une meme fiche
rendue dans quatre livrets ne doit pas etre relue quatre fois ; deux exercices
qui ne different que par un coefficient ne demandent pas deux lectures
completes.

CE QUE LA MESURE REPOND. Presque rien n'est duplique. Sur 2 537 items, les
corps canoniques distincts sont 2 523 : 14 items seulement sont des copies
exactes, et 13 de plus ne different d'un frere que par un nombre. La
reduction possible est de 14 items, soit 0,55 %. Le corpus est editorialement
singulier : ce n'est pas une base de gabarits recopies. Les 14 copies exactes
sont toutes des coups de pouce partages entre exercices voisins.

Ce resultat est negatif et il est publie tel quel. L'hypothese qui justifiait
ce graphe — une dette gonflee par la duplication — est refutee par le compte.

CE QUE LE GRAPHE ETABLIT QUAND MEME, ET QUI COMPTE.

1. La file n'est pas indexee par rendu. 1 642 des 2 537 items sont inclus
   dans plusieurs assemblages — jusqu'a seize pour un seul objet — et
   n'occupent malgre tout qu'une ligne chacun. `RENDERED_CONSUMERS` le montre
   objet par objet : la multiplication par les variantes n'a jamais eu lieu,
   et il n'y a donc rien a en deduire.

2. L'heritage de preuve est DIMENSIONNE. Deux coups de pouce identiques au
   bit pres sont attaches a deux exercices differents. Relire l'un etablit la
   correction scientifique et la formulation du texte ; cela n'etablit pas
   qu'il convient a l'autre exercice. L'heritage porte donc sur
   CONTENU_SCIENTIFIQUE et FORMULATION, jamais sur ADEQUATION_A_L_OBJET_PARENT.
   Presenter 2 510 comme le nombre de revues necessaires serait faux : les
   2 537 verifications d'adequation restent dues.

3. Chaque arete d'heritage porte l'egalite d'empreinte qui la justifie.
   `UNJUSTIFIED_REVIEW_EVIDENCE_INHERITANCE` compte les items qui heriteraient
   sans cette preuve. Il vaut 0 par construction, et le test le verifie en
   tentant d'en fabriquer un.

DERIVATIONS RECONNUES, TOUTES EXACTES.

`CANONICAL`      l'item EST la source canonique de son groupe.
`EXACT_COPY`     corps canonique identique au bit pres a celui de la source.
`NUMERIC_DELTA`  meme squelette une fois les nombres abstraits, corps
                 differents. La lecture porte alors sur le delta, pas sur le
                 tout — mais aucune preuve n'est heritee.

Hors de ces trois cas, l'item est sa propre source. Aucune similarite
approximative, aucun seuil de distance : deux textes sont identiques ou ils ne
le sont pas.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402

QUEUE = Path("audit/HUMAN_REVIEW_QUEUE.json")
PARTITION = Path("audit/CURRENT_REVIEW_DEBT_PARTITION.json")
INVENTORY = Path("audit/INVENTAIRE_COLLECTION.json")
OUTPUT_JSON = ROOT / "audit/SEMANTIC_REVIEW_CLOSURE_GRAPH.json"
OUTPUT_MD = ROOT / "audit/SEMANTIC_REVIEW_CLOSURE_GRAPH.md"

INHERITABLE = ("CONTENU_SCIENTIFIQUE", "FORMULATION")
NON_INHERITABLE = ("ADEQUATION_A_L_OBJET_PARENT", "PLACEMENT_CURRICULAIRE")

NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")


def _digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_body(path: Path) -> str:
    """Le corps de l'objet, sans sa ligne META et sans variation d'espaces.

    La ligne META porte l'identite (id, chapitre, capacites) : deux objets qui
    ne different que par elle sont deux objets differents portant le meme
    texte. C'est exactement la situation qu'on veut voir, donc on la retire du
    corps au lieu de la laisser masquer l'egalite.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    if lines and lines[0].lstrip().startswith("% META:"):
        lines = lines[1:]
    return " ".join("\n".join(lines).split())


def numeric_skeleton(body: str) -> str:
    return NUMBER.sub("#", body)


def _object_rows(root: Path) -> dict[str, dict[str, Any]]:
    partition = json.loads((root / PARTITION).read_text(encoding="utf-8"))
    rows: dict[str, dict[str, Any]] = {}
    for component, payload in sorted(partition["components"].items()):
        for row in payload.get("objects", []):
            row = dict(row)
            row["component"] = component
            rows[str(row["fingerprint"])] = row
    return rows


def _rendered_consumers(root: Path) -> dict[str, list[str]]:
    """Les assemblages qui incluent chaque fichier source."""
    inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    consumers: dict[str, list[str]] = collections.defaultdict(list)
    for assembly in inventory.get("assemblies", []):
        assembly_id = str(assembly.get("assembly_id"))
        for included in assembly.get("included_files", []):
            consumers[str(included)].append(assembly_id)
    return {path: sorted(set(ids)) for path, ids in consumers.items()}


def _qcm_questions(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    questions: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(root.glob("*/**/chapitres/*/qcm/*-QCM.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        chapter = str(payload.get("chapitre") or path.parent.parent.name)
        for question in payload.get("questions", []):
            questions[(chapter, str(question.get("id")))] = {
                "question": question,
                "path": path.relative_to(root).as_posix(),
            }
    return questions


def _qcm_canonical(question: dict[str, Any], category: str) -> str:
    if category == "QCM_ANSWER_SEMANTICS":
        payload = {
            "enonce": question.get("enonce"),
            "options": question.get("options"),
            "correcte": question.get("correcte"),
        }
    else:
        payload = {"diagnostics": question.get("diagnostics")}
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def collect_units(root: Path = ROOT) -> list[dict[str, Any]]:
    """Un enregistrement par item de la file, avec sa source semantique."""
    queue = json.loads((root / QUEUE).read_text(encoding="utf-8"))
    objects = _object_rows(root)
    consumers = _rendered_consumers(root)
    qcm = _qcm_questions(root)

    units: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in queue["items"]:
        category = str(item["category"])
        for unit_id in item["unit_ids"]:
            if unit_id in seen:
                raise ValueError(f"unite de revue en double dans la file: {unit_id}")
            seen.add(unit_id)
            if category == "OBJECT_REVIEW":
                fingerprint = unit_id.split("::", 1)[1]
                row = objects.get(fingerprint)
                if row is None:
                    raise ValueError(f"unite sans objet dans la partition: {unit_id}")
                path = root / str(row["path"])
                if not path.is_file():
                    raise ValueError(f"objet absent du disque: {row['path']}")
                body = canonical_body(path)
                units.append({
                    "REVIEW_ITEM_ID": unit_id,
                    "category": category,
                    "queue_item": item["item_id"],
                    "object_id": row.get("object_id"),
                    "path": row["path"],
                    "chapter": row.get("chapter"),
                    "canonical_body_digest": _digest(body),
                    "numeric_skeleton_digest": _digest(numeric_skeleton(body)),
                    "RENDERED_CONSUMERS": consumers.get(str(row["path"]), []),
                })
            else:
                chapter, question_id = unit_id.split("::", 1)[1].rsplit("/", 1)
                found = qcm.get((chapter, question_id))
                if found is None:
                    raise ValueError(f"question QCM introuvable: {unit_id}")
                body = _qcm_canonical(found["question"], category)
                units.append({
                    "REVIEW_ITEM_ID": unit_id,
                    "category": category,
                    "queue_item": item["item_id"],
                    "object_id": f"{chapter}/{question_id}",
                    "path": found["path"],
                    "chapter": chapter,
                    "canonical_body_digest": _digest(body),
                    "numeric_skeleton_digest": _digest(numeric_skeleton(body)),
                    "RENDERED_CONSUMERS": consumers.get(found["path"], []),
                })
    return units


def close(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attache a chaque item sa source canonique et sa derivation.

    La source d'un groupe est son item de plus petit identifiant : un choix
    arbitraire mais deterministe, pour que deux executions donnent le meme
    graphe.
    """
    by_body: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for unit in units:
        by_body[unit["canonical_body_digest"]].append(unit)
    sources = {
        digest: min(group, key=lambda u: u["REVIEW_ITEM_ID"])["REVIEW_ITEM_ID"]
        for digest, group in by_body.items()
    }

    by_skeleton: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for unit in units:
        by_skeleton[unit["numeric_skeleton_digest"]].append(unit)
    skeleton_sources = {
        digest: min(group, key=lambda u: u["REVIEW_ITEM_ID"])["REVIEW_ITEM_ID"]
        for digest, group in by_skeleton.items()
    }

    closed = []
    for unit in units:
        row = dict(unit)
        body_source = sources[unit["canonical_body_digest"]]
        if body_source == unit["REVIEW_ITEM_ID"]:
            skeleton_group = by_skeleton[unit["numeric_skeleton_digest"]]
            skeleton_source = skeleton_sources[unit["numeric_skeleton_digest"]]
            if len(skeleton_group) > 1 and skeleton_source != unit["REVIEW_ITEM_ID"]:
                row["DERIVATION"] = "NUMERIC_DELTA"
                row["CANONICAL_SEMANTIC_SOURCE"] = skeleton_source
                row["DERIVATION_PROOF"] = {
                    "numeric_skeleton_digest": unit["numeric_skeleton_digest"],
                    "bodies_are_equal": False,
                }
                # Un delta numerique NE transmet aucune preuve : deux enonces
                # qui different par un coefficient peuvent differer par leur
                # validite. Il signale seulement ou lire vite.
                row["INHERITS_REVIEW_EVIDENCE_FOR"] = []
            else:
                row["DERIVATION"] = "CANONICAL"
                row["CANONICAL_SEMANTIC_SOURCE"] = unit["REVIEW_ITEM_ID"]
                row["DERIVATION_PROOF"] = {
                    "canonical_body_digest": unit["canonical_body_digest"],
                    "is_source": True,
                }
                row["INHERITS_REVIEW_EVIDENCE_FOR"] = []
        else:
            row["DERIVATION"] = "EXACT_COPY"
            row["CANONICAL_SEMANTIC_SOURCE"] = body_source
            row["DERIVATION_PROOF"] = {
                "canonical_body_digest": unit["canonical_body_digest"],
                "bodies_are_equal": True,
            }
            row["INHERITS_REVIEW_EVIDENCE_FOR"] = list(INHERITABLE)
        row["REQUIRES_OWN_REVIEW_FOR"] = [
            dimension
            for dimension in (*INHERITABLE, *NON_INHERITABLE)
            if dimension not in row["INHERITS_REVIEW_EVIDENCE_FOR"]
        ]
        closed.append(row)
    return closed


def unjustified_inheritance(closed: list[dict[str, Any]]) -> list[str]:
    """Items qui heritent sans egalite d'empreinte demontree."""
    by_id = {row["REVIEW_ITEM_ID"]: row for row in closed}
    offenders = []
    for row in closed:
        if not row["INHERITS_REVIEW_EVIDENCE_FOR"]:
            continue
        source = by_id.get(row["CANONICAL_SEMANTIC_SOURCE"])
        proof = row.get("DERIVATION_PROOF") or {}
        if (
            source is None
            or proof.get("bodies_are_equal") is not True
            or source["canonical_body_digest"] != row["canonical_body_digest"]
        ):
            offenders.append(row["REVIEW_ITEM_ID"])
    return sorted(offenders)


def build(root: Path = ROOT) -> dict[str, Any]:
    units = collect_units(root)
    closed = close(units)

    derivations = collections.Counter(row["DERIVATION"] for row in closed)
    canonical_bodies = {row["canonical_body_digest"] for row in closed}
    offenders = unjustified_inheritance(closed)

    multi_consumer = sum(1 for row in closed if len(row["RENDERED_CONSUMERS"]) > 1)
    consumer_histogram = collections.Counter(
        len(row["RENDERED_CONSUMERS"]) for row in closed
    )
    # `RENDERED_CONSUMERS` est mesure sur les assemblages LaTeX. Les QCM sont
    # des JSON, consommes par une autre chaine : leur zero ne signifie pas
    # « contenu mort », il signifie « hors du perimetre de cette mesure ».
    # Le distinguer evite qu'on lise 212 objets orphelins la ou il n'y en a
    # que le reste apres retrait des QCM.
    unrendered = [row for row in closed if not row["RENDERED_CONSUMERS"]]
    unrendered_latex = [
        row for row in unrendered if row["category"] == "OBJECT_REVIEW"
    ]

    summary = {
        "RAW_REVIEW_ITEMS": len(closed),
        "CANONICAL_SEMANTIC_UNITS": len(canonical_bodies),
        "EXACT_DERIVED_DUPLICATES": derivations.get("EXACT_COPY", 0),
        "SEMANTIC_DELTA_VARIANTS": derivations.get("NUMERIC_DELTA", 0),
        "INDEPENDENT_CONTENT_REVIEW_UNITS": len(canonical_bodies),
        "INDEPENDENT_REVIEW_UNITS_REQUIRED": len(closed) - derivations.get("EXACT_COPY", 0),
        "PER_ITEM_ADEQUACY_CHECKS_STILL_REQUIRED": len(closed),
        "UNJUSTIFIED_REVIEW_EVIDENCE_INHERITANCE": len(offenders),
        "REVIEW_ITEMS_WITH_MULTIPLE_RENDERED_CONSUMERS": multi_consumer,
        "REVIEW_ITEMS_OUTSIDE_LATEX_ASSEMBLY_SCOPE": len(unrendered) - len(unrendered_latex),
        "LATEX_OBJECTS_IN_NO_ASSEMBLY": len(unrendered_latex),
        "MAX_RENDERED_CONSUMERS_FOR_ONE_ITEM": max(consumer_histogram or {0: 0}),
        "REDUCTION_RATIO": round(
            derivations.get("EXACT_COPY", 0) / len(closed), 4
        ) if closed else 0.0,
    }

    inputs = [path.as_posix() for path in (QUEUE, PARTITION, INVENTORY)]
    payload = {
        "artifact_type": "semantic_review_closure_graph",
        "schema_version": 1,
        "generated_by": "scripts/build_semantic_review_closure_graph.py",
        "approves_nothing": True,
        "summary": summary,
        "derivation_distribution": dict(sorted(derivations.items())),
        "rendered_consumer_histogram": dict(sorted(consumer_histogram.items())),
        "inheritance_model": {
            "INHERITABLE_DIMENSIONS": list(INHERITABLE),
            "NON_INHERITABLE_DIMENSIONS": list(NON_INHERITABLE),
            "why": (
                "Deux objets au corps identique restent attaches a deux "
                "parents differents. Relire l'un etablit la correction du "
                "texte, jamais son adequation a l'autre parent."
            ),
        },
        "unjustified_inheritance": offenders,
        "latex_objects_in_no_assembly": sorted(
            row["path"] for row in unrendered_latex
        ),
        "records": sorted(closed, key=lambda row: row["REVIEW_ITEM_ID"]),
    }
    payload["freshness"] = freshness.stamp(inputs, root=root)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Graphe de clôture sémantique de la dette de revue",
        "",
        "## Résultat",
        "",
        f"- `RAW_REVIEW_ITEMS` : **{s['RAW_REVIEW_ITEMS']}**",
        f"- `CANONICAL_SEMANTIC_UNITS` : **{s['CANONICAL_SEMANTIC_UNITS']}**",
        f"- `EXACT_DERIVED_DUPLICATES` : **{s['EXACT_DERIVED_DUPLICATES']}**",
        f"- `SEMANTIC_DELTA_VARIANTS` : **{s['SEMANTIC_DELTA_VARIANTS']}**",
        f"- `INDEPENDENT_REVIEW_UNITS_REQUIRED` : **{s['INDEPENDENT_REVIEW_UNITS_REQUIRED']}**",
        f"- `UNJUSTIFIED_REVIEW_EVIDENCE_INHERITANCE` : **{s['UNJUSTIFIED_REVIEW_EVIDENCE_INHERITANCE']}**",
        "",
        "## Ce que la mesure dit",
        "",
        "L'hypothèse qui justifiait ce graphe — une dette gonflée par la "
        "duplication éditoriale — est **refutée**. La réduction possible est de "
        f"{s['EXACT_DERIVED_DUPLICATES']} items sur {s['RAW_REVIEW_ITEMS']}, "
        f"soit {s['REDUCTION_RATIO'] * 100:.1f} %. Le corpus est éditorialement "
        "singulier : ce n'est pas une base de gabarits recopiés.",
        "",
        "La file n'est pas non plus indexée par rendu : "
        f"{s['REVIEW_ITEMS_WITH_MULTIPLE_RENDERED_CONSUMERS']} items sont "
        "rendus dans plusieurs livrets et n'occupent malgré tout qu'une ligne "
        "chacun. Il n'y a donc rien à déduire de ce côté non plus.",
        "",
        "## Héritage de preuve",
        "",
        f"Héritable : {', '.join(payload['inheritance_model']['INHERITABLE_DIMENSIONS'])}.",
        "",
        f"Non héritable : {', '.join(payload['inheritance_model']['NON_INHERITABLE_DIMENSIONS'])}.",
        "",
        payload["inheritance_model"]["why"],
        "",
        f"Les {s['PER_ITEM_ADEQUACY_CHECKS_STILL_REQUIRED']} vérifications "
        "d'adéquation restent dues, une par item. Présenter "
        f"{s['CANONICAL_SEMANTIC_UNITS']} comme le nombre de revues nécessaires "
        "serait faux.",
        "",
        "## Fraîcheur",
        "",
        f"- `EVIDENCE_HEAD` : `{payload['freshness'].get('EVIDENCE_HEAD')}`",
        f"- `INPUT_DIGEST` : `{payload['freshness'].get('INPUT_DIGEST')}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file():
            print("SEMANTIC_REVIEW_CLOSURE_GRAPH check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("SEMANTIC_REVIEW_CLOSURE_GRAPH check: STALE")
            return 1
        print("SEMANTIC_REVIEW_CLOSURE_GRAPH check: OK")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
