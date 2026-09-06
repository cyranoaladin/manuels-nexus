#!/usr/bin/env python3
"""Lignee des objets pedagogiques avant le remplissage synthetique.

Le commit `533d1919` a introduit 986 fichiers exercices/corriges en recopiant
quelques corps canoniques. Son parent est donc un oracle : un objet qui portait
deja un corps substantiel avant lui est authentique ; un objet qui n'existait
pas est un filler. Cette lignee decide, aucune similarite textuelle ne decide.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/PREFILLER_LINEAGE.json"
MD_TARGET = ROOT / "audit/PREFILLER_LINEAGE.md"
GENERATED_BY = "scripts/build_prefiller_lineage.py"

#: Le commit qui a rempli les slots vides, etabli par archeologie.
FILLER_COMMIT = "533d19198eb7810699a41a7b5275744691420859"
#: En deca, un fichier n'est qu'un gabarit : il ne prouve aucune anteriorite.
SUBSTANTIVE_BYTES = 200

MIN_BODY_CHARS = 80


def _run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout


def prefiller_tree(root: Path, subdir: str) -> dict[str, int]:
    """Taille de chaque fichier juste avant le commit de remplissage."""

    output = _run_git(root, ["ls-tree", "-r", "-l", f"{FILLER_COMMIT}^", "--", subdir])
    sizes: dict[str, int] = {}
    for line in output.splitlines():
        parts = line.split(maxsplit=4)
        if len(parts) < 5 or parts[1] != "blob":
            continue
        size = parts[3]
        path = parts[4].strip()
        sizes[path] = int(size) if size.isdigit() else 0
    return sizes


def _body_text(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(line for line in lines[1:] if line.strip())


def filler_commit_bodies(root: Path, subdir: str) -> dict[str, str]:
    """Corps de chaque objet AU moment du remplissage, indexe par empreinte.

    Le remplissage a recopie le corps canonique tel qu'il etait alors. Un objet
    corrige depuis n'a donc plus le meme corps que ses copies : sans cet index,
    il sortirait de son groupe et le groupe paraitrait sans ancetre.
    """

    listing = _run_git(root, ["ls-tree", "-r", FILLER_COMMIT, "--", subdir])
    digest_to_paths: dict[str, str] = {}
    for line in listing.splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4 or parts[1] != "blob":
            continue
        blob, path = parts[2], parts[3].strip()
        if not path.endswith(".tex"):
            continue
        content = _run_git(root, ["cat-file", "-p", blob])
        body = _body_text(content)
        if len(body) < MIN_BODY_CHARS:
            continue
        digest_to_paths.setdefault(
            hashlib.sha256(body.encode()).hexdigest(), path
        )
    return digest_to_paths


def _body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(line for line in lines[1:] if line.strip())


def _meta(path: Path) -> dict[str, Any]:
    head = path.read_text(encoding="utf-8", errors="ignore").split("\n", 1)[0]
    if not head.startswith("% META:"):
        return {}
    try:
        return json.loads(head[len("% META:"):].strip())
    except json.JSONDecodeError:
        return {}



def _historical_bodies(root: Path, relative: str, limit: int = 60) -> set[str]:
    """Toutes les empreintes de corps qu'un fichier a portees au fil du temps."""

    revisions = _run_git(
        root, ["log", "--follow", "--format=%H", f"-{limit}", "--", relative]
    ).split()
    digests: set[str] = set()
    for revision in revisions:
        content = _run_git(root, ["show", f"{revision}:{relative}"])
        if not content:
            continue
        body = _body_text(content)
        if len(body) >= MIN_BODY_CHARS:
            digests.add(hashlib.sha256(body.encode()).hexdigest())
    return digests


def resolve_by_chapter_history(
    root: Path, group_digest: str, chapters: list[str], sizes: dict[str, int]
) -> str | None:
    """Chercher l'ancetre parmi les objets du meme chapitre qui preexistaient.

    Un corps canonique a pu changer apres le remplissage : la copie garde alors
    une version que l'original n'a plus. On interroge donc l'historique de
    chaque objet anterieur du chapitre, au lieu d'un seul instantane.
    """

    for path, size in sorted(sizes.items()):
        if size < SUBSTANTIVE_BYTES:
            continue
        if not any(f"/{chapter}/" in path for chapter in chapters):
            continue
        if group_digest in _historical_bodies(root, path):
            return path
    return None


