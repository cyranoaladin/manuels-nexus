#!/usr/bin/env python3
"""Dette de revue humaine du lot couple 1NSI (algorithmique).

Les deux chapitres d'algorithmique de Premiere NSI ont ete reconstruits apres
le retrait de 116 objets de mathematiques de Terminale qui y etaient loges.
La verification effective du remplacement depend des sources et des recus
courants ; aucune execution ni relecture n'est presumee.

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
        "inventory_collection", Path(__file__).with_name("inventory_collection.py")
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _clone_module():
    spec = importlib.util.spec_from_file_location(
        "p0_clone_ledger", Path(__file__).with_name("build_p0_content_clone_ledger.py")
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


# Use the canonical writer's actual discovery scope, never a copied list.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from NSI.scripts.verify_python import SUBDIRS  # noqa: E402
from scientific_receipt_binding import bind, usable  # noqa: E402

EXECUTABLE_SUBDIRS = frozenset(SUBDIRS)


def _execution_evidence(base: Path, path: Path, source_sha256: str) -> dict[str, Any]:
    source = path.read_bytes()
    current_sha = "sha256:" + hashlib.sha256(source).hexdigest()
    if source_sha256 != current_sha:
        raise ValueError(f"source changed before execution binding: {path}")
    text = source.decode("utf-8")
    executable_scope = path.parent.parent == base and path.parent.name in EXECUTABLE_SUBDIRS
    claims = any(marker in text for marker in (
        "% BEGIN-VERIFY", "% BEGIN-TRACE", "% PYTHON-SOURCE", r"\begin{python}",
        r"\lstinputlisting", r"\inputminted", r"\begin{minted}", r"\begin{lstlisting}"))
    receipt_path = base / "validations" / f"{path.stem}.execution.json"
    evidence = {
        "executable_scope": executable_scope,
        "execution_applicability": "EXECUTION_REQUIRED" if claims else "EXECUTION_NOT_APPLICABLE",
        "applicability_method": "CURRENT_SOURCE_EXECUTABLE_MARKERS_NOT_SCIENTIFIC_REVIEW",
        "execution_state": "EXECUTION_MISSING" if claims else "EXECUTION_NOT_APPLICABLE",
        "evidence_gap": claims,
        "receipt_path": None, "receipt_sha256": None, "declared_source_path": None,
        "declared_source_sha256": None, "verdict": None,
        "binding_state": "MISSING_RECEIPT", "source_bound_current": False,
        "execution_passed": False, "certifies_documentary_claims": False,
        "certifies_complete_program_correctness": False,
        "scientific_review_state": "NOT_EVALUATED_BY_EXECUTION",
    }
    if receipt_path.is_file():
        data = receipt_path.read_bytes()
        evidence.update(receipt_path=str(receipt_path.relative_to(ROOT)),
                        receipt_sha256="sha256:" + hashlib.sha256(data).hexdigest())
        try:
            receipt = json.loads(data)
            if not isinstance(receipt, dict):
                raise ValueError("receipt is not an object")
        except (ValueError, UnicodeError) as exc:
            evidence.update(binding_state="UNREADABLE_RECEIPT", error=str(exc))
        else:
            binding = bind(receipt, base, ROOT)
            identity_matches = (binding.get("source_path") == path.relative_to(ROOT).as_posix()
                                and binding.get("current_source_sha256") == current_sha)
            if binding["state"] == "CURRENT_BOUND" and not identity_matches:
                binding = {**binding, "state": "STALE", "reason": "RECEIPT_FOR_DIFFERENT_SOURCE"}
            source_bound = identity_matches and binding["state"] == "CURRENT_BOUND"
            passed = executable_scope and claims and usable(binding) and receipt.get("verdict") == "pass"
            evidence.update(declared_source_path=receipt.get("source_path"),
                            declared_source_sha256=receipt.get("source_sha256"), verdict=receipt.get("verdict"),
                            binding_state=binding["state"], binding=binding,
                            source_bound_current=source_bound, execution_passed=passed,
                            evidence_gap=claims and not passed)
        if claims:
            evidence["execution_state"] = "EXECUTION_PRESENT"
        if receipt_path.read_bytes() != data:
            raise ValueError(f"receipt changed during execution binding: {receipt_path}")
    if claims and not executable_scope:
        evidence["execution_state"] = "UNCHECKED_EXECUTABLE_SOURCE"
    if path.read_bytes() != source:
        raise ValueError(f"source changed during execution binding: {path}")
    return evidence


def _execution_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = [entry["execution_evidence"] for entry in entries]
    required = [row for row in evidence if row["execution_applicability"] == "EXECUTION_REQUIRED"]
    passed = sum(row["execution_passed"] for row in required)
    gaps = sum(row["evidence_gap"] for row in evidence)
    return {
        "objects": len(entries),
        "objects_in_executable_scope": sum(row["executable_scope"] for row in evidence),
        "objects_requiring_execution": len(required),
        "receipts_found": sum(row["receipt_path"] is not None for row in required),
        "missing_receipts": sum(row["receipt_path"] is None for row in required),
        "source_bound_current": sum(row["source_bound_current"] for row in evidence),
        "execution_passed": passed,
        "evidence_gaps": gaps,
        "unchecked_executable_sources": sum(row["execution_state"] == "UNCHECKED_EXECUTABLE_SOURCE" for row in required),
        "status": "COMPLETE" if not gaps else "INCOMPLETE_EXECUTION_EVIDENCE",
        "scope": "EXECUTABLE_CLAIMS_ONLY; independent reading and human approval remain separate",
        "certifies_documentary_claims": False,
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
    return {
        "execution_evidence": _execution_summary(entries),
        "clone_capacity_integrity": {
            "invalid_credit_objects": len(invalid),
            "indeterminate_credit_objects": len(indeterminate),
            "status": "HISTORICAL_NOT_RECHECKED", "current_credit": False,
            "source_path": "audit/P0_CONTENT_CLONE_LEDGER.json",
            "source_sha256": _sha256_text((ROOT / "audit/P0_CONTENT_CLONE_LEDGER.json").read_text()),
        },
        "cross_discipline": {
            "condemned": int(cross["condemned_count"]),
            "unknown": int(cross["unknown"]),
            "status": "HISTORICAL_NOT_RECHECKED", "current_credit": False,
            "source_path": "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json",
            "source_sha256": _sha256_text((ROOT / "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json").read_text()),
        },
        "role_coverage": {
            "cells": len(coverage_rows),
            "semantic_unknown": semantic_unknown,
            "status": "HISTORICAL_NOT_RECHECKED", "current_credit": False,
            "source_path": "audit/TRUE_PEDAGOGICAL_COVERAGE.json",
            "source_sha256": _sha256_text((ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json").read_text()),
        },
        "note": (
            "aucune de ces verifications ne remplace la lecture par un "
            "professeur de la discipline"
        ),
    }


def _deja_declares() -> frozenset[str]:
    """Empreintes deja portees par un autre registre de dette bloquante.

    La liste des registres est celle de `build_residual_true_new_forensics`,
    qui en est l'autorite : trois copies d'une meme liste finissent par
    diverger.
    """
    scripts = str(Path(__file__).resolve().parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    forensics = __import__("importlib").import_module(
        "build_residual_true_new_forensics"
    )
    empreintes: set[str] = set()
    # L'algebre historique declare deja la dette qui SURVIT a la ligne de
    # base sous une identite inchangee. Le lot couple existe pour declarer ce
    # que sa reconstruction a cree ou reecrit, pas pour redeclarer cette
    # dette-la : la revendiquer une seconde fois romprait la disjonction que
    # la partition exige.
    algebre = ROOT / "audit/CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json"
    if algebre.is_file():
        historique = json.loads(algebre.read_text(encoding="utf-8"))
        ensembles = historique["full_current_algebra"]["sets"]
        for classe in ("UNCHANGED", "APPROVED_TRANSITION_NEW", "TRUE_NEW"):
            for empreinte in ensembles.get(classe) or []:
                empreintes.add(str(empreinte))
    for relative in forensics.DECLARED_DEBT_LEDGERS:
        if Path(relative).name == OUTPUT.name:
            continue
        chemin = ROOT / relative
        if not chemin.is_file():
            continue
        charge = json.loads(chemin.read_text(encoding="utf-8"))
        for valeur in charge.values() if isinstance(charge, dict) else []:
            if not isinstance(valeur, list):
                continue
            for ligne in valeur:
                if isinstance(ligne, dict) and ligne.get("fingerprint"):
                    empreintes.add(str(ligne["fingerprint"]))
    return frozenset(empreintes)


def _reconcile_source_inventory(inventory: dict[str, Any]) -> tuple[Path, ...]:
    from build_p0_content_clone_ledger import read_meta
    actual = tuple(sorted(path for chapter in CHAPTERS
                          for path in (ROOT / "NSI/chapitres" / chapter).rglob("*.tex")
                          if path.read_text(encoding="utf-8").startswith("% META:")))
    rows = [obj for manual in inventory["manuals"].values()
            for chapter_id, chapter in manual["chapters"].items() if chapter_id in CHAPTERS
            for obj in chapter["objects"]]
    paths = [row["path"] for row in rows]
    if len(set(paths)) != len(paths) or set(paths) != {path.relative_to(ROOT).as_posix() for path in actual}:
        raise ValueError("coupled inventory source set differs from current chapter sources")
    for row in rows:
        if row["metadata"] != read_meta((ROOT / row["path"]).read_text(encoding="utf-8")):
            raise ValueError("coupled inventory source metadata changed")
    return actual


def _binding_inputs() -> dict[str, str | None]:
    from build_residual_true_new_forensics import DECLARED_DEBT_LEDGERS
    from NSI.scripts.execution_protocol import implementation_manifest
    paths = {path.relative_to(ROOT).as_posix() for chapter in CHAPTERS
             for path in (ROOT / "NSI/chapitres" / chapter).rglob("*")
             if path.is_file() and path.suffix in {".tex", ".py", ".json", ".yaml"}}
    paths.update(str(path) for path in DECLARED_DEBT_LEDGERS if path.name != OUTPUT.name)
    paths.update(implementation_manifest(ROOT))
    paths.update({"audit/CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
                  "audit/TRUE_PEDAGOGICAL_COVERAGE.json", "audit/P0_CONTENT_CLONE_LEDGER.json",
                  "audit/NSI_CROSS_DISCIPLINE_CONTENT_LEDGER.json",
                  "scripts/build_nsi_coupled_review_debt.py", "scripts/inventory_collection.py",
                  "scripts/build_p0_content_clone_ledger.py", "scripts/build_residual_true_new_forensics.py",
                  "scripts/scientific_receipt_binding.py"})
    return {path: "sha256:" + hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            if (ROOT / path).is_file() else None for path in sorted(paths)}


def build_ledger(*, inventory=None) -> dict[str, Any]:
    from build_current_review_index import observation
    from evidence_freshness import head_sha
    head = head_sha(ROOT)
    inputs_before = _binding_inputs()
    clone = _clone_module()
    inventory_module = _inventory_module()
    if inventory is None:
        inventory = inventory_module.build_inventory(ROOT, require_git_provenance=True)
    paths_before = _reconcile_source_inventory(inventory)
    declared_elsewhere = _deja_declares()
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
        for path in (path for path in paths_before if path.is_relative_to(base)):
            relative = str(path.relative_to(ROOT))
            source_bytes = path.read_bytes()
            current = source_bytes.decode("utf-8")
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
            if fingerprint in declared_elsewhere:
                # Un objet ecrit apres la decision qui a ouvert ce lot est
                # deja porte par le registre de sa propre campagne. Le
                # reclamer ici le compterait DEUX fois, et la partition de
                # dette -- qui exige des composants disjoints -- refuserait
                # de se construire. Le registre du lot couple ne revendique
                # donc que ce qu'aucun autre registre bloquant ne declare.
                continue
            source_sha256 = "sha256:" + hashlib.sha256(source_bytes).hexdigest()
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
                    "machine_verified_by_execution": execution_evidence["execution_passed"],
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
    verification = _machine_verification(entries)
    if (head_sha(ROOT) != head or _binding_inputs() != inputs_before
            or _reconcile_source_inventory(inventory) != paths_before):
        raise ValueError("coupled review observation inputs or HEAD changed")
    return {
        "artifact_type": "BLOCKING_REVIEW_DEBT_LEDGER",
        "ledger_id": "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT",
        "schema_version": 1,
        "generated_by": "scripts/build_nsi_coupled_review_debt.py",
        "chapters": list(CHAPTERS),
        "baseline_sha": BASELINE_SHA,
        "observation": observation(ROOT, head),
        "input_digests": inputs_before,
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
        "machine_verification_performed": verification,
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
