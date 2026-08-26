#!/usr/bin/env python3
"""Freeze the exact 1SPE-SUITES human-review source candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "1SPE_SUITES_REVIEW_SOURCE_FREEZE.json"
SOURCE_SHA = "c667f12b1792f31981b6b5894c8c604df1bce634"
CHAPTER_PREFIX = "Mathematiques/manuel-maths/chapitres/1SPE-SUITES"
QCM_JSON = f"{CHAPTER_PREFIX}/qcm/1SPE-SUITES-QCM.json"
QCM_TEX = f"{CHAPTER_PREFIX}/qcm/1SPE-SUITES-QCM.tex"
CONTRACT = f"{CHAPTER_PREFIX}/contrat.yaml"
MANIFEST = "audit/BUILD_MANIFEST.json"
PROGRAMME_AUTHORITY_PATHS = (
    "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt",
    "audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml",
    "audit/official_program_contracts/1SPE.yaml",
    "audit/official_program_coverage/1SPE.json",
    "audit/OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.json",
    "audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.json",
    "audit/OFFICIAL_ATOMIZATION_SECOND_PASS.json",
)


def _git(*args: str, text: bool = True) -> str | bytes:
    run = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=text,
        capture_output=True,
        check=True,
    )
    return run.stdout


def _source_bytes(path: str) -> bytes:
    return _git("show", f"{SOURCE_SHA}:{path}", text=False)


def _blob_sha1(path: str) -> str:
    return str(_git("rev-parse", f"{SOURCE_SHA}:{path}")).strip()


def _last_commit(path: str) -> str:
    return str(
        _git("log", "-1", "--format=%H", SOURCE_SHA, "--", path)
    ).strip()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _binding(path: str) -> dict[str, str]:
    content = _source_bytes(path)
    return {
        "path": path,
        "source_commit_sha": _last_commit(path),
        "source_sha256": hashlib.sha256(content).hexdigest(),
        "git_blob_sha1": _blob_sha1(path),
    }


def _named_binding(path: str) -> dict[str, str]:
    binding = _binding(path)
    return {
        "path": binding["path"],
        "source_commit_sha": binding["source_commit_sha"],
        "sha256": binding["source_sha256"],
        "git_blob_sha1": binding["git_blob_sha1"],
    }


def _tree_paths() -> list[str]:
    output = str(_git("ls-tree", "-r", "--name-only", SOURCE_SHA, CHAPTER_PREFIX))
    return [line for line in output.splitlines() if line]


def _meta_object(path: str) -> dict[str, str]:
    content = _source_bytes(path)
    first_line = content.decode("utf-8").splitlines()[0]
    if not first_line.startswith("% META: "):
        raise ValueError(f"missing first-line META at {path}")
    meta = json.loads(first_line.removeprefix("% META: "))
    if meta.get("chapitre") != "1SPE-SUITES":
        raise ValueError(f"wrong chapter META at {path}")
    binding = _binding(path)
    return {
        "object_id": meta["id"],
        "path": path,
        "source_kind": "TEX_META",
        "object_type": meta["type_objet"],
        "status": meta["status"],
        "source_commit_sha": binding["source_commit_sha"],
        "source_sha256": binding["source_sha256"],
        "git_blob_sha1": binding["git_blob_sha1"],
    }


def _build_raw() -> dict[str, Any]:
    tex_paths = [
        path
        for path in _tree_paths()
        if path.endswith(".tex") and path != QCM_TEX
    ]
    objects = [_meta_object(path) for path in sorted(tex_paths)]
    qcm_binding = _binding(QCM_JSON)
    objects.append(
        {
            "object_id": "1SPE-SUITES-QCM",
            "path": QCM_JSON,
            "source_kind": "SYNTHETIC_QCM_CANONICAL",
            "object_type": "qcm",
            "status": "generated",
            "source_commit_sha": qcm_binding["source_commit_sha"],
            "source_sha256": qcm_binding["source_sha256"],
            "git_blob_sha1": qcm_binding["git_blob_sha1"],
        }
    )
    objects.sort(key=lambda row: row["object_id"])

    remediation_sources = [
        {
            "object_id": row["object_id"],
            "path": row["path"],
            "source_sha256": row["source_sha256"],
            "git_blob_sha1": row["git_blob_sha1"],
        }
        for row in objects
        if row["source_kind"] == "TEX_META"
        and row["path"].startswith(f"{CHAPTER_PREFIX}/remediation/")
    ]
    authority_sources = [_named_binding(path) for path in PROGRAMME_AUTHORITY_PATHS]

    payload: dict[str, Any] = {
        "schema_version": "1SPE_SUITES_REVIEW_SOURCE_FREEZE.v1",
        "chapter": "1SPE-SUITES",
        "source_sha": SOURCE_SHA,
        "freeze_semantics": {
            "content_review_only": True,
            "publication_approval": False,
            "release_acceptance": False,
            "visual_d7_approval": False,
            "source_change_invalidates_freeze": True,
        },
        "counts": {
            "chapter_objects": len(objects),
            "tex_meta_objects": len(tex_paths),
            "synthetic_qcm_objects": 1,
            "remediation_sources": len(remediation_sources),
            "unknown": 0,
        },
        "objects": objects,
        "contract": _named_binding(CONTRACT),
        "qcm": {
            "canonical": _named_binding(QCM_JSON),
            "generated_tex": _named_binding(QCM_TEX),
        },
        "remediation": {
            "sources": remediation_sources,
            "aggregate_digest": canonical_digest(remediation_sources),
        },
        "relevant_manifest": {
            **_named_binding(MANIFEST),
            "role": "repository build-manifest authority; not asserted fresh for this candidate",
        },
        "programme_authority": {
            "nor": "MENE2602917A",
            "sources": authority_sources,
            "aggregate_digest": canonical_digest(authority_sources),
        },
        "chapter_object_set_digest": canonical_digest(objects),
    }
    return payload


def validate_freeze(payload: dict[str, Any]) -> None:
    if payload.get("source_sha") != SOURCE_SHA:
        raise ValueError("freeze source SHA is not the authorized candidate")
    counts = payload.get("counts", {})
    if counts != {
        "chapter_objects": 161,
        "tex_meta_objects": 160,
        "synthetic_qcm_objects": 1,
        "remediation_sources": 13,
        "unknown": 0,
    }:
        raise ValueError("freeze counts are not exact")
    objects = payload.get("objects", [])
    if len(objects) != 161 or len({row.get("object_id") for row in objects}) != 161:
        raise ValueError("chapter object set is not exact")
    if payload.get("chapter_object_set_digest") != canonical_digest(objects):
        raise ValueError("chapter object-set digest mismatch")
    remediation = payload.get("remediation", {})
    if remediation.get("aggregate_digest") != canonical_digest(
        remediation.get("sources", [])
    ):
        raise ValueError("remediation digest mismatch")
    authority = payload.get("programme_authority", {})
    if authority.get("aggregate_digest") != canonical_digest(authority.get("sources", [])):
        raise ValueError("programme authority digest mismatch")
    expected = _build_raw()
    if payload != expected:
        raise ValueError("freeze does not match the exact Git source tree")


def build_freeze() -> dict[str, Any]:
    payload = _build_raw()
    validate_freeze(payload)
    return payload


def _current_blob(path: str) -> str:
    candidate = ROOT / path
    if not candidate.is_file():
        raise ValueError(f"current source missing: {path}")
    return str(_git("hash-object", path)).strip()


def validate_current_bindings(payload: dict[str, Any]) -> None:
    bindings = list(payload["objects"])
    bindings.extend((payload["contract"], payload["qcm"]["generated_tex"]))
    bindings.extend(payload["programme_authority"]["sources"])
    # BUILD_MANIFEST is frozen above as contextual evidence at SOURCE_SHA.  Its
    # empty derived envelope is refreshed whenever repository sources advance;
    # that mechanical refresh must not rebind otherwise unchanged chapter
    # content.  A future receipt policy may add a separate render binding.
    seen: set[str] = set()
    for row in bindings:
        path = row["path"]
        if path in seen:
            continue
        seen.add(path)
        if _current_blob(path) != row["git_blob_sha1"]:
            raise ValueError(f"STALE freeze binding: {path}")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the fixed artifact and current source bindings without writing",
    )
    args = parser.parse_args()
    payload = build_freeze()
    rendered = render_json(payload)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("STALE: audit/1SPE_SUITES_REVIEW_SOURCE_FREEZE.json")
        validate_current_bindings(payload)
        print(
            "PASS 1SPE-SUITES source freeze: "
            f"{payload['source_sha']} | 161 objects | UNKNOWN=0"
        )
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
