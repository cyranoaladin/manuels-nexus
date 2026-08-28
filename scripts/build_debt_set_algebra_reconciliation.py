#!/usr/bin/env python3
"""Algebre EXACTE des ensembles de dette, en empreintes et non en nombres.

Constat qui motive cet artefact : la soustraction naive
``6541 - 5371 = 1170`` ne rend pas ``2232``. Elle est fausse parce que le
champ ``resolved`` du fichier de baseline n'est PAS l'ensemble des empreintes
de reference resolues : il archive toutes les generations, dont 951 empreintes
deja resolues avant que la baseline de reference ne soit gelee.

Cet artefact ne commente pas des nombres : il produit les ENSEMBLES, leur
cardinal et leur digest, et exige que leur union soit exactement l'actif
courant, sans recouvrement et sans inconnu.

Aucune baseline n'est modifiee : lecture seule sur Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit" / "DEBT_SET_ALGEBRA_RECONCILIATION_CURRENT.json"
OUTPUT_MD = ROOT / "audit" / "DEBT_SET_ALGEBRA_RECONCILIATION_CURRENT.md"
BASELINE = "audit/ANOMALIES_BASELINE.json"

#: Blob portant la baseline de reference (6541 empreintes actives). Le champ
#: git_sha du fichier designe le commit qu'il DECRIT (7752988a) et non celui ou
#: il est range : deux versions distinctes portent ce meme git_sha, ce qui rend
#: l'ancre ambigue. Le blob est donc designe explicitement.
REFERENCE_BLOB_COMMIT = "28cf690381bed58544fc606f11396e159bc200c3"
REFERENCE_DESCRIBED_SHA = "7752988ae7041a7a5de700fcf4609bd47a4fba3a"
REFERENCE_DIGEST = (
    "sha256:3757764ead6d1a4fbd0aef0f8d01637f10c80cd5c044350e2108ffe1614ee056"
)
#: Le document de provenance annonce 6541 empreintes AU commit 7752988a. Or le
#: fichier de baseline A ce commit en contient 2866 : le jeu de 6541 vit dans un
#: blob posterieur qui, lui, porte encore 7752988a dans son champ git_sha
#: interne. Cette metadonnee interne est donc HISTORIQUEMENT PERIMEE. On ne
#: reecrit ni la baseline ni l'historique : on nomme le defaut et on prouve
#: qu'aucun consommateur courant ne s'y fie.
DECLARED_REFERENCE_COMMIT = "7752988ae7041a7a5de700fcf4609bd47a4fba3a"
REFERENCE_BLOB_ID = "e66f1db022065965385c0ecf6073b5f29577ebf1"

A4_DECISION = (
    "audit/A4_METHOD_REVIEW_DEBT_POLICY.md"
    "#decision-a4-method-review-debt-2026-08-19"
)
RESIDUAL_13_DECISION = (
    "audit/BASELINE_QUALIFICATION_DECISION.md"
    "#decision-baseline-residual-13-temporary-2026-08-25"
)
NSI_STATUS_DECISION = (
    "audit/BASELINE_QUALIFICATION_DECISION.md"
    "#decision-baseline-status-governance-1nsi-2026-08-10"
)
TRIGO_DECISION_PREFIX = (
    "audit/HUMAN_DECISION_1SPE_TRIGO_OPTIONAL_EXTENSIONS_2026-08-23.md"
)


def set_digest(fingerprints: Iterable[str]) -> str:
    """Meme formule que le digest de la baseline de reference."""

    payload = json.dumps(sorted(fingerprints), separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _baseline_at(commit: str) -> dict[str, Any]:
    raw = subprocess.run(
        ["git", "show", f"{commit}:{BASELINE}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(raw)


def _described(entries: Iterable[dict[str, Any]]) -> set[str]:
    return {str(entry["fingerprint"]) for entry in entries}


def _class_of(entry: dict[str, Any]) -> str:
    reference = entry.get("decision_ref")
    if reference is None:
        return "SURVIVING_REFERENCE"
    if reference == A4_DECISION:
        return "A4_METHOD_REVIEW_DEBT"
    if reference == RESIDUAL_13_DECISION:
        return "RESIDUAL_QUALIFIED_REVIEW_DEBT"
    if reference == NSI_STATUS_DECISION:
        return "NSI_STATUS_GOVERNANCE_DEBT"
    if str(reference).startswith(TRIGO_DECISION_PREFIX):
        return "TRIGO_OPTIONAL_EXTENSION_DEBT"
    return "UNKNOWN"


def _blob_id(commit: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{commit}:{BASELINE}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _stale_provenance_ledger(reference_active: set[str]) -> dict[str, Any]:
    """Nomme le defaut de provenance sans toucher a la baseline ni a l'historique."""

    declared = _baseline_at(DECLARED_REFERENCE_COMMIT)
    return {
        "classification": "HISTORICAL_STALE_PROVENANCE_METADATA",
        "declared_reference_commit": DECLARED_REFERENCE_COMMIT,
        "actual_set_size_at_declared_commit": len(declared["active"]),
        "actual_blob_commit_containing_the_reference_set": REFERENCE_BLOB_COMMIT,
        "actual_blob_id": _blob_id(REFERENCE_BLOB_COMMIT),
        "blob_id_at_declared_commit": _blob_id(DECLARED_REFERENCE_COMMIT),
        "internal_stale_git_sha": DECLARED_REFERENCE_COMMIT,
        "reference_set_size": len(reference_active),
        "baseline_modified": False,
        "history_rewritten": False,
        "current_authority": [
            "exact fingerprint set",
            "set digest",
            "actual containing blob id and commit",
        ],
        "internal_git_sha_is_authoritative": False,
        "note": (
            "le champ git_sha interne de la baseline ne designe pas un ensemble "
            "unique : deux blobs distincts le portent. L'autorite courante est "
            "l'ensemble d'empreintes et son digest, ancres sur le blob reel."
        ),
    }


