#!/usr/bin/env python3
"""Verite d'assemblage des cours : qui possede quel corps, et ce qui s'imprime.

Le sommaire imprime du manuel 1NSI ouvre le chapitre « Algorithmique 1 :
parcours et tris » sur six sections qui appartiennent au chapitre suivant --
recherche dichotomique, algorithmes gloutons, k plus proches voisins -- chacune
imprimee DEUX fois, avant que le chapitre n'arrive a son propre contenu. Les
memes corps sont ensuite imprimes une troisieme fois, dans le chapitre auquel
ils appartiennent reellement.

Un registre de clones dit qu'un corps est partage. Il ne dit pas ce que le
lecteur recoit. Ce producteur mesure l'ecart entre le cours qu'un chapitre
DEVRAIT assembler et celui qu'il assemble, en trois grandeurs :

`FOREIGN_COURSE_BODY`
    un corps assemble par un chapitre dont il n'est pas le proprietaire
    semantique ;

`DUPLICATED_COURSE_BODY`
    un corps assemble plusieurs fois dans le meme chapitre ;

`MISSING_EXPECTED_COURSE_BODY`
    une capacite du contrat qu'aucun corps de cours ne sert.

Le proprietaire n'est jamais deduit d'un ordre de fichiers : il vient de la
selection canonique par preuve du registre P0.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit/COURSE_BODY_OWNERSHIP_MAP.json"
CLONE_LEDGER = ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json"
CORPORA = (
    ROOT / "Mathematiques" / "manuel-maths" / "chapitres",
    ROOT / "NSI" / "chapitres",
)
SECTION = re.compile(r"\\section\{([^}]*)\}")


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def build_map() -> dict[str, Any]:
    clone = _load("p0_clone_ledger", "scripts/build_p0_content_clone_ledger.py")
    identity = _load("capacity_identity", "scripts/capacity_identity.py")
    resolver = identity.CapacityIdentityResolver.from_corpora()
    ledger = json.loads(CLONE_LEDGER.read_text(encoding="utf-8"))

    # Proprietaire semantique par chemin, tel que le registre l'a ETABLI.
    owner_of: dict[str, str] = {}
    ambiguous_paths: set[str] = set()
    for group in ledger["groups"]:
        selection = group["canonical_selection"]
        if selection["status"] == "AMBIGUOUS":
            ambiguous_paths.update(row["path"] for row in group["members"])
            continue
        canonical = set(selection["canonical_paths"])
        owners = sorted(
            {row["chapter"] for row in group["members"] if row["path"] in canonical}
        )
        if len(owners) != 1:
            continue
        for row in group["members"]:
            owner_of[row["path"]] = owners[0]

    bodies: dict[str, dict[str, Any]] = {}
    chapters: dict[str, dict[str, Any]] = {}
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for directory in sorted(corpus.iterdir()):
            if not (directory / "contrat.yaml").is_file():
                continue
            chapter = directory.name
            if chapter not in resolver.chapters:
                continue
            course = directory / "cours"
            assembled: list[dict[str, Any]] = []
            served: set[str] = set()
            for position, path in enumerate(sorted(course.glob("*.tex")), start=1):
                text = path.read_text(encoding="utf-8", errors="replace")
                meta = clone.read_meta(text)
                digest = clone.digest(clone.pedagogical_body(text))
                relative = str(path.relative_to(ROOT))
                raws = [
                    identity.normalise(value)
                    for key in ("capacites_codes", "capacites")
                    for value in (meta.get(key) or [])
                ]
                codes = resolver.resolve_codes(chapter, [r for r in raws if r])
                owner = owner_of.get(relative, chapter)
                titles = SECTION.findall(text)
                assembled.append(
                    {
                        "assembly_position": position,
                        "path": relative,
                        "body_digest": digest,
                        "declared_capacities": list(codes),
                        "semantic_owner_chapter": owner,
                        "is_foreign": owner != chapter,
                        "ownership_proven": relative not in ambiguous_paths,
                        "toc_titles": titles,
                    }
                )
                if owner == chapter:
                    served.update(codes)
                entry = bodies.setdefault(
                    digest,
                    {
                        "body_digest": digest,
                        "toc_titles": titles,
                        "authentic_chapter": owner,
                        "carriers": [],
                    },
                )
                entry["carriers"].append(
                    {"chapter": chapter, "path": relative, "capacities": list(codes)}
                )

            seen = collections.Counter(row["body_digest"] for row in assembled)
            duplicated = sorted(d for d, n in seen.items() if n > 1)
            foreign = [row["path"] for row in assembled if row["is_foreign"]]
            expected = [item.local_code for item in resolver.capacities_of(chapter)]
            missing = [code for code in expected if code not in served]
            chapters[chapter] = {
                "expected_capacities": expected,
                "assembled_bodies": assembled,
                "foreign_course_bodies": foreign,
                "duplicated_course_body_digests": duplicated,
                "duplicated_course_body_count": sum(
                    n - 1 for n in seen.values() if n > 1
                ),
                "missing_expected_course_capacities": missing,
            }

    shared = {
        digest: entry
        for digest, entry in bodies.items()
        if len({carrier["chapter"] for carrier in entry["carriers"]}) > 1
    }
    for entry in shared.values():
        entry["false_copies"] = sorted(
            carrier["path"]
            for carrier in entry["carriers"]
            if carrier["chapter"] != entry["authentic_chapter"]
        )

    totals = {
        "FOREIGN_COURSE_BODY": sum(
            len(row["foreign_course_bodies"]) for row in chapters.values()
        ),
        "DUPLICATED_COURSE_BODY": sum(
            row["duplicated_course_body_count"] for row in chapters.values()
        ),
        "MISSING_EXPECTED_COURSE_BODY": sum(
            len(row["missing_expected_course_capacities"]) for row in chapters.values()
        ),
    }
    return {
        "artifact_type": "course_body_ownership_map",
        "schema_version": 1,
        "generated_by": "scripts/build_course_assembly_truth.py",
        "ownership_rule": (
            "le proprietaire vient de la selection canonique par preuve du "
            "registre P0 ; jamais de l'ordre des fichiers"
        ),
        "totals": totals,
        "chapters_with_foreign_bodies": sorted(
            name for name, row in chapters.items() if row["foreign_course_bodies"]
        ),
        "chapters_with_duplicated_bodies": sorted(
            name
            for name, row in chapters.items()
            if row["duplicated_course_body_count"]
        ),
        "shared_bodies": [shared[k] for k in sorted(shared)],
        "chapters": {name: chapters[name] for name in sorted(chapters)},
        "map_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(sorted(shared), separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    rendered = render(build_map())
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    totals = json.loads(rendered)["totals"]
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {totals}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
