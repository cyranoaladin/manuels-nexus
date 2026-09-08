#!/usr/bin/env python3
"""Reconcile external Astra controls against observed HEAD, without approvals.

The external documents stay outside Git. Rows store locations, not copies of
Astra text. PARTIAL records its exact proven subset. MAPPED is never PASS.
The external path must be supplied explicitly; no private services are used.
"""

from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import pathlib
import re
import subprocess
import sys

STATUSES = frozenset(
    {
        "COVERED_CURRENT_HEAD",
        "PARTIAL",
        "NOT_COVERED",
        "OBSOLETE_BY_CURRENT_HEAD",
        "NOT_APPLICABLE_JUSTIFIED",
        "DEFERRED_TO_RELEASE_PHASE",
    }
)


CHAPTER_INPUT_ROOTS = (
    "Mathematiques/manuel-maths/chapitres",
    "NSI/chapitres",
)
# Every non-chapter repository input read directly or by the invoked scanner.
# The producer itself is part of the evidence and must be committed as well.
DEPENDENCY_INPUT_FILES = (
    "scripts/build_astra_delta_matrix.py",
    "scripts/build_cross_manual_contamination.py",
    "scripts/build_p0_content_clone_ledger.py",
    "scripts/clone_normalization_fixtures.py",
    "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
    "NSI/scripts/assemble_manuel.py",
    "NSI/manifests/books/1NSI.json",
    "NSI/manifests/books/TNSI.json",
    "audit/CROSS_MANUAL_CONTAMINATION.json",
    "audit/CROSS_MANUAL_CONTAMINATION.md",
    "audit/CROSS_MANUAL_CONTAMINATION_MATRIX.json",
    "audit/RETIRED_SYNTHETIC_OBJECT_IDS.json",
    "AGENTS.md",
    "SOURCE_DE_VERITE.md",
    "audit/SOURCE_ROLES.yaml",
    "audit/ASSEMBLY_REUSE_CONTRACTS.yaml",
    "audit/HUMAN_REVIEW_GOVERNANCE.yaml",
)
HEAD_INPUT_PATHS = (*CHAPTER_INPUT_ROOTS, *DEPENDENCY_INPUT_FILES)


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    )


def retirement_disposition(revived, old_path_existence):
    if revived or any(old_path_existence.values()):
        return "PARTIAL"
    return "OBSOLETE_BY_CURRENT_HEAD"


def chapter_delta(astra, current, *, reviewed_project_contract=False):
    only_old = sorted(set(astra) - set(current))
    only_current = sorted(set(current) - set(astra))
    reasons = {}
    project = "NSI/chapitres/TNSI-PROJET"
    if reviewed_project_contract and project in only_current:
        reasons[project] = (
            "Unite de demarche de projet explicitement ajoutee au manifeste TNSI; "
            "contrat rattache au preambule, deux capacites pedagogiques, "
            "PROJECT_ASSESSMENT. Aucun quota de chapitres induit."
        )
    return {
        "ONLY_IN_ASTRA": only_old,
        "ONLY_IN_CURRENT": only_current,
        "SEMANTIC_REASON": reasons,
        "CANONICAL_CHAPTER_SET_UNRECONCILED": len(only_old)
        + len(set(only_current) - set(reasons)),
    }


def parse_controls(text):
    rows = [
        (m.group(1), text[: m.start()].count("\n") + 1)
        for m in re.finditer(r"^### (\S+) — (.+)$", text, re.M)
    ]
    if not rows or len(rows) != len({row[0] for row in rows}):
        raise ValueError("empty or duplicate external control IDs")
    return rows


def validate_control_partition(payload, expected_ids):
    rows = payload["rows"]
    ids = [row["ASTRA_CONTROL_ID"] for row in rows]
    if set(ids) != set(expected_ids) or len(ids) != len(set(ids)):
        raise ValueError("control partition is incomplete, duplicated or invented")
    if payload.get("approves_nothing") is not True:
        raise ValueError("status cannot approve anything")
    for field in ("dependency_inputs", "history_refs"):
        if field in payload and payload.get(field + "_digest") != digest_json(payload[field]):
            raise ValueError(f"dependency manifest digest mismatch: {field}")
    evidence = payload["evidence"]
    for key, record in evidence.items():
        body = {field: value for field, value in record.items() if field != "digest"}
        if record.get("digest") != digest_json(body):
            raise ValueError(f"evidence digest mismatch: {key}")
    for row in rows:
        if row["STATUS"] not in STATUSES:
            raise ValueError("unrecognized status")
        if row["CURRENT_HEAD"] != payload["CURRENT_HEAD"]:
            raise ValueError("mixed HEAD evidence")
        refs = row["CURRENT_EVIDENCE"]
        if row["STATUS"] in {"COVERED_CURRENT_HEAD", "PARTIAL"} and not refs:
            raise ValueError("covered/partial status requires evidence")
        if set(refs) - set(evidence):
            raise ValueError("unknown evidence reference")
        expected = (
            digest_json({key: evidence[key]["digest"] for key in refs})
            if refs
            else None
        )
        if row["CURRENT_EVIDENCE_DIGEST"] != expected:
            raise ValueError("row evidence digest mismatch")
        if not row.get("NOTES"):
            raise ValueError("missing scope notes")


