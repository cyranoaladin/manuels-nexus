#!/usr/bin/env python3
"""Dette de revue humaine du lot couple 1NSI (algorithmique).

Les deux chapitres d'algorithmique de Premiere NSI ont ete reconstruits apres
le retrait de 116 objets de mathematiques de Terminale qui y etaient loges. Ce
qui a ete ecrit a la place est verifie par execution -- chaque bloc Python
tourne, chaque assertion passe -- mais personne ne l'a relu.

Ce registre le declare. Il ne l'approuve pas.

Trois classes sont distinguees, et ne doivent jamais etre fondues :

`CREATED`
    objets neufs, qui n'ont jamais porte d'approbation ;

`REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED`
    objets qui avaient passe une verification machine avant leur reecriture.
    Cette preuve ne vaut pas approbation humaine et ne peut donc pas etre
    presentee comme une approbation devenue perimee ;

`REWRITTEN_STALE_APPROVAL`
    reserve aux objets pour lesquels une ancienne approbation humaine est
    reellement prouvee. Cette classe est vide dans le lot courant.

Les deux classes sont derivees de Git, par comparaison avec le SHA de
reference, jamais d'une liste ecrite a la main : une liste finit par mentir.
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
OUTPUT = ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json"
CHAPTERS = ("1NSI-ALGO-DICHO-GLOUTON-KNN", "1NSI-ALGO-PARCOURS-TRIS")

#: Etat de reference : le HEAD du dernier run complet vert, avant toute
#: intervention sur ces deux chapitres.
BASELINE_SHA = "52c061428f472f9926829d5c5a4e1c74c7392e58"

#: Seul le statut explicitement humain vaut approbation. `verified` designe une
#: verification machine dans ce depot et ne doit jamais etre promu par inference.
HUMAN_APPROVED_STATUSES = frozenset({"approved"})
MACHINE_VERIFIED_STATUSES = frozenset({"verified"})


def _inventory_module():
    spec = importlib.util.spec_from_file_location(
        "inventory_collection", ROOT / "scripts/inventory_collection.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", ROOT / "scripts/build_p0_content_clone_ledger.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout


def _baseline_text(relative: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_SHA}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _semantic_digest(clone: Any, text: str) -> str:
    body = clone.pedagogical_body(text)
    return clone.digest(clone.normalized_body(body))


#: Sous-dossiers que `NSI/scripts/verify_python.py` visite reellement. Un
#: objet situe hors de cette portee -- un QCM rendu en .tex, par exemple --
#: ne porte aucun bloc executable : son absence de recu est NORMALE et ne doit
#: pas etre comptee comme une lacune de preuve.
EXECUTABLE_SUBDIRS = frozenset(
    {
        "exercices",
        "corriges",
        "evaluations",
        "ece",
        "projet",
        "cours",
        "methodes",
        "remediation",
    }
)


def _execution_evidence(base: Path, path: Path, source_sha256: str) -> dict[str, Any]:
    executable_scope = path.parent.name in EXECUTABLE_SUBDIRS
    receipt_path = base / "validations" / f"{path.stem}.execution.json"
    if not executable_scope:
        # EXECUTION_NOT_APPLICABLE : l'objet ne porte aucun code. Ce n'est PAS
        # une lacune de preuve, et le confondre avec une ferait passer une
        # absence normale pour une dette.
        return {
            "executable_scope": False,
            "execution_applicability": "EXECUTION_NOT_APPLICABLE",
            "execution_state": "EXECUTION_NOT_APPLICABLE",
            "evidence_gap": False,
            "receipt_path": None,
            "receipt_sha256": None,
            "declared_source_path": None,
            "declared_source_sha256": None,
            "verdict": None,
            "binding_state": "NO_EXECUTABLE_CONTENT",
            "source_bound_current": False,
        }
    if not receipt_path.is_file():
        # EXECUTION_REQUIRED et recu absent : la seule vraie lacune.
        return {
            "executable_scope": True,
            "execution_applicability": "EXECUTION_REQUIRED",
            "execution_state": "EXECUTION_MISSING",
            "evidence_gap": True,
            "receipt_path": None,
            "receipt_sha256": None,
            "declared_source_path": None,
            "declared_source_sha256": None,
            "verdict": None,
            "binding_state": "MISSING_RECEIPT",
            "source_bound_current": False,
        }
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    relative = str(path.relative_to(ROOT))
    declared_path = receipt.get("source_path")
    declared_sha = receipt.get("source_sha256")
    verdict = receipt.get("verdict")
    source_bound = (
        declared_path == relative
        and declared_sha == source_sha256
        and verdict == "pass"
    )
    return {
        "executable_scope": True,
        "execution_applicability": "EXECUTION_REQUIRED",
        "execution_state": "EXECUTION_PRESENT",
        # Le recu existe et conclut : la lacune de PREUVE est fermee. Qu'il
        # soit lie ou non a la source courante est une autre question, portee
        # par `binding_state`, et il ne faut pas confondre les deux.
        "evidence_gap": False,
        "receipt_path": str(receipt_path.relative_to(ROOT)),
        "receipt_sha256": "sha256:"
        + hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "declared_source_path": declared_path,
        "declared_source_sha256": declared_sha,
        "verdict": verdict,
        "binding_state": (
            "CURRENT_SOURCE_BOUND" if source_bound else "UNBOUND_RECEIPT"
        ),
        "source_bound_current": source_bound,
    }


def _machine_verification(entries: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = json.loads(
        (ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text(encoding="utf-8")
    )
    clone = json.loads(
        (ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text(encoding="utf-8")
    )
    cross = json.loads(
        (ROOT / "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json").read_text(
            encoding="utf-8"
        )
    )
    prefixes = tuple(f"NSI/chapitres/{chapter}/" for chapter in CHAPTERS)
    invalid = [
        path
        for path in clone["objects_on_invalid_credit"]
        if str(path).startswith(prefixes)
    ]
    indeterminate = [
        path
        for path in clone["objects_with_indeterminate_credit"]
        if str(path).startswith(prefixes)
    ]
    coverage_rows = [
        row for row in coverage["rows"] if row.get("chapter") in CHAPTERS
    ]
    semantic_unknown = sum(
        row.get("state") == "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"
        for row in coverage_rows
    )
    in_scope = [
        entry
        for entry in entries
        if entry["execution_evidence"]["execution_applicability"]
        == "EXECUTION_REQUIRED"
    ]
    found_receipts = sum(
        entry["execution_evidence"]["execution_state"] == "EXECUTION_PRESENT"
        for entry in in_scope
    )
    source_bound = sum(
        entry["execution_evidence"]["source_bound_current"] for entry in entries
    )
    # Un objet hors portee executable n'a pas de recu a manquer : le compter
    # ferait passer une absence normale pour une lacune de preuve.
    # Une lacune de preuve n'existe que si l'execution est REQUISE et le recu
    # absent. Tout le reste est une absence normale.
    missing_receipts = sum(
        entry["execution_evidence"]["evidence_gap"] for entry in entries
    )
    assert missing_receipts == len(in_scope) - found_receipts
    return {
        "execution_evidence": {
            "objects": len(entries),
            "objects_in_executable_scope": len(in_scope),
            "receipts_found": found_receipts,
            "missing_receipts": missing_receipts,
            "source_bound_current": source_bound,
            "status": (
                "COMPLETE"
                if source_bound == len(in_scope)
                else "UNBOUND_RECEIPTS"
                if missing_receipts == 0
                else "INCOMPLETE_RECEIPTS"
            ),
        },
        "clone_capacity_integrity": {
            "invalid_credit_objects": len(invalid),
            "indeterminate_credit_objects": len(indeterminate),
            "status": "COMPLETE" if not invalid and not indeterminate else "GAP",
        },
        "cross_discipline": {
            "condemned": int(cross["condemned_count"]),
            "unknown": int(cross["unknown"]),
            "status": (
                "COMPLETE"
                if cross["condemned_count"] == 0 and cross["unknown"] == 0
                else "GAP"
            ),
        },
        "role_coverage": {
            "cells": len(coverage_rows),
            "semantic_unknown": semantic_unknown,
            "status": "COMPLETE" if semantic_unknown == 0 else "UNVALIDATED",
        },
        "note": (
            "aucune de ces verifications ne remplace la lecture par un "
            "professeur de la discipline"
        ),
    }


def build_ledger() -> dict[str, Any]:
    clone = _clone_module()
    inventory_module = _inventory_module()
    inventory = json.loads(
        (ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8")
    )
    # Les empreintes sont RECALCULEES par la fonction de l'inventaire, jamais
    # recopiees : une empreinte ecrite en dur finit par ne plus designer
    # l'objet qu'elle nomme.
    fingerprint_by_path: dict[str, str] = {}
    for anomaly in inventory["anomalies"]["blocking_statuses"]:
        fingerprint_by_path[str(anomaly.get("path"))] = (
            inventory_module._anomaly_fingerprint(
                anomaly, category="blocking_statuses", repository_root=ROOT
            )
        )
    entries: list[dict[str, Any]] = []
    for chapter in CHAPTERS:
        base = ROOT / "NSI/chapitres" / chapter
        for path in sorted(base.rglob("*.tex")):
            relative = str(path.relative_to(ROOT))
            current = path.read_text(encoding="utf-8", errors="replace")
            meta = clone.read_meta(current)
            status = str(meta.get("status") or "")
            previous = _baseline_text(relative)

            if previous is None:
                origin, previous_status = "CREATED", None
            elif previous == current:
                continue  # inchange : sa dette eventuelle est ailleurs
            else:
                previous_status = str(
                    clone.read_meta(previous).get("status") or ""
                )
                if _semantic_digest(clone, previous) == _semantic_digest(
                    clone, current
                ):
                    # La source a bouge, le corps pedagogique non : correction
                    # d'identite ou declaration ajoutee. Le presenter comme
                    # une reecriture ferait relire un contenu inchange et
                    # noierait la dette reelle.
                    origin = "DECLARATION_CHANGED_SEMANTICS_IDENTICAL"
                elif previous_status in HUMAN_APPROVED_STATUSES:
                    origin = "REWRITTEN_STALE_APPROVAL"
                elif previous_status in MACHINE_VERIFIED_STATUSES:
                    origin = "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED"
                else:
                    origin = "REWRITTEN"

            fingerprint = fingerprint_by_path.get(relative)
            if fingerprint is None:
                # Objet sans anomalie bloquante : rien a declarer ici.
                continue
            source_sha256 = _sha256_text(current)
            execution_evidence = _execution_evidence(base, path, source_sha256)
            entries.append(
                {
                    "fingerprint": fingerprint,
                    "object_id": meta.get("id") or path.stem,
                    "path": relative,
                    "chapter": chapter,
                    "role": path.parent.name,
                    "status": status,
                    "origin": origin,
                    "status_before_rewrite": previous_status,
                    "source_sha256": source_sha256,
                    "source_sha256_before": (
                        _sha256_text(previous) if previous is not None else None
                    ),
                    "semantic_digest_current": _semantic_digest(clone, current),
                    "semantic_digest_before": (
                        _semantic_digest(clone, previous)
                        if previous is not None
                        else None
                    ),
                    "human_approval_evidence": previous_status
                    in HUMAN_APPROVED_STATUSES,
                    "human_approval_invalidated_by_rewrite": origin
                    == "REWRITTEN_STALE_APPROVAL",
                    "execution_evidence": execution_evidence,
                    "machine_verified_by_execution": execution_evidence[
                        "source_bound_current"
                    ],
                    "policy_disposition": "open_debt",
                    "in_approved_baseline": False,
                    "human_review_required": True,
                    "release_blocking": True,
                    "release_acceptance": False,
                    "logical_owner": "direction_scientifique_programme",
                }
            )

    entries.sort(key=lambda row: row["path"])
    by_origin = collections.Counter(row["origin"] for row in entries)
    by_chapter = collections.Counter(row["chapter"] for row in entries)
    paths = sorted(row["path"] for row in entries)
    fingerprints = sorted(row["fingerprint"] for row in entries)
    if len(set(fingerprints)) != len(entries):
        raise ValueError("empreintes non univoques")
    return {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT",
        "schema_version": 1,
        "generated_by": "scripts/build_nsi_coupled_review_debt.py",
        "chapters": list(CHAPTERS),
        "baseline_sha": BASELINE_SHA,
        "count": len(entries),
        "counts_by_origin": dict(sorted(by_origin.items())),
        "counts_by_chapter": dict(sorted(by_chapter.items())),
        "human_review_required": True,
        "release_blocking": True,
        "release_acceptance": False,
        "in_approved_baseline": False,
        "is_baseline_qualification": False,
        "is_gate_exception": False,
        "semantics": (
            "Registre d'observation. Il n'inscrit rien dans la baseline "
            "approuvee, ne materialise aucune qualification, et ne doit rendre "
            "vert aucun gate. La fermeture doit venir du cycle de statut apres "
            "revue humaine."
        ),
        "why_created": (
            "Les deux chapitres d'algorithmique de Premiere NSI portaient 116 "
            "objets de mathematiques de Terminale, tous status approved. Le "
            "contenu ecrit a leur place n'a pas ete relu. Les recus historiques "
            "sans chemin ni digest source restent non lies : une execution non "
            "rattachee au source courant n'est pas une preuve machine current, "
            "et aucune preuve machine ne vaut validation par un professeur."
        ),
        "machine_verification_performed": _machine_verification(entries),
        "human_review_packets": {
            "EXPERT_NSI": "PENDING_UNASSIGNED",
            "EXPERT_PROGRAMME_PEDAGOGIE": "PENDING_UNASSIGNED",
        },
        "reviewers_must_be_distinct": True,
        "expected_gate_behaviour": {
            "check": "rouge sur ces objets",
            "validate-model": "rouge sur ces objets",
            "fail-on-new": "rouge sur ces objets",
            "release-strict": "rouge",
        },
        "fingerprint_set_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(fingerprints, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "paths_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(paths, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "entries": entries,
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    payload = build_ledger()
    rendered = render(payload)
    if arguments.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}")
            return 1
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: {payload['count']} objets, "
        f"{payload['counts_by_origin']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
