#!/usr/bin/env python3
"""Build the immutable T3 Wave A debt-scope freeze."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALGEBRA_PATH = ROOT / "audit" / "CURRENT_ANOMALY_SET_ALGEBRA.json"
SUNSET_PATH = ROOT / "audit" / "RESIDUAL_13_SUNSET_LEDGER.json"
OUTPUT_JSON = ROOT / "audit" / "T3_WAVE_A_INITIAL_FREEZE.json"
OUTPUT_MD = ROOT / "audit" / "T3_WAVE_A_INITIAL_FREEZE.md"
DEFAULT_LOCK = Path(tempfile.gettempdir()) / "nexus-t3-wave-a-initial-freeze.lock"

SOURCE_SHA = "7b6140920c1e09d359bc7bf0d837192f3fe455da"
RESIDUAL_DIGEST = (
    "sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98"
)
PREVIOUS_89_DIGEST = (
    "sha256:8daf2b85cecb556daa788056c66060ee6e0c20d00a09c976b9bac9f1bd9d8303"
)
PARTITION = {
    "1SPE-EXPONENTIELLE": 2,
    "1SPE-SUITES": 5,
    "1SPE-VARIABLES-ALEATOIRES": 4,
    "TNSI-PROJET": 2,
}
POST_FREEZE_CONTENT_PATHS = [
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/10_C1_generalites_suites.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/12_C3_suites_geometriques.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/cours/13_C4_sommes.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/dossier_curation.json",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-A-corrige.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/evaluations/1SPE-SUITES-EV-B-corrige.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/methodes/1SPE-SUITES-ME-003.tex",
    "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/remediation/1SPE-SUITES-RE-C3.tex",
]


def fingerprint_digest(fingerprints: list[str]) -> str:
    payload = json.dumps(
        sorted(fingerprints), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def git_blob(relative_path: str) -> tuple[bytes, str]:
    data = subprocess.run(
        ["git", "show", f"{SOURCE_SHA}:{relative_path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    oid = subprocess.run(
        ["git", "rev-parse", f"{SOURCE_SHA}:{relative_path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    return data, oid


def git_json(relative_path: str) -> tuple[dict, dict[str, str]]:
    data, oid = git_blob(relative_path)
    return json.loads(data.decode("utf-8")), {
        "git_blob_oid": oid,
        "sha256": f"sha256:{hashlib.sha256(data).hexdigest()}",
    }


def build() -> tuple[dict, str]:
    algebra_rel = str(ALGEBRA_PATH.relative_to(ROOT))
    sunset_rel = str(SUNSET_PATH.relative_to(ROOT))
    algebra, algebra_provenance = git_json(algebra_rel)
    sunset, sunset_provenance = git_json(sunset_rel)

    residual_entries = sorted(
        sunset["entries"], key=lambda entry: entry["fingerprint"]
    )
    residual = [entry["fingerprint"] for entry in residual_entries]
    previous = sorted(
        algebra["set_algebra"]["sets"]["EXPECTED_REVIEW_DEBT"]
    )
    previous_details = {
        entry["fingerprint"]: entry
        for entry in algebra["expected_review_debt_details"]
    }
    partition = dict(
        sorted(Counter(entry["chapter"] for entry in residual_entries).items())
    )
    intersection = sorted(
        fingerprint
        for fingerprint in previous
        if previous_details[fingerprint]["chapter"] in PARTITION
    )

    if len(residual) != 13 or fingerprint_digest(residual) != RESIDUAL_DIGEST:
        raise ValueError("residual-13 scope drift")
    if partition != PARTITION:
        raise ValueError(f"residual-13 partition drift: {partition}")
    if len(previous) != 89 or fingerprint_digest(previous) != PREVIOUS_89_DIGEST:
        raise ValueError("previous-89 scope drift")
    if set(residual) & set(previous):
        raise ValueError("residual-13 and previous-89 are not disjoint")
    if intersection:
        raise ValueError(f"unexpected previous-89 Wave A intersection: {intersection}")

    artifact = {
        "artifact_type": "t3_wave_a_initial_freeze",
        "schema_version": 1,
        "wave_a_source_sha": SOURCE_SHA,
        "freeze_materialization": {
            "basis": "IMMUTABLE_GIT_TREE",
            "chronology": "RETROACTIVE_AFTER_FIRST_SUITES_TDD_EDIT",
            "post_freeze_content_paths": POST_FREEZE_CONTENT_PATHS,
            "post_freeze_content_path_count": len(POST_FREEZE_CONTENT_PATHS),
        },
        "residual_13": {
            "count": 13,
            "digest": RESIDUAL_DIGEST,
            "fingerprints": residual,
            "partition_by_chapter": PARTITION,
        },
        "previous_89": {
            "count": 89,
            "digest": PREVIOUS_89_DIGEST,
            "fingerprints": previous,
            "wave_a_intersection": intersection,
            "wave_a_intersection_count": len(intersection),
        },
        "set_relations": {
            "residual_13_intersection_previous_89": sorted(
                set(residual) & set(previous)
            ),
            "unknown": 0,
        },
        "source_artifacts": {
            algebra_rel: algebra_provenance,
            sunset_rel: sunset_provenance,
        },
        "source_semantic_digests": {
            algebra_rel: algebra["source_digest"],
            sunset_rel: sunset["fingerprint_digest"],
        },
        "verdict": "FROZEN_NO_TOCTOU",
    }

    lines = [
        "# T3 Wave A — gel initial",
        "",
        f"- `WAVE_A_SOURCE_SHA = {SOURCE_SHA}`",
        f"- `RESIDUAL_13 = 13` — `{RESIDUAL_DIGEST}`",
        f"- `PREVIOUS_89 = 89` — `{PREVIOUS_89_DIGEST}`",
        "- `RESIDUAL_13 ∩ PREVIOUS_89 = 0`",
        "- `UNKNOWN = 0`",
        "- Base : arbre Git immuable au SHA ci-dessus.",
        "- Chronologie : matérialisation rétroactive après le premier lot TDD Suites ; "
        "les huit sources modifiées sont explicitement listées dans le JSON.",
        "",
        "## Partition résiduelle",
        "",
        "| Chapitre | Nombre |",
        "|---|---:|",
    ]
    lines.extend(f"| `{chapter}` | {count} |" for chapter, count in PARTITION.items())
    lines.extend(
        [
            "",
            "## Treize fingerprints gelés",
            "",
            "| Fingerprint | Chapitre | Objet |",
            "|---|---|---|",
        ]
    )
    lines.extend(
        f"| `{entry['fingerprint']}` | `{entry['chapter']}` | `{entry['object_id']}` |"
        for entry in residual_entries
    )
    lines.extend(
        [
            "",
            "L'intersection Wave A avec les 89 dettes antérieures est vide. "
            "La fermeture finale sera réconciliée à partir de ces deux sets gelés, "
            "sans double comptage.",
            "",
        ]
    )
    return artifact, "\n".join(lines)


def _stage(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


def atomic_write_pair(
    outputs: list[tuple[Path, bytes]], lock_path: Path
) -> None:
    """Replace an output pair under a lock, rolling back a partial replace."""

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        staged: dict[Path, Path] = {}
        backups: dict[Path, Path | None] = {}
        replaced: list[Path] = []
        try:
            for path, content in outputs:
                staged[path] = _stage(path, content)
                backups[path] = _stage(path, path.read_bytes()) if path.exists() else None

            for index, (path, _content) in enumerate(outputs):
                os.replace(staged[path], path)
                replaced.append(path)
                if index == 0 and os.environ.get(
                    "NEXUS_T3_FREEZE_TEST_FAIL_AFTER_FIRST_REPLACE"
                ) == "1":
                    raise RuntimeError("injected failure after first replace")

            for path, _content in outputs:
                directory_descriptor = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory_descriptor)
                finally:
                    os.close(directory_descriptor)
        except BaseException:
            for path in reversed(replaced):
                backup = backups[path]
                if backup is None:
                    path.unlink(missing_ok=True)
                else:
                    os.replace(backup, path)
                    backups[path] = None
            raise
        finally:
            for temporary in [*staged.values(), *backups.values()]:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact, markdown = build()
    json_text = json.dumps(
        artifact, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"

    if args.check:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            return 1
        return int(
            OUTPUT_JSON.read_text(encoding="utf-8") != json_text
            or OUTPUT_MD.read_text(encoding="utf-8") != markdown
        )

    atomic_write_pair(
        [
            (OUTPUT_JSON, json_text.encode("utf-8")),
            (OUTPUT_MD, markdown.encode("utf-8")),
        ],
        DEFAULT_LOCK,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
