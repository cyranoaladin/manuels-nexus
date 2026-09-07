#!/usr/bin/env python3
"""Disposition des groupes de contenus identiques, categorie par categorie.

Un corps identique n'est pas en soi un defaut : la version eleve et la version
professeur d'un meme objet, ou un exemple sciemment repris, sont legitimes. Ce
module etablit donc pour chaque groupe ce qui l'a produit, puis lui attribue
exactement une categorie. Aucune suppression n'est deduite d'un simple hash.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/CLONE_DISPOSITION_LEDGER.json"
MD_TARGET = ROOT / "audit/CLONE_DISPOSITION_LEDGER.md"
GENERATED_BY = "scripts/build_clone_disposition_ledger.py"
REUSE_REGISTRY = ROOT / "audit/INTENTIONAL_REUSE_REGISTRY.json"

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
VARIANT_SEGMENT = re.compile(r"(^|/)(eleve|professeur|student|teacher)(/|$)")
#: Le corps pedagogique, c'est le fichier moins sa ligne d'identite.
MIN_BODY_CHARS = 80

SOURCE_ROOTS = {
    "1SPE": "Mathematiques/manuel-maths",
    "TSPE_2026_2027": "Mathematiques/manuel-maths",
    "TCOMPL": "Mathematiques/manuel-maths",
    "TEXPERTES": "Mathematiques/manuel-maths",
    "1NSI": "NSI",
    "TNSI": "NSI",
}


#: La mesure publiee avant la correction du detecteur est SUPERSEDEE. Elle
#: reste dans l'historique Git -- on n'efface pas une mesure fausse, on dit
#: pourquoi elle l'etait -- mais elle ne vaut plus comme mesure courante.
SUPERSEDED_MEASURE = {
    "SUPERSEDED_STATUS": "SUPERSEDED_BY_CORRECTED_CLONE_DETECTOR",
    "SUPERSEDED_BY": "audit/CROSS_MANUAL_CONTAMINATION.json",
    "SUPERSEDED_REASON": (
        "la normalisation employee laissait l'identite de l'objet dans le "
        "corps compare : chaque copie etait unique par construction, et la "
        "contamination inter-manuels ne pouvait structurellement pas etre vue"
    ),
    "HISTORICAL_MEASURE_BEFORE_CORRECTION": {"CLONE_GROUPS_TOTAL": 6, "TRUE_PRODUCT_CLONES_OPEN": 0, "CROSS_MANUAL_GROUPS": 0, "CAPACITY_MISREPRESENTING_GROUPS": 0, "NEAR_CLONES": 131},
    "HISTORICAL_MEASURE_PRESERVED_IN_GIT": True,
}


def _meta(path: Path) -> dict[str, Any]:
    head = path.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
    if not head.startswith("% META:"):
        return {}
    try:
        return json.loads(head[len("% META:"):].strip())
    except json.JSONDecodeError:
        return {}


_CLONE_IDENTITY = None


def _identity_rule():
    """La definition de l'identite d'un objet vit a un seul endroit.

    Deux producteurs qui comparent des corps doivent retirer la meme chose,
    sinon l'un voit un clone la ou l'autre declare deux objets distincts.
    """

    global _CLONE_IDENTITY
    if _CLONE_IDENTITY is None:
        spec = importlib.util.spec_from_file_location(
            "clone_identity_rule",
            Path(__file__).resolve().parent / "build_p0_content_clone_ledger.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _CLONE_IDENTITY = module
    return _CLONE_IDENTITY


def _body(path: Path) -> str:
    """Le corps de l'objet, ligne META et identite declaree retirees.

    Retirer la seule ligne `% META:` ne suffisait pas : le corps nomme l'objet
    une seconde fois, dans l'argument de `\\begin{exercice}{<id>}`. Chaque
    copie etait donc unique par construction, et
    `SOURCE_CLONE_WITH_DISTINCT_IDS` -- la disposition ecrite pour ce cas
    precis -- ne pouvait jamais s'appliquer : les copies exactes tombaient
    dans la classe plus faible des quasi-clones.
    """

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    body = "\n".join(line for line in lines[1:] if line.strip())
    rule = _identity_rule()
    for token in rule.identity_tokens(_meta(path)):
        body = body.replace(token, rule.IDENTITY_PLACEHOLDER)
    return body


def _normalised_body(body: str) -> str:
    """Corps insensible aux identifiants et a l'espacement, pour les quasi-clones."""

    text = re.sub(r"\\begin\{(exercice|corrige)\}\{[^}]*\}", r"\\begin{\1}{}", body)
    text = re.sub(r"[A-Z0-9]+(?:-[A-Z0-9]+){2,}", "ID", text)
    return re.sub(r"\s+", " ", text).strip()