def classify_groups(root: Path, subdir: str = "NSI/chapitres") -> dict[str, Any]:
    sizes = prefiller_tree(root, subdir)
    filler_bodies = filler_commit_bodies(root, subdir)

    records: dict[str, dict[str, Any]] = {}
    for path in sorted((root / subdir).rglob("*.tex")):
        if "_harvest" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        body = _body(path)
        if len(body) < MIN_BODY_CHARS:
            continue
        meta = _meta(path)
        prefiller_size = sizes.get(relative)
        records[relative] = {
            "path": relative,
            "object_id": meta.get("id"),
            "chapter": meta.get("chapitre"),
            "role": meta.get("type_objet"),
            "capacities": meta.get("capacites_codes") or meta.get("capacites") or [],
            "existed_before_filler": prefiller_size is not None,
            "prefiller_bytes": prefiller_size,
            "substantive_before_filler": bool(
                prefiller_size is not None and prefiller_size >= SUBSTANTIVE_BYTES
            ),
            "digest": hashlib.sha256(body.encode()).hexdigest(),
        }

    by_digest: dict[str, list[str]] = collections.defaultdict(list)
    for relative, record in records.items():
        by_digest[record["digest"]].append(relative)

    groups: list[dict[str, Any]] = []
    for digest, members in sorted(by_digest.items()):
        if len(members) < 2:
            continue
        entries = [records[m] for m in sorted(members)]
        preexisting = [e for e in entries if e["substantive_before_filler"]]
        body_length = len(_body(root / entries[0]["path"]))

        if body_length < SUBSTANTIVE_BYTES:
            # Aucun membre ne porte de contenu : ce groupe n'a pas de canonique
            # a elire, il n'a que des gabarits a retirer. Un placeholder n'est
            # pas publiable, il ne devient pas canonique faute de concurrent.
            groups.append({
                "digest": digest,
                "lineage_case": "PLACEHOLDER_NOT_CONTENT",
                "why": (
                    f"corps de {body_length} caracteres, sous le seuil de contenu : "
                    "gabarit reproduit, aucun objet pedagogique"
                ),
                "canonical_path": None,
                "canonical_object_id": None,
                "members": entries,
                "preexisting_paths": [e["path"] for e in preexisting],
                "filler_paths": [e["path"] for e in entries],
                "excess_objects": len(entries),
                "chapters": sorted({e["chapter"] for e in entries if e["chapter"]}),
                "manual": (
                    "1NSI" if all(str(e["chapter"]).startswith("1NSI") for e in entries)
                    else "TNSI" if all(str(e["chapter"]).startswith("TNSI") for e in entries)
                    else "MIXED"
                ),
            })
            continue

        if len(preexisting) == 1:
            case = "CANONICAL_BY_PRE_FILLER_LINEAGE"
            canonical = preexisting[0]["path"]
            why = "un seul membre portait deja un corps substantiel avant le remplissage"
        elif not preexisting and digest in filler_bodies:
            # Le corps du groupe est celui d'un objet qui, lui, preexistait :
            # l'ancetre existe, il a simplement ete corrige depuis.
            origin = filler_bodies[digest]
            if sizes.get(origin, 0) >= SUBSTANTIVE_BYTES:
                case = "CANONICAL_BY_PRE_FILLER_LINEAGE"
                canonical = origin
                why = (
                    "aucun membre ne preexistait, mais leur corps est celui d'un "
                    "objet anterieur au remplissage, corrige depuis"
                )
            else:
                case = "ALL_EMPTY_PRE_FILLER"
                canonical = None
                why = "aucun ancetre substantiel avant le remplissage"
        elif not preexisting:
            recovered = resolve_by_chapter_history(
                root,
                digest,
                sorted({str(e["chapter"]) for e in entries if e["chapter"]}),
                sizes,
            )
            if recovered:
                case = "RECOVERED_BY_LATER_HISTORY"
                canonical = recovered
                why = (
                    "l'ancetre est un objet anterieur au remplissage dont le corps "
                    "a change depuis ; la copie en garde une version historique"
                )
            else:
                case = "ALL_EMPTY_PRE_FILLER"
                canonical = None
                why = "aucun ancetre substantiel avant le remplissage"
        elif len(preexisting) > 1:
            case = "MULTIPLE_PREEXISTING_CONTENT"
            canonical = None
            why = "plusieurs membres preexistaient : ce ne sont pas des fillers equivalents"
        else:
            case = "ALL_EMPTY_PRE_FILLER"
            canonical = None
            why = "aucun membre n'existait avant le remplissage : l'histoire ne designe aucun proprietaire"

        groups.append({
            "digest": digest,
            "lineage_case": case,
            "why": why,
            "canonical_path": canonical,
            "canonical_object_id": (
                next((e["object_id"] for e in entries if e["path"] == canonical), None)
                if canonical else None
            ),
            "members": entries,
            "preexisting_paths": [e["path"] for e in preexisting],
            "filler_paths": [
                e["path"] for e in entries if not e["substantive_before_filler"]
            ],
            "excess_objects": len(entries) - 1,
            "chapters": sorted({e["chapter"] for e in entries if e["chapter"]}),
            "manual": (
                "1NSI" if all(str(e["chapter"]).startswith("1NSI") for e in entries)
                else "TNSI" if all(str(e["chapter"]).startswith("TNSI") for e in entries)
                else "MIXED"
            ),
        })

    by_case = collections.Counter(g["lineage_case"] for g in groups)
    per_manual: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for group in groups:
        per_manual[group["manual"]][group["lineage_case"]] += 1

    return {
        "artifact_type": "prefiller_lineage",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "filler_commit": FILLER_COMMIT,
        "oracle": f"{FILLER_COMMIT}^",
        "substantive_threshold_bytes": SUBSTANTIVE_BYTES,
        "groups": groups,
        "summary": {
            "CLONE_GROUPS": len(groups),
            "CANONICAL_BY_PRE_FILLER_LINEAGE": by_case["CANONICAL_BY_PRE_FILLER_LINEAGE"],
            "RECOVERED_BY_LATER_HISTORY": by_case["RECOVERED_BY_LATER_HISTORY"],
            "MULTIPLE_PREEXISTING_CONTENT": by_case["MULTIPLE_PREEXISTING_CONTENT"],
            "ALL_EMPTY_PRE_FILLER": by_case["ALL_EMPTY_PRE_FILLER"],
            "PLACEHOLDER_NOT_CONTENT": by_case["PLACEHOLDER_NOT_CONTENT"],
            "UNRESOLVED_AUTHOR_DECISION": (
                by_case["ALL_EMPTY_PRE_FILLER"] + by_case["MULTIPLE_PREEXISTING_CONTENT"]
            ),
            "FILLER_OBJECTS": sum(len(g["filler_paths"]) for g in groups),
            "PER_MANUAL": {k: dict(v) for k, v in sorted(per_manual.items())},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = classify_groups(args.root)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["# Lignee des objets avant le remplissage synthetique", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