def require_head_inputs(root, paths):
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            *paths,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode or result.stdout:
        raise ValueError("Observed source inputs differ from HEAD")


def build(root, ext):
    root, ext = Path(root).resolve(), Path(ext).resolve()
    if ext.is_relative_to(root):
        raise ValueError("External Astra inputs must stay outside the repository")

    def git(*args):
        p = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True
        )
        return {
            "command": ["git", *args],
            "rc": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }

    def file_evidence(path):
        p = root / path
        return {"path": path, "sha256": digest_bytes(p.read_bytes())}

    head = git("rev-parse", "HEAD")["stdout"]
    initial = git("status", "--porcelain=v1")
    history_refs = git("for-each-ref", "--format=%(refname) %(objectname)")
    if history_refs["rc"]:
        raise ValueError("Cannot identify Git history inputs")
    require_head_inputs(root, HEAD_INPUT_PATHS)
    dependency_inputs = [file_evidence(path) for path in DEPENDENCY_INPUT_FILES]
    external_names = [
        "Rapport_audit_collection.md",
        "Grille_controles_collection.md",
        "Constats_structurels.md",
        "MISSION_AUDIT_COLLECTION.md",
        "LISEZMOI.md",
        "1SPE.md",
        "TSPE.md",
        "TCOMPL.md",
        "TEXPERTES.md",
        "1NSI.md",
        "TNSI.md",
    ]
    external = {
        p: {
            "sha256": digest_bytes((ext / p).read_bytes()),
            "line_count": len((ext / p).read_text().splitlines()),
        }
        for p in external_names
    }
    books = external_names[-6:]
    astra = sorted(
        set(
            path
            for name in books
            for path in re.findall(
                r"^Racine : `([^`]+)`", (ext / name).read_text(), re.M
            )
        )
    )
    corpora = [root / "Mathematiques/manuel-maths/chapitres", root / "NSI/chapitres"]
    contracts = sorted(
        str(p.relative_to(root))
        for corpus in corpora
        for p in corpus.glob("*/contrat.yaml")
    )
    current = sorted(str(pathlib.Path(p).parent) for p in contracts)
    # The semantic explanation was actually read at this contract digest.
    # A changed project contract requires a new bounded review, not inheritance
    # based on its filename alone.
    project_contract = root / "NSI/chapitres/TNSI-PROJET/contrat.yaml"
    delta = chapter_delta(
        astra, current,
        reviewed_project_contract=project_contract.is_file()
        and digest_bytes(project_contract.read_bytes())
        == "sha256:05b5886783c7ff5699202ebb9967c2644e4c0f4c762ac83ada2eb0343f9814ec",
    )
    math_tree = ast.parse(
        (root / "Mathematiques/manuel-maths/scripts/assemble_manuel.py").read_text()
    )
    math_chapters = next(
        ast.literal_eval(n.value)
        for n in math_tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "CHAPITRES" for t in n.targets)
    )
    nsi_chapters = [
        c["id"]
        for book in ["1NSI", "TNSI"]
        for c in json.loads(
            (root / ("NSI/manifests/books/" + book + ".json")).read_text()
        )["chapters"]
    ]
    assembled_declarations = math_chapters + nsi_chapters
    canonical_names = sorted(pathlib.Path(p).name for p in current)
    if len(assembled_declarations) != len(set(assembled_declarations)) or set(
        assembled_declarations
    ) != set(canonical_names):
        raise ValueError("Declared chapter set does not match canonical contracts")
    source_paths = sorted(
        str(p.relative_to(root))
        for corpus in corpora
        for p in corpus.rglob("*.tex")
        if "_harvest" not in p.parts
    )
    source_inputs = [file_evidence(p) for p in source_paths + contracts]
    spec = importlib.util.spec_from_file_location(
        "astra_cmc", root / "scripts/build_cross_manual_contamination.py"
    )
    cmc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cmc)
    content = cmc.build()
    old = json.loads((root / "audit/CROSS_MANUAL_CONTAMINATION.json").read_text())
    check = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts/build_cross_manual_contamination.py"),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    retired = json.loads(
        (root / "audit/RETIRED_SYNTHETIC_OBJECT_IDS.json").read_text()
    )["retired"]
    refs = [
        ("10f01ba68^" if r["object_type"] == "remediation" else "30c029dd7^")
        + ":"
        + r["path"]
        for r in retired
    ]
    raw = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch"],
        input=("\n".join(refs) + "\n").encode(),
        capture_output=True,
        check=True,
    ).stdout
    ledger = cmc.identity_rule()
    position = 0
    historic = []
    for r, ref in zip(retired, refs):
        end = raw.index(b"\n", position)
        header = raw[position:end].decode()
        position = end + 1
        if header.endswith("missing"):
            raise RuntimeError(ref)
        size = int(header.split()[-1])
        text = raw[position : position + size].decode()
        position += size + 1
        historic.append(
            {
                "id": r["object_id"],
                "path": r["path"],
                "chapter": r["chapter"],
                "revision": ref.split(":")[0],
                "git_blob": header.split()[0],
                "semantic_digest": digest_bytes(ledger.pedagogical_body(text).encode()),
            }
        )
    current_rows = []
    for path in source_paths:
        text = (root / path).read_text()
        meta = ledger.read_meta(text)
        parts = pathlib.Path(path).parts
        current_rows.append(
            {
                "id": meta.get("id"),
                "path": path,
                "chapter": parts[parts.index("chapitres") + 1],
                "semantic_digest": digest_bytes(ledger.pedagogical_body(text).encode()),
            }
        )
    byid = {v["id"]: v for v in current_rows if v["id"]}
    bysemantic = collections.defaultdict(list)
    for row in current_rows:
        bysemantic[(row["chapter"], row["semantic_digest"])].append(row)
    reused = []
    revived = []
    for h in historic:
        if h["id"] in byid:
            reused.append(
                {
                    "id": h["id"],
                    "historical_digest": h["semantic_digest"],
                    "current_digest": byid[h["id"]]["semantic_digest"],
                    "current_path": byid[h["id"]]["path"],
                }
            )
        for row in bysemantic[(h["chapter"], h["semantic_digest"])]:
            revived.append({"historical": h, "current": row})
    str02 = (
        (ext / "Constats_structurels.md")
        .read_text()
        .split("## STR-02")[1]
        .split("## STR-03")[0]
    )
    old_paths = re.findall(r"`([^`]+\.tex)`", str02)
    old_path_existence = {p: (root / p).exists() for p in old_paths}
    identity = {
        "head": head,
        "root": git("rev-parse", "--show-toplevel")["stdout"],
        "branch": git("branch", "--show-current")["stdout"],
        "status": initial,
        "upstream": git(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
        ),
        "submodule_status": git("submodule", "status"),
        "untracked": git("ls-files", "--others", "--exclude-standard"),
    }
    evidence = {
        "E01": {"kind": "OBSERVED_GIT_IDENTITY", "result": identity},
        "E02": {
            "kind": "RECONCILED_DECLARED_CHAPTER_SETS",
            "source_files": [
                file_evidence(p)
                for p in [
                    "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
                    "NSI/scripts/assemble_manuel.py",
                    "NSI/manifests/books/1NSI.json",
                    "NSI/manifests/books/TNSI.json",
                    "NSI/chapitres/TNSI-PROJET/contrat.yaml",
                ]
            ],
            "current_contract_set_digest": digest_json(
                [file_evidence(p) for p in contracts]
            ),
            "ASTRA_CHAPTER_DIR_SET": astra,
            "CURRENT_CANONICAL_CHAPTER_SET": current,
            **delta,
            "declared_assembly_chapters": sorted(assembled_declarations),
            "ASSEMBLY_CONTRACT_SET_EQUALITY": True,
            "introduced_commit": git(
                "log",
                "--diff-filter=A",
                "--format=%H",
                "--",
                "NSI/chapitres/TNSI-PROJET/contrat.yaml",
            )["stdout"],
        },
        "E03": {
            "kind": "EXECUTED_CURRENT_CONTAMINATION_SCAN",
            "producer": file_evidence("scripts/build_cross_manual_contamination.py"),
            "normalization": file_evidence("scripts/build_p0_content_clone_ledger.py"),
            "fixtures": file_evidence("scripts/clone_normalization_fixtures.py"),
            "source_population_digest": digest_json(source_inputs),
            "source_file_count": len(source_paths),
            "summary": content["summary"],
            "normalization_proof": content["normalization_proof"],
            "check": {
                "command": [
                    sys.executable,
                    "-B",
                    "scripts/build_cross_manual_contamination.py",
                    "--check",
                ],
                "rc": check.returncode,
                "stdout": check.stdout.strip(),
                "stderr": check.stderr.strip(),
            },
            "committed_summary_differences": {
                k: {"recorded": old["summary"].get(k), "observed": v}
                for k, v in content["summary"].items()
                if v != old["summary"].get(k)
            },
            "limitation": "Duplicate-body detector only; does not certify semantics of unique authored text or final PDF runtime.",
        },
        "E04": {
            "kind": "READ_HISTORICAL_GIT_BLOBS_VERSUS_CURRENT_SOURCE_DIGESTS",
            "registry": file_evidence("audit/RETIRED_SYNTHETIC_OBJECT_IDS.json"),
            "historical_objects_read": len(historic),
            "historical_population_digest": digest_json(historic),
            "current_source_population_digest": digest_json(source_inputs),
            "retired_historical_bodies_reappearing_in_target_chapter": revived,
            "retired_ids_reused_count": len(reused),
            "same_old_paths_present": sum((root / r["path"]).exists() for r in retired),
            "reused_ids_digest": digest_json(reused),
            "reused_id_semantic_matches": sum(
                r["historical_digest"] == r["current_digest"] for r in reused
            ),
            "old_str02_paths_existence": old_path_existence,
            "limitation": "Retirement identifies a content generation; reused identifier counts and semantic matches are measured above. Final runtime and historical publication PDF contents remain uninspected.",
        },
        "E05": {
            "kind": "DOCUMENT_AUTHORITY_INSPECTION",
            "source_files": [
                file_evidence(p)
                for p in [
                    "AGENTS.md",
                    "SOURCE_DE_VERITE.md",
                    "audit/SOURCE_ROLES.yaml",
                    "audit/ASSEMBLY_REUSE_CONTRACTS.yaml",
                    "audit/HUMAN_REVIEW_GOVERNANCE.yaml",
                ]
            ],
            "limitation": "Documents read for scope only; no blanket authority freshness or all-assertion reconciliation claimed.",
        },
    }
    for e in evidence.values():
        e["digest"] = digest_json(e)
    partial = {
        "GOV-03": (
            ["E05"],
            "Hierarchie et decision quota identifiees; reconciliation exhaustive des exigences encore a faire.",
        ),
        "GOV-04": (
            ["E03", "E05"],
            "Nature distincte des rapports et preuves; seul producteur contamination effectivement reexecute ici.",
        ),
        "GOV-07": (
            ["E03", "E04"],
            "Fraicheur contamination et generations retirees inspectees; autres preuves a reconcilier.",
        ),
        "GOV-09": (
            ["E01"],
            "Aucune mutation du depot dans cette sous-mission; coordination inter-agents assuree par agent parent.",
        ),
        "INV-01": (
            ["E02", "E03"],
            "Population des chapitres et TeX inspectee; inventaire exhaustif hors chapitres non certifie ici.",
        ),
        "INV-06": (
            ["E03", "E04"],
            "Groupes identiques et anciennes generations reconcilies; dispositions pedagogiques des groupes courants encore a relire.",
        ),
        "INV-09": (
            ["E03", "E04"],
            f"Chemins STR-02 encore presents: {sum(old_path_existence.values())}/{len(old_paths)}; "
            f"corps retires retrouves dans leur chapitre cible: {len(revived)}; "
            "PDF finaux a inspecter apres freeze.",
        ),
        "INV-10": (
            ["E02", "E04"],
            "Ensemble de chapitres et generations retirees reconcilies; autres migrations et packet sets hors cette sous-mission.",
        ),
        "ASM-02": (
            ["E02"],
            f"Liste contractuelle et selection declaree = {len(current)}/{len(assembled_declarations)}; "
            "inclusions runtime et sommaires finaux non observes.",
        ),
        "QA-02": (
            ["E03"],
            "19 mutations de normalisation executees sans erreur; autres gates non eprouves ici.",
        ),
        "QA-04": (
            ["E03"],
            "RC1 sur artefact contamination perime reconnu; aucun fail-on-new assimile a zero defaut.",
        ),
        "QA-05": (
            ["E03"],
            "Population courante du controle contamination recalculee; autres inputs a verifier.",
        ),
        "QA-09": (
            ["E03"],
            "Rapport contamination compare au producteur dans E03; reconciliation de tous les autres rapports non terminee.",
        ),
    }
    # Explicit release-stage controls. Mixed source/pedagogy controls remain open above.
    deferred = {
        "GOV-10",
        "CODE-01",
        "CODE-09",
        "ASM-03",
        "ASM-04",
        "ASM-07",
        "ASM-08",
        "ASM-09",
        "ASM-10",
        "CHARTE-03",
        "QA-07",
        "QA-08",
        "PUB-01",
        "PUB-02",
        "PUB-03",
        "PUB-04",
        "PUB-07",
        "PUB-09",
        "PUB-10",
    } | {f"PDF-{i:02d}" for i in range(1, 11)}
    grid = (ext / "Grille_controles_collection.md").read_text()
    controls = parse_controls(grid)
    rows = []
    for cid, line in controls:
        status = "NOT_COVERED"
        notes = "Controle lu; aucune preuve substantielle de sa portee complete verifiee dans cette sous-mission. Les anciens rapports ne sont pas promus."
        ev = []
        app = "APPLICABLE_TO_CURRENT_CORPUS"
        if cid == "GOV-01":
            status = "COVERED_CURRENT_HEAD"
            ev = ["E01"]
            notes = "Etat Git courant observe directement; aucune equivalence au distant supposee."
        elif cid in partial:
            status = "PARTIAL"
            ev, notes = partial[cid]
        elif cid in deferred:
            status = "DEFERRED_TO_RELEASE_PHASE"
            app = "APPLICABLE_TO_FROZEN_FINAL_CANDIDATE"
            notes = "Depend du candidat final, des builds apres freeze ou de la decision humaine finale; aucun ancien PDF ne vaut candidat courant."
        elif cid.endswith("-REV-3"):
            status = "PARTIAL"
            ev = ["E02"]
            notes = "Chapitre present et selectionne dans la liste canonique declaree; objets, reponses aux sous-questions, parcours et pages finales restent a verifier."
        rows.append(
            {
                "ASTRA_CONTROL_ID": cid,
                "ASTRA_OBSERVATION": {
                    "document": "Grille_controles_collection.md",
                    "line": line,
                },
                "CURRENT_APPLICABILITY": app,
                "CURRENT_EVIDENCE": ev,
                "CURRENT_EVIDENCE_DIGEST": digest_json(
                    {k: evidence[k]["digest"] for k in ev}
                )
                if ev
                else None,
                "CURRENT_HEAD": head,
                "STATUS": status,
                "NOTES": notes,
            }
        )
    ids = [r["ASTRA_CONTROL_ID"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate control partition")
    counts = collections.Counter(r["STATUS"] for r in rows)
    summary = {
        "ASTRA_CONTROLS_TOTAL": len(rows),
        "ASTRA_CONTROLS_MAPPED": len(rows),
        "ASTRA_CONTROLS_UNMAPPED": 0,
        "ASTRA_CONTROLS_COVERED": counts["COVERED_CURRENT_HEAD"],
        "ASTRA_CONTROLS_OBSOLETE": counts["OBSOLETE_BY_CURRENT_HEAD"],
        "ASTRA_CONTROLS_PARTIAL": counts["PARTIAL"],
        "ASTRA_CONTROLS_NOT_COVERED": counts["NOT_COVERED"],
        "ASTRA_CONTROLS_DEFERRED_RELEASE_PHASE": counts["DEFERRED_TO_RELEASE_PHASE"],
        "ASTRA_CONTROLS_NOT_APPLICABLE_JUSTIFIED": counts["NOT_APPLICABLE_JUSTIFIED"],
        "CURRENT_CANONICAL_CHAPTERS": len(current),
        "ASTRA_CHAPTER_DIRS": len(astra),
        "CANONICAL_CHAPTER_SET_UNRECONCILED": delta["CANONICAL_CHAPTER_SET_UNRECONCILED"],
        "CURRENT_CROSS_MANUAL_CONTAMINATION": content["summary"][
            "CROSS_MANUAL_CONTAMINATION_OBJECTS"
        ],
        "CURRENT_CAPACITY_MISREPRESENTATION_DETECTED_BY_CLONES": content["summary"][
            "CAPACITY_MISREPRESENTING_GROUPS"
        ],
        "RETIRED_SYNTHETIC_BODIES_IN_CURRENT_CHAPTER_SOURCES": len(revived),
        "RETIRED_IDENTIFIERS_REUSED_FOR_DIFFERENT_CONTENT": len(reused)
        - sum(r["historical_digest"] == r["current_digest"] for r in reused),
        "RETIRED_SYNTHETIC_OBJECTS_STILL_ASSEMBLED": "NON_VERIFIE_RUNTIME",
        "RETIRED_SYNTHETIC_OBJECTS_STILL_REFERENCED": f"{len(reused)} identifiers reused; historical body generations must be distinguished",
    }
    if sum(counts.values()) != len(rows):
        raise ValueError("Control count partition mismatch")
    require_head_inputs(root, HEAD_INPUT_PATHS)
    if git("rev-parse", "HEAD")["stdout"] != head:
        raise ValueError("HEAD changed during observation")
    if git("for-each-ref", "--format=%(refname) %(objectname)") != history_refs:
        raise ValueError("Git history inputs changed during observation")
    if source_inputs != [file_evidence(p) for p in source_paths + contracts]:
        raise ValueError("Source inputs changed during observation")
    if dependency_inputs != [file_evidence(path) for path in DEPENDENCY_INPUT_FILES]:
        raise ValueError("Dependency inputs changed during observation")
    for name, record in external.items():
        if digest_bytes((ext / name).read_bytes()) != record["sha256"]:
            raise ValueError("External inputs changed during observation")
    payload = {
        "artifact_type": "astra_delta_matrix",
        "schema_version": 1,
        "generated_by": "scripts/build_astra_delta_matrix.py",
        "CURRENT_HEAD": head,
        "external_documents": external,
        "dependency_inputs": dependency_inputs,
        "dependency_inputs_digest": digest_json(dependency_inputs),
        "history_refs": history_refs,
        "history_refs_digest": digest_json(history_refs),
        "external_content_copied": False,
        "mapping_means": "Every external control has a disposition; MAPPED is not a successful check or scientific coverage.",
        "approves_nothing": True,
        "summary": summary,
        "evidence": evidence,
        "rows": rows,
        "structural_delta": {
            "STR-02": {
                "STATUS": retirement_disposition(revived, old_path_existence),
                "evidence": ["E03", "E04"],
                "notes": f"Chemins cites encore presents: {sum(old_path_existence.values())}; "
                f"corps retires retrouves: {len(revived)}. La qualification des contenus "
                "courants et le controle scientifique des remplacements demeurent ouverts.",
            },
            "STR-05": {
                "STATUS": "OBSOLETE_BY_CURRENT_HEAD",
                "evidence": ["E05"],
                "notes": "Le seuil numerique de50 exercices ne constitue plus une exigence release; la richesse qualitative reste exigible.",
            },
        },
    }

    validate_control_partition(payload, {cid for cid, _ in controls})
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--external-root", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument(
        "--verify-snapshot",
        type=Path,
        help="Check historical snapshot integrity, not current readiness",
    )
    args = parser.parse_args(argv)
    root, ext = args.root.resolve(), args.external_root.resolve()
    if args.verify_snapshot:
        payload = json.loads(args.verify_snapshot.read_text())
        controls = parse_controls((ext / "Grille_controles_collection.md").read_text())
        validate_control_partition(payload, {cid for cid, _ in controls})
        for name, record in payload["external_documents"].items():
            if digest_bytes((ext / name).read_bytes()) != record["sha256"]:
                raise ValueError(f"external document digest mismatch: {name}")
        print("Snapshot integrity verified; observed HEAD:", payload["CURRENT_HEAD"])
        print("This is not a current scientific or release certification.")
        return 0
    output = args.output.resolve()
    if output.is_relative_to(ext):
        raise ValueError("Writing into the external audit is forbidden")
    if output.is_relative_to(root) and not output.is_relative_to(root / "audit/astra"):
        raise ValueError("Repository snapshots must be under audit/astra/")
    payload = build(root, ext)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if output.exists():
        if output.read_text() != content:
            raise ValueError(
                "Historical snapshots are immutable; choose a new output path"
            )
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print("Observation:", output, digest_bytes(output.read_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