def _resolve(base: Path, ref: str, near: Path) -> Path | None:
    for candidate in (base / ref, near / ref):
        target = candidate if candidate.suffix == ".tex" else candidate.with_suffix(".tex")
        if target.is_file():
            return target.resolve()
    return None


def assembly_occurrences(root: Path) -> dict[str, collections.Counter]:
    """Combien de fois chaque source est composee dans chaque cible."""

    inventory = json.loads(
        (root / "audit/CANONICAL_RELEASE_INVENTORY.json").read_text(encoding="utf-8")
    )
    occurrences: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for target in inventory["canonical_targets"]:
        manual = target["manual_id"]
        target_id = f"{manual}_{target['variant']}"
        base = root / SOURCE_ROOTS[manual]
        master = (root / target["master"]).resolve()
        pending, seen = [master], set()
        while pending:
            current = pending.pop()
            if current in seen or not current.is_file():
                continue
            seen.add(current)
            for ref in INPUT_RE.findall(
                current.read_text(encoding="utf-8", errors="ignore")
            ):
                resolved = _resolve(base, ref, current.parent)
                if resolved is None:
                    continue
                occurrences[
                    resolved.relative_to(root).as_posix()
                ][target_id] += 1
                pending.append(resolved)
    return occurrences


def _first_commit(root: Path, relative: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%H", "--", relative],
        cwd=root, capture_output=True, text=True,
    )
    commits = [line for line in result.stdout.split() if line]
    return commits[-1] if commits else None


