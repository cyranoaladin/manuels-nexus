#!/usr/bin/env python3
"""Classification read-only du graphe des fichiers de style LaTeX.

Pour chaque fichier .sty / .cls suivi par git, ce controle etablit :

* ses consommateurs exhaustifs, preuve par preuve (chemin + ligne) ;
* sa classe : ACTIVE_CANONICAL, ACTIVE_NONCANONICAL, HISTORICAL_ONLY,
  FIXTURE_ONLY, OBSOLETE ;
* pour chaque groupe de duplicatas de contenu : le survivant canonique, ses
  consommateurs et un verdict safe-to-delete argumente.

Ce script ne supprime rien et ne modifie rien. Un verdict safe-to-delete n'est
emis que lorsque la preuve de consommateurs est exhaustive et vide.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STYLE_SUFFIXES = (".sty", ".cls")
#: Extensions dans lesquelles un consommateur peut se declarer.
CONSUMER_SUFFIXES = (
    ".tex",
    ".cls",
    ".sty",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".toml",
    ".cfg",
    ".mk",
    ".sh",
)
CONSUMER_NAMES = ("Makefile", "makefile")

LATEX_LOAD_RE = re.compile(
    r"\\(?:usepackage|RequirePackage|documentclass|LoadClass|LoadClassWithOptions)"
    r"(?:\[[^\]]*\])?\{([^}]*)\}"
)

#: Un consommateur de production : il participe a la fabrication d'un livrable.
PRODUCTION_HINTS = ("gabarits/", "/scripts/", "/build/", "assemble", "Makefile")
TEST_HINTS = ("/tests/", "test_", "/fixtures/")
REPORT_HINTS = ("audit/", "docs/", "README", ".md")


@dataclass
class Reference:
    consumer: str
    line: int
    kind: str
    relation: str
    excerpt: str


@dataclass
class StyleFile:
    path: str
    name: str
    suffix: str
    sha256: str
    size: int
    references: list[Reference] = field(default_factory=list)
    classification: str = "UNCLASSIFIED"
    rationale: str = ""
    duplicate_group: str | None = None
    canonical_survivor: str | None = None
    duplicate_kind: str | None = None
    safe_to_delete: bool = False
    migration_needed: bool = False


def tracked_files(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    )
    return completed.stdout.splitlines()


def _is_consumer_candidate(relative: str) -> bool:
    name = Path(relative).name
    return name in CONSUMER_NAMES or Path(relative).suffix in CONSUMER_SUFFIXES


def _reference_kind(consumer: str) -> str:
    if any(hint in consumer for hint in TEST_HINTS):
        return "test"
    if any(hint in consumer for hint in PRODUCTION_HINTS):
        return "production"
    if any(hint in consumer for hint in REPORT_HINTS):
        return "report"
    return "other"


def _resolve_load(
    token: str, consumer: str, by_stem: dict[str, list[str]]
) -> list[str]:
    """Resout un \\usepackage vers le ou les fichiers reellement charges.

    TeX resout d'abord dans le repertoire du document courant : une classe du
    sous-arbre NSI qui charge nexus-charte-v6 charge la copie NSI, pas celle des
    mathematiques. On restreint donc au sous-arbre du consommateur quand il en
    existe une, sinon on garde tous les candidats.
    """

    candidates = by_stem.get(Path(token).stem, [])
    if len(candidates) <= 1:
        return list(candidates)
    prefix = consumer.split("/")[0]
    local = [item for item in candidates if item.split("/")[0] == prefix]
    return local or list(candidates)


def collect(root: Path = ROOT) -> list[StyleFile]:
    tracked = tracked_files(root)
    styles = [item for item in tracked if item.endswith(STYLE_SUFFIXES)]
    entries = {}
    for relative in styles:
        data = (root / relative).read_bytes()
        entries[relative] = StyleFile(
            path=relative,
            name=Path(relative).name,
            suffix=Path(relative).suffix,
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
        )

    #: Un module LaTeX est charge par son nom sans extension.
    by_stem: dict[str, list[str]] = defaultdict(list)
    for relative in styles:
        by_stem[Path(relative).stem].append(relative)
    style_names = [(relative, Path(relative).name) for relative in styles]

    for relative in tracked:
        if relative in entries or not _is_consumer_candidate(relative):
            continue
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        kind = _reference_kind(relative)
        latex_source = Path(relative).suffix in (".tex", ".sty", ".cls")
        for number, line in enumerate(text.splitlines(), start=1):
            targets: dict[str, str] = {}
            if ".sty" in line or ".cls" in line:
                for style, name in style_names:
                    if name in line:
                        targets[style] = "path_mention"
            # Un chargement LaTeX prime sur une simple mention de chemin : c'est
            # le seul lien qui fait reellement entrer le fichier dans un build.
            # Il n'est reconnu que dans une source LaTeX : la meme sequence dans
            # un litteral Python ou une docstring n'est qu'une mention.
            for match in LATEX_LOAD_RE.finditer(line) if latex_source else ():
                for token in match.group(1).split(","):
                    for candidate in _resolve_load(token.strip(), relative, by_stem):
                        targets[candidate] = "load"
            for target, relation in targets.items():
                entries[target].references.append(
                    Reference(
                        consumer=relative,
                        line=number,
                        kind=kind,
                        relation=relation,
                        excerpt=line.strip()[:160],
                    )
                )
    return list(entries.values())


def classify(entries: list[StyleFile]) -> list[StyleFile]:
    by_digest: dict[str, list[StyleFile]] = defaultdict(list)
    for entry in entries:
        by_digest[entry.sha256].append(entry)

    for digest, group in by_digest.items():
        if len(group) < 2:
            continue
        # Le seul survivant canonique defendable est celui du repertoire
        # partage. Entre deux copies par discipline, aucun arbitrage n'est
        # derivable du contenu : le groupe est declare tel quel.
        shared = [item for item in group if item.path.startswith("gabarits/")]
        survivor = shared[0].path if len(shared) == 1 else None
        kind = "SHARED_ORIGINAL" if survivor else "PER_DISCIPLINE_COPY"
        for item in group:
            item.duplicate_group = f"sha256:{digest[:16]}"
            item.canonical_survivor = survivor
            item.duplicate_kind = (
                "SHARED_ORIGINAL" if survivor == item.path else kind
            )

    for entry in entries:
        loads = [ref for ref in entry.references if ref.relation == "load"]
        production_loads = [ref for ref in loads if ref.kind == "production"]
        test_loads = [ref for ref in loads if ref.kind == "test"]
        mentions = [ref for ref in entry.references if ref.relation == "path_mention"]
        mention_kinds = {ref.kind for ref in mentions}

        if production_loads:
            wrapper = entry.duplicate_kind == "PER_DISCIPLINE_COPY"
            entry.classification = (
                "ACTIVE_NONCANONICAL" if wrapper else "ACTIVE_CANONICAL"
            )
            entry.rationale = (
                f"charge par {len(production_loads)} consommateur(s) de production"
                + (
                    f" ; copie par discipline du groupe {entry.duplicate_group}"
                    if wrapper
                    else ""
                )
            )
            entry.migration_needed = wrapper
        elif test_loads:
            entry.classification = "FIXTURE_ONLY"
            entry.rationale = f"charge uniquement par {len(test_loads)} test(s)"
        elif not entry.references:
            entry.classification = "OBSOLETE"
            entry.rationale = "aucun consommateur ni mention suivis par git"
            entry.safe_to_delete = True
        elif mention_kinds <= {"report", "other"}:
            entry.classification = "HISTORICAL_ONLY"
            entry.rationale = (
                f"aucun chargement LaTeX ; {len(mentions)} mention(s) en rapport "
                "ou documentation uniquement"
            )
        else:
            entry.classification = "ACTIVE_NONCANONICAL"
            entry.rationale = (
                f"aucun chargement LaTeX mais {len(mentions)} mention(s) dont "
                f"{sorted(mention_kinds)} : lien a instruire avant toute suppression"
            )
    return entries


def build_report(root: Path = ROOT) -> dict:
    entries = classify(collect(root))
    entries.sort(key=lambda item: item.path)

    groups: dict[str, list[StyleFile]] = defaultdict(list)
    for entry in entries:
        if entry.duplicate_group:
            groups[entry.duplicate_group].append(entry)

    duplicate_report = []
    for group_id, members in sorted(groups.items()):
        survivor = members[0].canonical_survivor
        duplicate_report.append(
            {
                "duplicate_group": group_id,
                "member_count": len(members),
                "members": [item.path for item in members],
                "canonical_survivor": survivor,
                "duplicate_kind": members[0].duplicate_kind,
                "resolution_required": (
                    "aucun survivant derivable du contenu : les deux copies sont "
                    "chargees par leur propre discipline ; la convergence doit se "
                    "faire vers gabarits/common et non par suppression de l'une"
                    if survivor is None
                    else None
                ),
                "consumers": {
                    item.path: sorted({ref.consumer for ref in item.references})
                    for item in members
                },
                "safe_to_delete": {
                    item.path: (
                        survivor is not None
                        and item.path != survivor
                        and not item.references
                    )
                    for item in members
                },
                "migration_needed": {
                    item.path: item.migration_needed for item in members
                },
            }
        )

    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        counts[entry.classification] += 1

    no_load_edge = [
        entry.path
        for entry in entries
        if not any(ref.relation == "load" for ref in entry.references)
    ]

    return {
        "artifact_type": "style_graph_classification",
        "schema_version": 1,
        "generated_by": "scripts/classify_style_graph.py",
        "read_only": True,
        "deletes_nothing": True,
        "physical_file_count": len(entries),
        "classification_counts": dict(sorted(counts.items())),
        "duplicate_group_count": len(duplicate_report),
        "no_load_edge_files": no_load_edge,
        "no_load_edge_count": len(no_load_edge),
        "load_edge_definition": (
            "un \\usepackage / \\RequirePackage / \\documentclass ecrit dans une "
            "source LaTeX suivie par git et resolu vers ce fichier ; une mention "
            "du meme nom dans un script, un test ou un rapport n'est pas un "
            "chargement"
        ),
        "files": [asdict(entry) for entry in entries],
        "duplicate_groups": duplicate_report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="ecrire le rapport JSON dans ce fichier")
    args = parser.parse_args(argv)

    report = build_report(ROOT)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(
            f"{report['physical_file_count']} fichiers, "
            f"{report['duplicate_group_count']} groupes de duplicatas"
        )
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