def build_reconciliation() -> dict[str, Any]:
    reference = _baseline_at(REFERENCE_BLOB_COMMIT)
    current = json.loads((ROOT / BASELINE).read_text(encoding="utf-8"))

    reference_active = _described(reference["active"])
    reference_resolved_at_freeze = _described(reference["resolved"])
    current_active_entries = list(current["active"])
    current_active = _described(current_active_entries)
    current_resolved = _described(current["resolved"])

    resolved_reference = reference_active & current_resolved
    surviving_reference = reference_active & current_active
    reference_untraced = reference_active - current_active - current_resolved
    resolved_pre_reference = current_resolved - reference_active
    post_reference_active = current_active - reference_active

    classes: dict[str, set[str]] = {}
    for entry in current_active_entries:
        classes.setdefault(_class_of(entry), set()).add(str(entry["fingerprint"]))

    union: set[str] = set()
    overlaps: list[str] = []
    for name, members in classes.items():
        overlap = union & members
        if overlap:
            overlaps.append(name)
        union |= members

    def described(name: str, members: set[str], note: str) -> dict[str, Any]:
        return {
            "set": name,
            "cardinality": len(members),
            "set_digest": set_digest(members),
            "note": note,
        }

    sets = [
        described(
            "REFERENCE_BASELINE",
            reference_active,
            "empreintes actives de la baseline de reference gelee ; aucune "
            "autorite humaine exacte ne la couvre (EXACT_HUMAN_AUTHORITY=NONE)",
        ),
        described(
            "RESOLVED_REFERENCE",
            resolved_reference,
            "empreintes de reference effectivement resolues depuis le gel",
        ),
        described(
            "SURVIVING_REFERENCE",
            surviving_reference,
            "empreintes de reference encore actives ; elles ne portent aucun "
            "decision_ref car elles precedent toute qualification de classe",
        ),
        described(
            "REFERENCE_UNTRACED",
            reference_untraced,
            "empreintes de reference ni actives ni archivees : doit valoir 0",
        ),
        described(
            "RESOLVED_PRE_REFERENCE",
            resolved_pre_reference,
            "archivees AVANT le gel de reference ; c'est exactement ce que la "
            "soustraction naive 6541-5371 comptait a tort",
        ),
        described(
            "POST_REFERENCE_ACTIVE",
            post_reference_active,
            "dettes qualifiees apparues apres le gel de reference",
        ),
        described(
            "A4_METHOD_REVIEW_DEBT",
            classes.get("A4_METHOD_REVIEW_DEBT", set()),
            "dette de revue des fiches methode sous politique de classe A4 ; "
            "le chiffre historique 89 agregeait cette classe et les extensions "
            "optionnelles TRIGO, qui relevent d'une AUTRE decision humaine",
        ),
        described(
            "TRIGO_OPTIONAL_EXTENSION_DEBT",
            classes.get("TRIGO_OPTIONAL_EXTENSION_DEBT", set()),
            "extensions optionnelles 1SPE-TRIGONOMETRIE ; decision humaine "
            "distincte, jamais a fondre dans la classe A4",
        ),
        described(
            "RESIDUAL_QUALIFIED_REVIEW_DEBT",
            classes.get("RESIDUAL_QUALIFIED_REVIEW_DEBT", set()),
            "les treize dettes residuelles qualifiees temporairement ; leur "
            "sunset exige de les garder distinctes",
        ),
        described(
            "NSI_STATUS_GOVERNANCE_DEBT",
            classes.get("NSI_STATUS_GOVERNANCE_DEBT", set()),
            "gouvernance des statuts 1NSI",
        ),
        described(
            "OTHER_CURRENT_DEBT",
            classes.get("OTHER_CURRENT_DEBT", set()),
            "aucune dette courante hors des classes nommees",
        ),
        described("CURRENT_ACTIVE", current_active, "actif courant total"),
    ]

    partition = {
        "classes": sorted(classes),
        "union_equals_current_active": union == current_active,
        "pairwise_disjoint": not overlaps,
        "unknown": len(classes.get("UNKNOWN", set())),
        "cardinality_equation": (
            f"{len(current_active)} = "
            f"{len(classes.get('SURVIVING_REFERENCE', set()))} + "
            f"{len(classes.get('A4_METHOD_REVIEW_DEBT', set()))} + "
            f"{len(classes.get('RESIDUAL_QUALIFIED_REVIEW_DEBT', set()))} + "
            f"{len(classes.get('NSI_STATUS_GOVERNANCE_DEBT', set()))} + "
            f"{len(classes.get('TRIGO_OPTIONAL_EXTENSION_DEBT', set()))}"
        ),
    }

    return {
        "artifact_type": "debt_set_algebra_reconciliation",
        "schema_version": 1,
        "generated_by": "scripts/build_debt_set_algebra_reconciliation.py",
        "modifies_no_baseline": True,
        "release_acceptance": False,
        "reference_baseline": {
            "blob_commit": REFERENCE_BLOB_COMMIT,
            "described_git_sha": REFERENCE_DESCRIBED_SHA,
            "declared_digest": REFERENCE_DIGEST,
            "recomputed_digest": set_digest(reference_active),
            "digest_reproduced": set_digest(reference_active) == REFERENCE_DIGEST,
            "historical_stale_provenance_metadata": _stale_provenance_ledger(
                reference_active
            ),
            "anchor_ambiguity": (
                "deux versions distinctes du fichier de baseline portent le "
                "meme git_sha 7752988a (2866 puis 6541 actives) : l'ancre par "
                "git_sha ne designe pas un ensemble unique, le blob si"
            ),
        },
        "metric_renaming": {
            "baseline_field": "resolved",
            "observed_cardinality": len(current_resolved),
            "is_reference_baseline_resolved": False,
            "correct_name": "RESOLVED_ARCHIVE_ALL_GENERATIONS",
            "decomposition": {
                "RESOLVED_REFERENCE": len(resolved_reference),
                "RESOLVED_PRE_REFERENCE": len(resolved_pre_reference),
            },
            "rationale": (
                "le mot resolved designait deux ensembles differents ; le champ "
                "de la baseline n'est pas renomme car aucune mise a jour de "
                "baseline n'est autorisee, mais la METRIQUE publiee l'est"
            ),
        },
        "naive_subtraction": {
            "expression": "6541 - 5371",
            "value": len(reference_active) - len(current_resolved),
            "is_wrong": True,
            "why": (
                f"{len(resolved_pre_reference)} des {len(current_resolved)} "
                "empreintes archivees n'ont jamais appartenu a la baseline de "
                "reference"
            ),
            "correct_expression": (
                f"|REFERENCE_BASELINE| - |RESOLVED_REFERENCE| + "
                f"|POST_REFERENCE_ACTIVE| = {len(reference_active)} - "
                f"{len(resolved_reference)} + {len(post_reference_active)} = "
                f"{len(current_active)}"
            ),
        },
        "sets": sets,
        "partition": partition,
        "invariants": {
            "reference_partition_exact": (
                len(resolved_reference)
                + len(surviving_reference)
                + len(reference_untraced)
                == len(reference_active)
            ),
            "current_partition_exact": (
                len(surviving_reference) + len(post_reference_active)
                == len(current_active)
            ),
            "no_untraced_reference_fingerprint": not reference_untraced,
            "union_equals_current_active": union == current_active,
            "pairwise_disjoint": not overlaps,
            "unknown_is_zero": not classes.get("UNKNOWN"),
        },
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Algèbre des ensembles de dette — état courant",
        "",
        "Les ensembles, pas les nombres. Chaque classe porte son cardinal et le",
        "digest de son ensemble d'empreintes ; leur union est exactement",
        "l'actif courant, sans recouvrement et sans inconnu.",
        "",
        "## Pourquoi la soustraction naïve échoue",
        "",
        f"`{payload['naive_subtraction']['expression']} = "
        f"{payload['naive_subtraction']['value']}` — et non "
        f"{payload['partition']['cardinality_equation'].split(' = ')[0]}.",
        "",
        payload["naive_subtraction"]["why"] + ".",
        "",
        f"Expression correcte : `{payload['naive_subtraction']['correct_expression']}`.",
        "",
        "## Ensembles",
        "",
        "| Ensemble | Cardinal | Digest |",
        "|---|---:|---|",
    ]
    for entry in payload["sets"]:
        lines.append(
            f"| `{entry['set']}` | {entry['cardinality']} | `{entry['set_digest'][:23]}…` |"
        )
    lines += [
        "",
        "## Partition de l'actif courant",
        "",
        f"`{payload['partition']['cardinality_equation']}`",
        "",
        "Les classes restent **distinctes** : fondre les treize résiduelles ou",
        "les extensions optionnelles TRIGO dans la classe A4 rendrait leur",
        "sunset inauditable.",
        "",
        "## Renommage de métrique",
        "",
        f"Le champ `resolved` de la baseline vaut "
        f"{payload['metric_renaming']['observed_cardinality']} : ce n'est **pas** "
        "`REFERENCE_BASELINE_RESOLVED` "
        f"({payload['metric_renaming']['decomposition']['RESOLVED_REFERENCE']}), "
        "mais `RESOLVED_ARCHIVE_ALL_GENERATIONS`. Le champ lui-même n'est pas",
        "renommé : aucune mise à jour de baseline n'est autorisée.",
        "",
        "## Ambiguïté d'ancre",
        "",
        payload["reference_baseline"]["anchor_ambiguity"] + ".",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_reconciliation()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)
    if args.check:
        if not OUTPUT_JSON.is_file() or OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            raise SystemExit("STALE: audit/DEBT_SET_ALGEBRA_RECONCILIATION_CURRENT.json")
        if not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            raise SystemExit("STALE: audit/DEBT_SET_ALGEBRA_RECONCILIATION_CURRENT.md")
        print(f"current: {payload['partition']['cardinality_equation']}")
        return 0
    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    print(f"wrote debt set algebra: {payload['partition']['cardinality_equation']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