def build(root: Path, *, with_history: bool = True) -> dict[str, Any]:
    occurrences = assembly_occurrences(root)
    assembled = sorted(occurrences)

    reuse_registry: dict[str, Any] = {}
    if REUSE_REGISTRY.is_file():
        payload = json.loads(REUSE_REGISTRY.read_text(encoding="utf-8"))
        reuse_registry = {e["object_id"]: e for e in payload.get("entries", [])}

    records: dict[str, dict[str, Any]] = {}
    for relative in assembled:
        path = root / relative
        if not path.is_file():
            continue
        body = _body(path)
        if len(body) < MIN_BODY_CHARS:
            continue
        meta = _meta(path)
        records[relative] = {
            "path": relative,
            "object_id": meta.get("id"),
            "chapter": meta.get("chapitre"),
            "role": meta.get("type_objet"),
            "capacities": meta.get("capacites_codes") or meta.get("capacites") or [],
            "targets": dict(occurrences[relative]),
            "digest": hashlib.sha256(body.encode()).hexdigest(),
            "normalised_digest": hashlib.sha256(
                _normalised_body(body).encode()
            ).hexdigest(),
        }

    exact: dict[str, list[str]] = collections.defaultdict(list)
    for relative, record in records.items():
        exact[record["digest"]].append(relative)

    near: dict[str, list[str]] = collections.defaultdict(list)
    for relative, record in records.items():
        near[record["normalised_digest"]].append(relative)

    groups: list[dict[str, Any]] = []
    for digest, members in sorted(exact.items()):
        if len(members) < 2:
            continue
        entries = [records[m] for m in sorted(members)]
        chapters = {e["chapter"] for e in entries}
        manuals = {
            t.rsplit("_", 1)[0]
            for e in entries for t in e["targets"]
        }
        ids = [e["object_id"] for e in entries]
        capacities = {tuple(sorted(map(str, e["capacities"]))) for e in entries}

        # Une source composee plusieurs fois dans une meme cible releve de
        # l'assemblage, pas du contenu.
        assembly_dupes = [
            {"path": e["path"], "targets": {k: v for k, v in e["targets"].items() if v > 1}}
            for e in entries
            if any(v > 1 for v in e["targets"].values())
        ]

        # Deux fichiers dont les chemins ne different que par un segment de
        # variante sont les deux faces d'un meme objet, pas deux objets.
        stripped = {VARIANT_SEGMENT.sub(r"\1\3", e["path"]) for e in entries}
        mirror = len(stripped) == 1 and len(entries) > 1

        # Une declaration de reutilisation n'est honoree que si elle se verifie :
        # anteriorite au remplissage synthetique, et consommateur propre et
        # existant. Sinon elle ne vaut rien et le groupe reste un clone.
        declared = []
        rejected_declarations = []
        for entry in entries:
            declaration = reuse_registry.get(entry["object_id"])
            if declaration is None:
                continue
            evidence = declaration.get("evidence", {})
            consumer = declaration.get("consumer")
            consumer_exists = bool(consumer) and any(
                (root / entry["path"]).parent.parent.rglob(f"{consumer}.tex")
            )
            if (
                evidence.get("predates_filler_commit")
                and evidence.get("distinct_consumer")
                and consumer_exists
            ):
                declared.append(entry)
            else:
                rejected_declarations.append({
                    "object_id": entry["object_id"],
                    "why": "declaration de reutilisation non verifiee",
                })

        if mirror:
            disposition = "EXPECTED_STUDENT_TEACHER_MIRROR"
            why = "meme objet compose en version eleve et en version professeur"
        elif assembly_dupes:
            disposition = "ASSEMBLY_DUPLICATION"
            why = "une source unique incluse plusieurs fois par le graphe d'assemblage"
        elif declared and len(declared) == len(entries) - 1:
            disposition = "INTENTIONAL_REUSE"
            why = (
                "reutilisation declaree, et verifiee : chaque membre precede le "
                "remplissage et sert son propre consommateur"
            )
        elif len(set(ids)) > 1:
            disposition = "SOURCE_CLONE_WITH_DISTINCT_IDS"
            why = "corps identiques presentes comme des objets distincts"
        else:
            disposition = "ACCIDENTAL_RENDER_DUPLICATION"
            why = "meme identifiant compose plusieurs fois sans intention declaree"

        groups.append({
            "digest": digest,
            "disposition": disposition,
            "why": why,
            "members": entries,
            "object_ids": ids,
            "chapters": sorted(c for c in chapters if c),
            "manuals": sorted(manuals),
            "cross_chapter": len(chapters) > 1,
            "cross_manual": len(manuals) > 1,
            "distinct_capacity_sets": len(capacities),
            "capacity_misrepresenting": len(capacities) > 1,
            "excess_objects": len(entries) - 1,
            "assembly_duplicates": assembly_dupes,
            "rejected_reuse_declarations": rejected_declarations,
            "first_commits": (
                {e["path"]: _first_commit(root, e["path"]) for e in entries}
                if with_history else {}
            ),
        })

    exact_members = {m for members in exact.values() if len(members) > 1 for m in members}
    near_groups = []
    for digest, members in sorted(near.items()):
        if len(members) < 2:
            continue
        if all(records[m]["digest"] == records[members[0]]["digest"] for m in members):
            continue  # deja couvert par un groupe exact
        near_groups.append({
            "normalised_digest": digest,
            "disposition": "NEAR_CLONE",
            "why": "corps proches apres normalisation, non identiques",
            "members": [records[m]["path"] for m in sorted(members)],
            "object_ids": [records[m]["object_id"] for m in sorted(members)],
            "excess_objects": len(members) - 1,
        })

    by_disposition = collections.Counter(g["disposition"] for g in groups)
    excess_by_disposition = collections.Counter()
    for group in groups:
        excess_by_disposition[group["disposition"]] += group["excess_objects"]

    true_product_clones = (
        excess_by_disposition["SOURCE_CLONE_WITH_DISTINCT_IDS"]
        + excess_by_disposition["ACCIDENTAL_RENDER_DUPLICATION"]
        + excess_by_disposition["ASSEMBLY_DUPLICATION"]
    )

    return {
        "artifact_type": "clone_disposition_ledger",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "body_definition": "fichier moins sa ligne % META, identite declaree neutralisee, lignes vides retirees",
        "superseded_measure": SUPERSEDED_MEASURE,
        "scope": "objets reellement composes dans les 12 cibles canoniques",
        "groups": groups,
        "near_clone_groups": near_groups,
        "summary": {
            "ASSEMBLED_OBJECTS": len(records),
            "CLONE_GROUPS_TOTAL": len(groups),
            "EXPECTED_STUDENT_TEACHER_MIRROR": by_disposition["EXPECTED_STUDENT_TEACHER_MIRROR"],
            "INTENTIONAL_REUSE": by_disposition["INTENTIONAL_REUSE"],
            "ACCIDENTAL_RENDER_DUPLICATION": by_disposition["ACCIDENTAL_RENDER_DUPLICATION"],
            "SOURCE_CLONE_WITH_DISTINCT_IDS": by_disposition["SOURCE_CLONE_WITH_DISTINCT_IDS"],
            "ASSEMBLY_DUPLICATION": by_disposition["ASSEMBLY_DUPLICATION"],
            "NEAR_CLONES": len(near_groups),
            "EXCESS_BY_DISPOSITION": dict(excess_by_disposition),
            "TRUE_PRODUCT_CLONES_OPEN": true_product_clones,
            "CAPACITY_MISREPRESENTING_GROUPS": sum(
                1 for g in groups if g["capacity_misrepresenting"]
            ),
            "CROSS_MANUAL_GROUPS": sum(1 for g in groups if g["cross_manual"]),
            "REJECTED_REUSE_DECLARATIONS": sum(
                len(g["rejected_reuse_declarations"]) for g in groups
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--no-history", action="store_true")
    args = parser.parse_args()

    report = build(args.root, with_history=not args.no_history)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["# Disposition des groupes de contenus identiques", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
