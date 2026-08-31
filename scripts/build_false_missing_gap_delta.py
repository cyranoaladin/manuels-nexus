#!/usr/bin/env python3
"""Les lacunes qui n'existaient pas : le delta 460 -> 380, nomme ligne a ligne.

Une lacune inventee coute aussi cher qu'une lacune ignoree. Elle envoie
reecrire du contenu qui va tres bien, et le volume ainsi recree ressemble
exactement au remplissage que la campagne repare.

Quatre-vingts unites d'ecriture du backlog precedent n'existaient pas. Le
contenu etait la ; c'est la MESURE qui ne savait pas le reconnaitre, parce
qu'elle extrayait un jeton local des references pleinement qualifiees au lieu
de les comparer par egalite.

Ce producteur ne se contente pas d'annoncer -80. Pour chaque unite retiree il
nomme la capacite, le role, la raison exacte de la fausse lacune, l'objet qui
la satisfait reellement, et l'identite canonique resolue.
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
COVERAGE_REL = "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
OUTPUT = ROOT / "audit/FALSE_MISSING_GAP_DELTA.json"

#: Etat du backlog AVANT le recablage du resolveur. Fige par son sha de
#: commit : le comparer a l'artefact courant ferait disparaitre le delta des
#: qu'il serait recalcule.
BEFORE_SHA = "289daa61dadfd977fec668d8405c98c4d9f10d34"


def _load(module_name: str, relative: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _backlog_at(sha: str) -> set[tuple[str, str, str]]:
    blob = subprocess.run(
        ["git", "show", f"{sha}:{COVERAGE_REL}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    payload = json.loads(blob)
    return {
        (row["chapter"], row["capacity"], row["role"])
        for row in payload["authoring_backlog"]
    }


def build_delta() -> dict[str, Any]:
    identity = _load("capacity_identity", "scripts/capacity_identity.py")
    clone = _load("p0_clone_ledger", "scripts/build_p0_content_clone_ledger.py")
    coverage = _load("true_coverage", "scripts/build_true_pedagogical_coverage.py")

    resolver = identity.CapacityIdentityResolver.from_corpora()
    before = _backlog_at(BEFORE_SHA)
    current = coverage.build_coverage()
    after = {
        (row["chapter"], row["capacity"], row["role"])
        for row in current["authoring_backlog"]
    }
    # Une unite peut sortir du backlog pour deux raisons TRES differentes :
    # soit son contenu credite reellement la capacite, soit son contenu existe
    # mais appartient a un groupe de clones dont le proprietaire n'est pas
    # demontrable. Les confondre ferait passer une revue a faire pour du
    # travail deja acquis.
    state_by_cell = {
        (row["chapter"], row["capacity"], row["role"]): row["state"]
        for row in current["rows"]
    } if "rows" in current else {}

    removed = sorted(before - after)
    added = sorted(after - before)

    invalid = set(
        json.loads(
            (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
        )["objects_on_invalid_credit"]
    )

    # Quel objet satisfait reellement chaque unite faussement manquante, et
    # par quelle regle de resolution son credit etait-il invisible ?
    satisfiers: dict[tuple[str, str, str], list[dict[str, Any]]] = (
        collections.defaultdict(list)
    )
    for corpus in coverage.CORPORA:
        if not corpus.is_dir():
            continue
        for path in sorted(corpus.rglob("*.tex")):
            if any(part in coverage.UNPUBLISHED for part in path.parts):
                continue
            index = path.parts.index("chapitres") + 1
            chapter, role = path.parts[index], path.parts[index + 1]
            if role not in coverage.MEASURED_ROLES:
                continue
            if chapter not in resolver.chapters:
                continue
            if str(path.relative_to(ROOT)) in invalid:
                continue
            meta = clone.read_meta(path.read_text(encoding="utf-8", errors="replace"))
            raws = []
            for key in ("capacites_codes", "capacites"):
                for value in meta.get(key) or []:
                    text = identity.normalise(value)
                    if text and text not in raws:
                        raws.append(text)
            for raw in raws:
                try:
                    resolution = resolver.resolve(chapter, raw)
                except identity.CapacityIdentityError:
                    continue
                if resolution.rule == identity.PREREQUISITE:
                    continue
                key = (chapter, resolution.identity.local_code, role)
                if key in before and key not in after:
                    satisfiers[key].append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "declared_as": raw,
                            "resolution_rule": resolution.rule,
                            "canonical_uid": resolution.identity.uid,
                            "official_ref": resolution.identity.official_ref,
                        }
                    )

    rows: list[dict[str, Any]] = []
    for chapter, capacity, role in removed:
        evidence = satisfiers.get((chapter, capacity, role), [])
        rules = sorted({item["resolution_rule"] for item in evidence})
        state = state_by_cell.get((chapter, capacity, role), "VALID_ALIGNED_CONTENT")
        rows.append(
            {
                "removal_class": (
                    "RECOVERED_VALID_CREDIT"
                    if state == "VALID_ALIGNED_CONTENT"
                    else "RECLASSIFIED_INDETERMINATE"
                ),
                "current_state": state,
                "chapter": chapter,
                "manual": identity.manual_of(chapter),
                "capacity": capacity,
                "role": role,
                "canonical_uid": f"{identity.manual_of(chapter)}::{chapter}::{capacity}",
                "why_it_was_falsely_missing": (
                    "l'objet declarait la capacite sous une forme pleinement "
                    "qualifiee que la mesure precedente reduisait a un jeton "
                    "local, donc ne rapprochait pas du code du contrat"
                ),
                "resolution_rules_that_recover_it": rules,
                "satisfied_by": sorted(item["path"] for item in evidence),
                "evidence": sorted(evidence, key=lambda item: item["path"]),
            }
        )

    unexplained = [row for row in rows if not row["satisfied_by"]]
    per_class = collections.Counter(row["removal_class"] for row in rows)
    per_manual = collections.Counter(row["manual"] for row in rows)
    per_rule = collections.Counter(
        rule for row in rows for rule in row["resolution_rules_that_recover_it"]
    )
    return {
        "artifact_type": "false_missing_gap_delta",
        "schema_version": 1,
        "generated_by": "scripts/build_false_missing_gap_delta.py",
        "before_sha": BEFORE_SHA,
        "before_authoring_units": len(before),
        "after_authoring_units": len(after),
        "false_missing_gaps_removed": len(removed),
        "gaps_added": len(added),
        "added": [
            {"chapter": c, "capacity": k, "role": r} for c, k, r in added
        ],
        "unexplained_removals": len(unexplained),
        "per_removal_class": dict(sorted(per_class.items())),
        "per_manual": dict(sorted(per_manual.items())),
        "per_resolution_rule": dict(sorted(per_rule.items())),
        "removed_units_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(
                [f"{c}/{k}/{r}" for c, k, r in removed], separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest(),
        "removed_units": rows,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_delta()
    if payload["unexplained_removals"]:
        raise SystemExit(
            f"{payload['unexplained_removals']} unites retirees sans contenu "
            "qui les satisfasse : ce ne sont pas de fausses lacunes"
        )
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: "
        f"{payload['false_missing_gaps_removed']} fausses lacunes, "
        f"{payload['gaps_added']} ajoutees"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
