#!/usr/bin/env python3
"""Current content review view, independent of frozen human queues.

An independent review is evidence, never human approval. Each record in
INDEPENDENT_CONTENT_REVIEWS binds a source, its semantic digest and its chapter
dependencies. A changed binding keeps the object pending and records the refused
evidence. Historical queues and retired versions never add rows to the current
population. No source status or human receipt is modified by this producer.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_dimension_mathematics as mathematics  # noqa: E402
from build_new_authoring_review_debt import CORPORA, DECONTAMINATION_COMMIT  # noqa: E402
import build_p0_content_clone_ledger as clone  # noqa: E402
import evidence_freshness as freshness  # noqa: E402
import human_review_governance as governance  # noqa: E402

OUTPUT = "audit/CURRENT_REVIEW_INDEX.json"
REVIEW_LEDGER = "audit/INDEPENDENT_CONTENT_REVIEWS.json"
RETIRED_LEDGER = "audit/RETIRED_SYNTHETIC_OBJECT_IDS.json"
TAKEOVER_HEAD = "6da7f7637e34a3f7f4aba91eb765ee92ce7fc1d9"
CORE_DIMENSIONS = (
    "PROGRAMME_REVIEW", "SCIENTIFIC_REVIEW", "PEDAGOGICAL_REVIEW", "EDITORIAL_REVIEW",
)
OPTIONAL_DIMENSIONS = (
    "ORACLE_REVIEW", "CODE_EXECUTION_REVIEW", "CORRECTION_ALIGNMENT_REVIEW",
    "FIGURE_REVIEW", "DATA_REVIEW", "DOCUMENTARY_HISTORICAL_REVIEW",
)
DIMENSIONS = frozenset(CORE_DIMENSIONS + OPTIONAL_DIMENSIONS)


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def observation(root: Path, head: str | None):
    status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                            cwd=root, capture_output=True, text=True)
    lines = status.stdout.splitlines() if status.returncode == 0 else ["UNVERIFIABLE_NON_GIT_CONTEXT"]
    dirty = bool(lines)
    return {"head": head, "base_head": head, "worktree_status": lines, "worktree_dirty": dirty,
            "scope": "WORKTREE_BOUND_BY_INPUT_DIGESTS" if dirty else "HEAD_BOUND_BY_INPUT_DIGESTS"}


def _digest(payload: Any) -> str:
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def _confined(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"source outside repository: {relative}")
    return path


def _source_paths(root: Path) -> set[str]:
    """The same chapter source surface, independently checked against inventory."""
    return {
        path.relative_to(root).as_posix()
        for corpus in CORPORA for path in (root / corpus).rglob("*.tex")
        if path.read_text(encoding="utf-8").startswith("% META:")
    }


def _new_paths(root: Path) -> set[str]:
    # Compare the actual working source set with the historical tree. A source
    # does not become unreviewed only when someone commits it.
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", DECONTAMINATION_COMMIT,
         "--", *CORPORA],
        cwd=root, check=True, text=True, capture_output=True,
    )
    return _source_paths(root) - set(result.stdout.splitlines())


def _retired_versions(root: Path, read) -> list[dict[str, Any]]:
    payload = json.loads(read(RETIRED_LEDGER))
    rows = []
    for record in payload["retired"]:
        relative = record["path"]
        result = subprocess.run(
            ["git", "show", f"{DECONTAMINATION_COMMIT}^:{relative}"],
            cwd=root, capture_output=True, check=True,
        )
        text = result.stdout.decode("utf-8")
        if clone.read_meta(text).get("id") != record["object_id"]:
            raise ValueError(f"retired source identity differs: {relative}")
        rows.append({
            "object_id": record["object_id"], "path": relative,
            "source_sha256": sha256(result.stdout),
            "body_digest": clone.digest(clone.pedagogical_body(text)),
            "historical_commit": DECONTAMINATION_COMMIT + "^",
            "retirement_reason": record["retirement_reason"],
            "state": "HISTORICAL_INVALIDATED_BY_CONTAMINATION",
        })
    return rows


REFERENCES = re.compile(r"\\(inputminted|includegraphics|lstinputlisting|input|include)(?![A-Za-z])\*?(?:\s*\[[^\]]*\])*")
RESOURCE_SUFFIXES = {".tex", ".json", ".yaml", ".py", ".csv", ".sql", ".txt",
                     ".png", ".jpg", ".jpeg", ".svg", ".pdf", ".eps", ".lua"}


def _referenced_sources(root: Path, source: Path, manual_root: Path) -> set[Path]:
    text = re.sub(r"(?<!\\)%[^\n]*", "", source.read_text(encoding="utf-8"))
    result = set()
    for match in REFERENCES.finditer(text):
        tail = text[match.end():].lstrip()
        arguments = 2 if match.group(1) == "inputminted" else 1
        value = None
        for _ in range(arguments):
            argument = re.match(r"\{([^{}]+)\}", tail)
            if argument is None:
                raise ValueError(f"unresolved dependency argument: {source.relative_to(root)}")
            value = argument.group(1).strip()
            tail = tail[argument.end():].lstrip()
        if not value or "\\" in value or "://" in value:
            raise ValueError(f"unresolved local dependency: {value}")
        candidates = {(base / value).resolve() for base in (manual_root, source.parent, root)}
        candidates = {path for path in candidates if path.is_relative_to(root.resolve())}
        if not candidates:
            raise ValueError(f"dependency outside repository: {value}")
        if not Path(value).suffix:
            suffixes = (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps") if match.group(1) == "includegraphics" else (".tex",)
            candidates |= {path.with_suffix(suffix) for path in list(candidates) for suffix in suffixes}
        present = {path for path in candidates if path.is_file()}
        if len(present) != 1:
            raise ValueError(f"dependency missing or ambiguous: {value} in {source.relative_to(root)}")
        result.update(present)
    return result


def _dependencies(root: Path, chapter: dict[str, Any], manual: str | None = None) -> list[str]:
    from inventory_collection import MANUAL_EXPECTED_LEVELS
    contract = chapter["contract_path"]
    directory = _confined(root, contract).parent
    paths = {contract}
    for path in directory.rglob("*"):
        relative_parts = path.relative_to(directory).parts
        if (path.is_file() and "validations" not in relative_parts
                and "build" not in relative_parts
                and path.suffix in RESOURCE_SUFFIXES
                and path.name != "chapitre.tex"):
            paths.add(path.relative_to(root).as_posix())
    manual_root = directory.parents[1]
    pending = [root / path for path in paths if path.endswith(".tex")]
    inspected = set()
    while pending:
        source = pending.pop()
        if source in inspected:
            continue
        inspected.add(source)
        for dependency in _referenced_sources(root, source, manual_root):
            paths.add(dependency.relative_to(root).as_posix())
            if dependency.suffix == ".tex":
                pending.append(dependency)
    paths.update(p.relative_to(root).as_posix()
                 for p in (manual_root / "referentiel").glob("*.json"))
    registry = root / "docs/programmes/PROGRAMMES_2026_2027.yaml"
    if registry.is_file():
        paths.add(registry.relative_to(root).as_posix())
        programmes = yaml.safe_load(registry.read_text(encoding="utf-8"))
        matches = [m for m in programmes["manuels"] if m["manual_id"] == manual]
        if len(matches) != 1:
            raise ValueError(f"official programme manual missing or ambiguous: {manual}")
        official = programmes["sources"][matches[0]["programme_source"]]["fichier"]
        source = _confined(root, official)
        if not source.is_file():
            raise ValueError(f"official programme source missing: {official}")
        paths.add(source.relative_to(root).as_posix())
    coverage_manual = MANUAL_EXPECTED_LEVELS.get(manual, manual)
    for candidate in (
        root / "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml",
        root / "audit/official_program_coverage" / f"{coverage_manual}.json",
        manual_root / "scripts/assemble.py",
        manual_root / "scripts/assemble_manuel.py",
        manual_root / "scripts/common.py",
        manual_root / "scripts/verify_sympy.py",
        manual_root / "scripts/verify_python.py",
        manual_root / "scripts/execution_protocol.py",
    ):
        if candidate.is_file():
            paths.add(candidate.relative_to(root).as_posix())
    if manual in {"1NSI", "TNSI"}:
        sandbox = root / "scripts/review_1nsi_content.py"
        if sandbox.is_file():
            paths.add(sandbox.relative_to(root).as_posix())
    return sorted(paths)


def _required_dimensions(manual: str, meta: dict[str, Any], text: str, dependencies=()) -> list[str]:
    # Applicability of data claims needs review even when a dataset is embedded
    # in prose or TeX. Absence of a CSV reference is not a non-applicability proof.
    dimensions = [*CORE_DIMENSIONS, "DATA_REVIEW"]
    if mathematics.VERIFY_BLOCK.search(text):
        dimensions.append("ORACLE_REVIEW")
    code_tokens = ("\\begin{python}", "\\lstinputlisting", "\\begin{lstlisting}",
                   "\\begin{minted}", "\\inputminted", "\\begin{verbatim}")
    if (manual in {"1NSI", "TNSI"} or any(token in text for token in code_tokens)
            or any(Path(path).suffix == ".py" for path in dependencies)):
        # Chapter-level dependencies are intentionally conservative. A review
        # must examine applicability before declaring a source has no code.
        dimensions.append("CODE_EXECUTION_REVIEW")
    if meta.get("type_objet") in {"exercice", "corrige", "evaluation", "corrige_evaluation",
                                  "coup_de_pouce", "amenagee", "remediation"}:
        dimensions.append("CORRECTION_ALIGNMENT_REVIEW")
    if any(token in text for token in ("\\includegraphics", "\\begin{tikzpicture}")):
        dimensions.append("FIGURE_REVIEW")
    if meta.get("chapitre") == "TNSI-HISTOIRE-INFORMATIQUE":
        dimensions.append("DOCUMENTARY_HISTORICAL_REVIEW")
    return dimensions


def _review_evidence(records, objects):
    """Consume only this agent-evidence format; human receipts use their own gate."""
    rejected = []
    seen = set()
    by_key = {(row["path"], row["object_id"]): row for row in objects}
    for review in records:
        review_id = review.get("review_id")
        if not isinstance(review_id, str) or not review_id or review_id in seen:
            raise ValueError("missing or duplicate independent review id")
        seen.add(review_id)
        actor = review.get("reviewer") or {}
        if (actor.get("is_human") is not False
                or actor.get("independent_from_author") is not True
                or not actor.get("actor_id")
                or actor.get("author_actor_id") == actor.get("actor_id")):
            raise ValueError("independent agent review cannot claim human authority")
        dimensions = review.get("dimensions") or {}
        if not dimensions or set(dimensions) - DIMENSIONS:
            raise ValueError("unknown or missing independent review dimension")
        for dimension, verdict in dimensions.items():
            if verdict.get("state") not in {"VALIDATED_BY_EVIDENCE", "PENDING"}:
                raise ValueError(f"invalid independent review state: {dimension}")
            if not isinstance(verdict.get("rationale"), str) or not verdict["rationale"].strip():
                raise ValueError(f"missing independent review rationale: {dimension}")
        row = by_key.get((review.get("path"), review.get("object_id")))
        reason = None
        if row is None:
            reason = "HISTORICAL_OBJECT_VERSION"
        else:
            for field, label in (
                ("source_sha256", "STALE_SOURCE_DIGEST"),
                ("semantic_digest", "STALE_SEMANTIC_DIGEST"),
                ("dependency_digest", "STALE_DEPENDENCY_DIGEST"),
            ):
                if review.get(field) != row[field]:
                    reason = label
                    break
        if reason:
            rejected.append({"review_id": review_id, "path": review.get("path"),
                             "object_id": review.get("object_id"), "reason": reason})
            continue
        for dimension, verdict in dimensions.items():
            if row["reviews"].get(dimension, {}).get("review_id"):
                raise ValueError(f"ambiguous current reviews for {row['object_id']}/{dimension}")
            row["reviews"][dimension] = {**verdict, "review_id": review_id,
                                         "reviewer_actor_id": actor["actor_id"]}
    return rejected


def build(root: Path, inventory: dict[str, Any], *, reviews=None, retired=None,
          new_paths=None) -> dict[str, Any]:
    root = root.resolve()
    head_before = freshness.head_sha(root)
    inputs = {}

    def read(relative):
        data = _confined(root, relative).read_bytes()
        digest = sha256(data)
        if relative in inputs and inputs[relative] != digest:
            raise ValueError(f"input changed during read: {relative}")
        inputs[relative] = digest
        return data

    flat = [(manual, chapter_id, chapter, obj)
            for manual, value in sorted(inventory["manuals"].items())
            for chapter_id, chapter in sorted(value["chapters"].items())
            for obj in chapter["objects"]]
    paths = [obj["path"] for _, _, _, obj in flat]
    ids = [obj["id"] for _, _, _, obj in flat]
    if len(paths) != len(set(paths)) or len(ids) != len(set(ids)):
        raise ValueError("duplicate current inventory object")
    source_set = _source_paths(root)
    if source_set != set(paths):
        raise ValueError(f"inventory source set differs: missing={sorted(source_set-set(paths))[:5]}, "
                         f"absent={sorted(set(paths)-source_set)[:5]}")
    if reviews is None:
        ledger = json.loads(read(REVIEW_LEDGER))
        if (ledger.get("artifact_type") != "independent_content_reviews"
                or ledger.get("schema_version") != 1
                or ledger.get("approves_nothing") is not True):
            raise ValueError("independent ledger cannot grant approval")
        reviews = ledger["reviews"]
    retired = _retired_versions(root, read) if retired is None else retired
    new_paths = _new_paths(root) if new_paths is None else set(new_paths)
    historical_by_identity = defaultdict(list)
    historical_by_path = defaultdict(list)
    historical_by_id = defaultdict(list)
    for record in retired:
        historical_by_identity[(record["path"], record["object_id"])].append(record)
        historical_by_path[record["path"]].append(record)
        historical_by_id[record["object_id"]].append(record)
    dependencies = {}
    objects = []
    for manual, chapter_id, chapter, obj in flat:
        path = obj["path"]
        source = read(path)
        text = source.decode("utf-8")
        meta = clone.read_meta(text)
        if meta.get("id") != obj["id"] or meta != obj["metadata"]:
            raise ValueError(f"inventory source metadata differs: {path}")
        semantic = governance.META_RE.sub(
            lambda _: "% META: " + governance.canonical_json(governance._semantic_meta(meta)),
            governance.normalise_text(text), count=1,
        )
        body_digest = clone.digest(clone.pedagogical_body(text))
        prior_versions = historical_by_path[path] + historical_by_id[obj["id"]]
        if any(body_digest == record["body_digest"] for record in prior_versions):
            raise ValueError(f"retired content is current: {path}")
        if chapter_id not in dependencies:
            manifest = {p: sha256(read(p)) for p in _dependencies(root, chapter, manual)}
            dependencies[chapter_id] = {"digest": _digest(manifest), "sources": manifest,
                                         "contract_path": chapter["contract_path"], "manual": manual}
        classification = (
            "FORMAL_ORACLE_PRESENT" if mathematics.VERIFY_BLOCK.search(text)
            else mathematics.classify_not_applicable(manual, meta.get("type_objet"), text.split("\n", 1)[-1])
        )
        required = _required_dimensions(manual, meta, text, dependencies[chapter_id]["sources"])
        objects.append({
            "object_id": obj["id"], "path": path, "manual": manual,
            "chapter": chapter_id, "object_type": meta.get("type_objet"),
            "source_sha256": sha256(source), "semantic_digest": sha256(semantic.encode("utf-8")),
            "body_digest": body_digest, "dependency_digest": dependencies[chapter_id]["digest"],
            "new_authoring": path in new_paths, "mathematics_classification": classification,
            "source_status": meta.get("status"), "human_approval": "PENDING",
            "required_review_dimensions": required,
            "reviews": {name: {"state": "PENDING"} for name in required},
            "historical_versions": historical_by_identity.get((path, obj["id"]), []),
        })
    rejected = _review_evidence(reviews, objects)
    for row in objects:
        row["review_state"] = (
            "VALIDATED_BY_EVIDENCE" if all(row["reviews"][d]["state"] == "VALIDATED_BY_EVIDENCE"
                                           for d in row["required_review_dimensions"])
            else "PENDING"
        )
    # Frozen queues remain references, not an alternative current population.
    historical_queues = []
    for relative in ("audit/HUMAN_REVIEW_QUEUE.json", "audit/CURRENT_REVIEW_DEBT_PARTITION.json",
                     "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json", "audit/QCM_REVIEW_CLOSURE.json",
                     "audit/1NSI_CONTENT_REVIEWS.json"):
        historical = historical_payload(root, relative)
        if historical is not None:
            historical_queues.append({"path": relative, "sha256": sha256(historical),
                                      "historical_commit": TAKEOVER_HEAD,
                                      "state": "NOT_CREDITED_WITHOUT_CURRENT_OBJECT_BINDING"})
    for relative in (
        "scripts/build_current_review_index.py", "scripts/build_new_authoring_review_debt.py",
        "scripts/human_review_governance.py", "scripts/build_p0_content_clone_ledger.py",
        "scripts/build_dimension_mathematics.py", "scripts/evidence_freshness.py",
    ):
        if (root / relative).is_file():
            read(relative)
    _assert_dependency_sets(root, dependencies)
    for relative, digest in inputs.items():
        path = _confined(root, relative)
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValueError(f"input changed during read: {relative}")
    if _source_paths(root) != source_set or freshness.head_sha(root) != head_before:
        raise ValueError("source set or HEAD changed during read")
    nonformal = [r for r in objects if r["mathematics_classification"] == "MATHEMATICAL_NON_FORMALIZABLE"]
    return {
        "artifact_type": "current_review_index", "schema_version": 1,
        "generated_by": "scripts/build_current_review_index.py", "approves_nothing": True,
        "observation": observation(root, head_before),
        "source_set_digest": _digest({r["path"]: r["source_sha256"] for r in objects}),
        "review_index_digest": _digest(objects), "input_digests": dict(sorted(inputs.items())),
        "chapter_dependencies": dependencies, "historical_queues": historical_queues,
        "retired_versions": retired, "rejected_review_evidence": rejected,
        "objects": objects,
        "summary": {
            "CURRENT_REVIEW_INDEX_TOTAL": len(objects), "CURRENT_REVIEW_INDEX_DUPLICATES": 0,
            "CURRENT_REVIEW_INDEX_MISSING_CURRENT_OBJECTS": 0,
            "CURRENT_REVIEW_INDEX_RETIRED_OBJECTS": 0, "CURRENT_REVIEW_INDEX_STALE_EVIDENCE": 0,
            "REJECTED_STALE_REVIEW_EVIDENCE": sum(r["reason"].startswith("STALE_") for r in rejected),
            "NEW_AUTHORING_OBJECTS": sum(r["new_authoring"] for r in objects),
            "NEW_AUTHORING_REVIEW_PENDING": sum(r["new_authoring"] and r["review_state"] == "PENDING" for r in objects),
            "MATHEMATICAL_NON_FORMALIZABLE_TOTAL": len(nonformal),
            "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING": sum(r["reviews"]["SCIENTIFIC_REVIEW"]["state"] == "PENDING" for r in nonformal),
            "REVIEW_STATES": dict(Counter(r["review_state"] for r in objects)),
            "HUMAN_APPROVAL_PENDING": len(objects), "UNJUSTIFIED_REVIEW_INHERITANCE": 0,
        },
    }



def historical_payload(root: Path, relative: str) -> bytes | None:
    """Read the immutable takeover snapshot, never a cyclic consumer output."""
    result = subprocess.run(["git", "show", f"{TAKEOVER_HEAD}:{relative}"],
                            cwd=root, capture_output=True)
    if result.returncode:
        # Tiny non-Git fixtures have no historical corpus. A real repository
        # must retain its declared takeover snapshot and its referenced file.
        if freshness.head_sha(root) is not None:
            raise ValueError(f"historical evidence unavailable: {relative}")
        return None
    return result.stdout


def _assert_dependency_sets(root: Path, dependencies):
    for record in dependencies.values():
        paths = _dependencies(root, {"contract_path": record["contract_path"]}, record["manual"])
        if set(paths) != set(record["sources"]):
            raise ValueError(f"dependency set changed: {record['contract_path']}")


def assert_current(root: Path, index: dict[str, Any]) -> None:
    """Guard the in-memory result again after a consumer's additional reads."""
    for relative, digest in index["input_digests"].items():
        path = _confined(root, relative)
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValueError(f"index input changed: {relative}")
    _assert_dependency_sets(root, index["chapter_dependencies"])
    if _source_paths(root) != {row["path"] for row in index["objects"]}:
        raise ValueError("index source set changed")
    if freshness.head_sha(root) != index["observation"]["head"]:
        raise ValueError("index observation HEAD changed")


def build_fresh(root: Path = ROOT, inventory=None):
    """Consumers compute the current view; a deposited JSON is not an oracle."""
    if inventory is None:
        from inventory_collection import build_inventory
        inventory = build_inventory(root, require_git_provenance=True)
    return build(root, inventory)


def binding(index):
    """Stable content binding; observation HEAD is carried by the index itself."""
    return {"source_set_digest": index["source_set_digest"],
            "review_index_digest": index["review_index_digest"],
            "input_digest": _digest(index["input_digests"])}


def comparable(payload):
    return {key: value for key, value in payload.items() if key != "observation"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    from inventory_collection import build_inventory

    payload = build(ROOT, build_inventory(ROOT, require_git_provenance=True))
    target = ROOT / OUTPUT
    if args.check:
        stored = json.loads(target.read_text()) if target.is_file() else {}
        if comparable(stored) != comparable(payload):
            print("CURRENT_REVIEW_INDEX: STALE")
            return 1
        print("CURRENT_REVIEW_INDEX: CURRENT_BY_INPUT_DIGEST", payload["observation"])
        return 0
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as out:
        out.write(rendered)
        temporary = out.name
    os.replace(temporary, target)
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
