from __future__ import annotations

import hashlib
import importlib.util
import json
import errno
import os
import shutil
import stat
import subprocess
import sys
import threading
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCRIPT = ROOT / "scripts" / "inventory_collection.py"
MANIFEST_SCRIPT = ROOT / "scripts" / "build_manifest.py"
SHA256_A = "sha256:" + "a" * 64
SHA256_B = "sha256:" + "b" * 64
RUN_ID = "0123456789abcdef0123456789abcdef"
REPRO_CONFIG_PATH = (
    "Mathematiques/manuel-maths/config/reproducible-build.json"
)
TOOL_VERSIONS = {
    "lualatex": "LuaHBTeX, Version 1.17.0",
    "pdfinfo": "pdfinfo version 24.02.0",
    "pdffonts": "pdffonts version 24.02.0",
    "python": f"Python {sys.version.split()[0]}",
}


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def inventory_module():
    return _load_module(INVENTORY_SCRIPT, "inventory_collection_observed_tests")


@pytest.fixture()
def manifest_module():
    assert MANIFEST_SCRIPT.is_file(), "scripts/build_manifest.py doit être créé"
    return _load_module(MANIFEST_SCRIPT, "build_manifest_tests")


def _git_repository(path: Path) -> str:
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "-c",
            "user.name=Observed Build Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _state_digest(builds: list[dict[str, object]]) -> str:
    canonical = json.dumps(
        builds,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _manifest(head: str, builds: list[dict[str, object]]) -> dict[str, object]:
    return {
        "artifact_type": "build_manifest",
        "build_state_digest": _state_digest(builds),
        "builds": builds,
        "generated_by": "build_manifest.py",
        "model_digest": SHA256_B,
        "provenance": {
            "branch": "master",
            "dirty": True,
            "head_sha": head,
        },
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
        "source_digest": SHA256_A,
    }


def _build(head: str, pdf_path: str, pdf_bytes: bytes) -> dict[str, object]:
    dependency_bytes = b"% generated dependency"
    return {
        "excluded_objects": ["OBJ-EXCLUDED"],
        "gates": {
            "compile": {"passed": True},
            "preflight": {"passed": True},
            "release_strict": {"blocker_count": 3, "passed": False},
        },
        "generated_dependencies": ["build/generated-index.tex"],
        "generated_dependency_digests": {
            "build/generated-index.tex": (
                "sha256:" + hashlib.sha256(dependency_bytes).hexdigest()
            )
        },
        "git_sha": head,
        "included_objects": ["OBJ-2", "OBJ-1"],
        "manual": "1SPE",
        "model_digest": SHA256_B,
        "ordered_trace": ["OBJ-2", "OBJ-1"],
        "page_count": 7,
        "pdf_path": pdf_path,
        "pdf_sha256": "sha256:" + hashlib.sha256(pdf_bytes).hexdigest(),
        "reproducibility": _reproducibility("c" * 40, 1),
        "source_digest": SHA256_A,
        "tool_versions": dict(TOOL_VERSIONS),
        "variant": "professeur",
    }


def _reproducibility(source_commit: str, epoch: int) -> dict[str, object]:
    return {
        "config_path": REPRO_CONFIG_PATH,
        "source_commit": source_commit,
        "source_date_epoch": epoch,
        "force_source_date": "1",
        "timezone": "UTC",
        "locale": "C.UTF-8",
        "pythonhashseed": "0",
    }


def _receipt(
    *,
    compile_succeeded: bool = True,
    preflight_succeeded: bool = True,
) -> dict[str, object]:
    return {
        "compile_succeeded": compile_succeeded,
        "evidence_sha256": {
            "master": SHA256_A,
            "log": SHA256_A,
            "fls": SHA256_A,
            "pdf": SHA256_A,
            "preflight": SHA256_A,
        },
        "fls_path": "build/manual.fls",
        "gates": {"release_strict": {"blocker_count": 3, "passed": False}},
        "generated_dependencies": ["build/generated-index.tex"],
        "log_path": "build/manual.log",
        "manual": "1SPE",
        "master_path": (
            "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.tex"
        ),
        "pdf_path": (
            "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
        ),
        "preflight_report": "build/preflight.json",
        "preflight_succeeded": preflight_succeeded,
        "reproducibility": _reproducibility("c" * 40, 1),
        "run_id": RUN_ID,
        "tool_versions": dict(TOOL_VERSIONS),
        "variant": "professeur",
    }


def _trace_token(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:40]


def _trace_marker(kind: str, path: str) -> str:
    return f"NEXUS_OBJECT_{kind}:{_trace_token(path)}"


def _git_timestamp(repository: Path, commit: str) -> int:
    return int(
        subprocess.run(
            ["git", "-C", str(repository), "show", "-s", "--format=%ct", commit],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )


def _write_reproducibility_config(
    repository: Path,
    *,
    source_commit: str,
    source_date_epoch: int,
    tracked: bool = True,
) -> Path:
    path = repository / REPRO_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": source_commit,
                "source_date_epoch": source_date_epoch,
            }
        ),
        encoding="utf-8",
    )
    if tracked:
        subprocess.run(
            ["git", "-C", str(repository), "add", REPRO_CONFIG_PATH],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "-c",
                "user.name=Observed Build Tests",
                "-c",
                "user.email=observed@example.invalid",
                "commit",
                "-qm",
                "reproducibility control",
            ],
            check=True,
        )
    return path


def _install_receipt_evidence(
    repository: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[dict[str, object], dict[str, Path], str, int]:
    source_commit = _git_repository(repository)
    source_date_epoch = _git_timestamp(repository, source_commit)
    config_path = _write_reproducibility_config(
        repository,
        source_commit=source_commit,
        source_date_epoch=source_date_epoch,
    )
    master_relative = (
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.tex"
    )
    pdf_relative = (
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    )
    master = repository / master_relative
    pdf = repository / pdf_relative
    log = repository / "build/manual.log"
    fls = repository / "build/manual.fls"
    preflight = repository / "build/preflight.json"
    dependency = repository / "build/generated-index.tex"
    object_2 = repository / "OBJ-2"
    object_1 = repository / "OBJ-1"
    for path in (
        master,
        pdf,
        log,
        fls,
        preflight,
        dependency,
        object_2,
        object_1,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
    master.write_text(
        f"\\typeout{{NEXUS_BUILD_RUN:{RUN_ID}}}\n",
        encoding="utf-8",
    )
    pdf_bytes = b"%PDF closed receipt evidence"
    pdf.write_bytes(pdf_bytes)
    log.write_text(
        "\n".join(
            [
                f"NEXUS_BUILD_RUN:{RUN_ID}",
                _trace_marker("BEGIN", "OBJ-2"),
                _trace_marker("END", "OBJ-2"),
                _trace_marker("BEGIN", "OBJ-1"),
                _trace_marker("END", "OBJ-1"),
                "Output written on MANUEL_1SPE_professeur.pdf (11 pages).",
            ]
        ),
        encoding="utf-8",
    )
    fls.write_text(
        "\n".join(
            [
                f"INPUT {master_relative}",
                "INPUT OBJ-2",
                "INPUT /usr/share/texlive/texmf-dist/tex/latex/base/article.cls",
                "INPUT OBJ-1",
                "OUTPUT build/generated-index.tex",
            ]
        ),
        encoding="utf-8",
    )
    dependency.write_text("% generated", encoding="utf-8")
    object_2.write_text("objet 2", encoding="utf-8")
    object_1.write_text("objet 1", encoding="utf-8")
    reproducibility = _reproducibility(source_commit, source_date_epoch)
    preflight.write_text(
        json.dumps(
            {
                "run_id": RUN_ID,
                "pdf_path": pdf_relative,
                "pdf_sha256": (
                    "sha256:" + hashlib.sha256(pdf_bytes).hexdigest()
                ),
                "page_count": 11,
                "passed": True,
                "checks": {
                    "verify_pdf": {"passed": True},
                    "pdfinfo": {"passed": True},
                    "pdffonts": {"passed": True},
                },
                "tool_versions": dict(TOOL_VERSIONS),
                "reproducibility": reproducibility,
            }
        ),
        encoding="utf-8",
    )
    paths = {
        "master": master,
        "log": log,
        "fls": fls,
        "pdf": pdf,
        "preflight": preflight,
        "config": config_path,
        "object_2": object_2,
        "object_1": object_1,
    }
    receipt = {
        **_receipt(),
        "generated_dependencies": ["build/generated-index.tex"],
        "master_path": master_relative,
        "pdf_path": pdf_relative,
        "reproducibility": reproducibility,
        "evidence_sha256": {
            name: "sha256:" + hashlib.sha256(paths[name].read_bytes()).hexdigest()
            for name in ("master", "log", "fls", "pdf", "preflight")
        },
    }
    pdf_digest = receipt["evidence_sha256"]["pdf"]  # type: ignore[index]
    fake_pdf = SimpleNamespace(
        _is_canonical_manual_pdf_path=lambda *_args, **_kwargs: True,
        inspect_stable_pdf=lambda *_args, **_kwargs: (
            pdf_digest,
            11,
            "pdfinfo",
            None,
        ),
    )
    fake_inventory = SimpleNamespace(
        COMPILED_PDF_BUILD_ROOTS={
            "1SPE": "Mathematiques/manuel-maths/build"
        },
        _model_digest=lambda _inventory: SHA256_B,
        _observed_deliverable_variant=lambda _manual, _variant: (
            "manuel_professeur"
        ),
        _page_count_with_pdfinfo=lambda _path: (11, None),
        _page_count_with_python=lambda _path: (None, "unused"),
        _pdf_core=fake_pdf,
        _pdf_matches_observed_identity=lambda _path, _manual, _variant: True,
        _validate_artifact_schema=lambda *_args, **_kwargs: None,
        build_inventory=lambda _root: {
            "declared_assemblies": [
                {
                    "included_objects": ["OBJ-2", "OBJ-1", "OBJ-EXCLUDED"],
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            "source_digest": SHA256_A,
        },
    )
    monkeypatch.setattr(
        manifest_module,
        "_load_inventory_module",
        lambda: fake_inventory,
    )
    monkeypatch.setattr(
        manifest_module,
        "_run_local_pdf_preflight",
        lambda _path, *, expected_pages: {
            "pdffonts": "passed",
            "pdfinfo": f"passed:{expected_pages}",
        },
    )
    monkeypatch.setattr(
        manifest_module,
        "_collect_local_tool_versions",
        lambda _reproducibility: dict(TOOL_VERSIONS),
        raising=False,
    )
    return receipt, paths, source_commit, source_date_epoch


def _install_schema(repository: Path) -> None:
    schema = ROOT / "audit/schemas/v1/build-manifest.schema.json"
    target = repository / "audit/schemas/v1/build-manifest.schema.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(schema, target)


def _write_manifest(repository: Path, payload: dict[str, object]) -> None:
    marker = repository / "build/.fixture-dirty"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("fixture", encoding="utf-8")
    for build in payload.get("builds", []):  # type: ignore[union-attr]
        for dependency in build.get("generated_dependencies", []):
            target = repository / dependency
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("% generated dependency", encoding="utf-8")
    target = repository / "audit/BUILD_MANIFEST.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _load(
    inventory_module,
    repository: Path,
) -> list[dict[str, object]]:
    return inventory_module._load_observed_build_manifest(
        repository,
        source_digest=SHA256_A,
        model_digest=SHA256_B,
        declared_assemblies=[
            {
                "manual": "1SPE",
                "scope": "manual",
                "variant": "professeur",
                "included_objects": ["OBJ-2", "OBJ-1", "OBJ-EXCLUDED"],
            }
        ],
        pdfinfo_counter=lambda _path: (7, None),
        python_counter=lambda _path: (None, "unused"),
    )


def test_empty_manifest_is_model_valid_and_yields_no_observed_build(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    _write_manifest(tmp_path, _manifest(head, []))

    assert _load(inventory_module, tmp_path) == []


def test_stale_empty_manifest_requires_explicit_refresh(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    stale = _manifest(head, [])
    stale["source_digest"] = "sha256:" + "0" * 64
    stale["model_digest"] = "sha256:" + "1" * 64
    _write_manifest(tmp_path, stale)

    with pytest.raises(inventory_module.InventoryError, match="source_digest"):
        _load(inventory_module, tmp_path)
    with pytest.raises(inventory_module.InventoryError, match="source_digest"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[],
            pdfinfo_counter=lambda _path: (7, None),
            python_counter=lambda _path: (None, "unused"),
            empty_manifest_refresh_capability=True,
        )


def test_bounded_refresh_loader_never_ignores_nonempty_manifest_digests(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    build = _build(head, "build/MANUEL_1SPE_professeur.pdf", b"%PDF")
    stale = _manifest(head, [build])
    stale["source_digest"] = "sha256:" + "0" * 64
    _write_manifest(tmp_path, stale)

    with pytest.raises(inventory_module.InventoryError, match="source_digest"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[],
            pdfinfo_counter=lambda _path: (7, None),
            python_counter=lambda _path: (None, "unused"),
            empty_manifest_refresh_capability=True,
        )


def test_empty_refresh_derivation_uses_only_the_bounded_inventory_path(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[Path, dict[str, object]]] = []

    def build_inventory(root: Path) -> dict[str, object]:
        calls.append((root, {}))
        return {"source_digest": SHA256_A}

    fake_inventory = SimpleNamespace(
        _model_digest=lambda _inventory: SHA256_B,
        _build_inventory_for_empty_manifest_refresh=build_inventory,
    )
    monkeypatch.setattr(
        manifest_module,
        "_load_inventory_module",
        lambda: fake_inventory,
    )
    monkeypatch.setattr(
        manifest_module,
        "_git_state",
        lambda _root: ("a" * 40, "fixture", True),
    )

    envelope = manifest_module._derive_empty_refresh_envelope(tmp_path)

    assert calls == [
        (tmp_path, {})
    ]
    assert envelope == {
        "artifact_type": "build_manifest",
        "build_state_digest": _state_digest([]),
        "builds": [],
        "generated_by": "build_manifest.py",
        "model_digest": SHA256_B,
        "provenance": {
            "branch": "fixture",
            "dirty": True,
            "head_sha": "a" * 40,
        },
        "schema_ref": "audit/schemas/v1/build-manifest.schema.json",
        "schema_version": 1,
        "source_digest": SHA256_A,
    }


def test_refresh_empty_manifest_restores_strict_inventory_loading(
    tmp_path: Path,
    inventory_module,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    stale = _manifest(head, [])
    stale["source_digest"] = "sha256:" + "0" * 64
    stale["model_digest"] = "sha256:" + "1" * 64
    _write_manifest(tmp_path, stale)
    expected = _manifest(head, [])
    monkeypatch.setattr(
        manifest_module,
        "_derive_empty_refresh_envelope",
        lambda _root: expected,
    )

    manifest_module.refresh_empty_manifest(
        tmp_path / "audit/BUILD_MANIFEST.json"
    )

    payload = json.loads(
        (tmp_path / "audit/BUILD_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert payload == expected
    assert _load(inventory_module, tmp_path) == []


def test_refresh_empty_manifest_refuses_nonempty_manifest_without_changes(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    build = _build(head, "build/MANUEL_1SPE_professeur.pdf", b"%PDF")
    _write_manifest(tmp_path, _manifest(head, [build]))
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()

    with pytest.raises(manifest_module.BuildManifestError, match="vide"):
        manifest_module.refresh_empty_manifest(path)

    assert path.read_bytes() == original


@pytest.mark.parametrize("kind", ["symlink", "hardlink"])
def test_refresh_empty_manifest_rejects_linked_destination(
    tmp_path: Path,
    manifest_module,
    kind: str,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    external = tmp_path.parent / f"{tmp_path.name}-{kind}-manifest.json"
    external.write_text(
        json.dumps(_manifest(head, [])),
        encoding="utf-8",
    )
    if kind == "symlink":
        path.symlink_to(external)
    else:
        os.link(external, path)
    original = external.read_bytes()

    with pytest.raises(manifest_module.BuildManifestError, match="non sûr|invalide"):
        manifest_module.refresh_empty_manifest(path)

    assert external.read_bytes() == original


def test_refresh_empty_manifest_rejects_parent_substitution(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    stale = _manifest(head, [])
    stale["source_digest"] = "sha256:" + "0" * 64
    _write_manifest(tmp_path, stale)
    expected = _manifest(head, [])
    monkeypatch.setattr(
        manifest_module,
        "_derive_empty_refresh_envelope",
        lambda _root: expected,
    )
    audit = tmp_path / "audit"
    path = audit / "BUILD_MANIFEST.json"
    original = path.read_bytes()
    external_audit = tmp_path.parent / f"{tmp_path.name}-refresh-external"
    external_audit.mkdir()
    external_manifest = external_audit / "BUILD_MANIFEST.json"
    external_manifest.write_bytes(original)
    external_original = external_manifest.read_bytes()
    parked = tmp_path / "audit-refresh-parked"
    real_replace = manifest_module.os.replace
    attacked = False

    def substitute_parent(
        source: str,
        destination: str,
        *,
        src_dir_fd: int,
        dst_dir_fd: int,
    ) -> None:
        nonlocal attacked
        if destination == "BUILD_MANIFEST.json" and not attacked:
            attacked = True
            audit.rename(parked)
            audit.symlink_to(external_audit, target_is_directory=True)
        real_replace(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
        )

    monkeypatch.setattr(manifest_module.os, "replace", substitute_parent)

    with pytest.raises(manifest_module.BuildManifestError, match="parent modifié"):
        manifest_module.refresh_empty_manifest(path)

    assert attacked is True
    assert external_manifest.read_bytes() == external_original
    assert (parked / "BUILD_MANIFEST.json").read_bytes() == original


@pytest.mark.parametrize("drift", ["head", "source"])
def test_refresh_empty_manifest_rejects_drift_after_staging(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    drift: str,
) -> None:
    _git_repository(tmp_path)
    source = tmp_path / "tracked-source.tex"
    source.write_text("initial", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked-source.tex"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Observed Build Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "-qm",
            "tracked source",
        ],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _install_schema(tmp_path)
    stale = _manifest(head, [])
    stale["source_digest"] = "sha256:" + "0" * 64
    _write_manifest(tmp_path, stale)
    expected = _manifest(head, [])
    monkeypatch.setattr(
        manifest_module,
        "_derive_empty_refresh_envelope",
        lambda _root: expected,
    )
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    real_write_all = manifest_module._write_all
    attacked = False

    def drift_after_staging(descriptor: int, payload: bytes) -> None:
        nonlocal attacked
        real_write_all(descriptor, payload)
        if attacked:
            return
        attacked = True
        if drift == "source":
            source.write_text("mutated", encoding="utf-8")
        else:
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(tmp_path),
                    "-c",
                    "user.name=Observed Build Tests",
                    "-c",
                    "user.email=observed@example.invalid",
                    "commit",
                    "--allow-empty",
                    "-qm",
                    "concurrent head",
                ],
                check=True,
            )

    monkeypatch.setattr(manifest_module, "_write_all", drift_after_staging)

    with pytest.raises(manifest_module.BuildManifestError, match="destination"):
        manifest_module.refresh_empty_manifest(path)

    assert attacked is True
    assert path.read_bytes() == original


def test_refresh_empty_manifest_rolls_back_and_recovers_after_fsync_failure(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    stale = _manifest(head, [])
    stale["source_digest"] = "sha256:" + "0" * 64
    _write_manifest(tmp_path, stale)
    expected = _manifest(head, [])
    monkeypatch.setattr(
        manifest_module,
        "_derive_empty_refresh_envelope",
        lambda _root: expected,
    )
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    real_fsync = manifest_module.os.fsync
    failed = False

    def fail_first_directory_fsync(descriptor: int) -> None:
        nonlocal failed
        metadata = os.fstat(descriptor)
        if stat.S_ISDIR(metadata.st_mode) and not failed:
            failed = True
            raise OSError(errno.EIO, "simulated directory fsync failure")
        real_fsync(descriptor)

    monkeypatch.setattr(
        manifest_module.os,
        "fsync",
        fail_first_directory_fsync,
    )

    with pytest.raises(manifest_module.BuildManifestError, match="transaction"):
        manifest_module.refresh_empty_manifest(path)

    assert failed is True
    assert path.read_bytes() == original
    assert not list(path.parent.glob(f".{path.name}.*"))

    manifest_module.refresh_empty_manifest(path)

    assert json.loads(path.read_text(encoding="utf-8")) == expected


def test_complete_manifest_is_loaded_with_order_preserved(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    observed = _load(inventory_module, tmp_path)

    assert observed == [build]
    assert observed[0]["ordered_trace"] == ["OBJ-2", "OBJ-1"]


@pytest.mark.parametrize(
    ("raw_variant", "deliverable_variant"),
    [
        ("professeur", "manuel_professeur"),
        ("eleve", "manuel_eleve"),
    ],
)
def test_observed_variant_mapping_is_explicit(
    inventory_module,
    raw_variant: str,
    deliverable_variant: str,
) -> None:
    assert (
        inventory_module._observed_deliverable_variant("1SPE", raw_variant)
        == deliverable_variant
    )


def test_release_gate_uses_declared_variant_mapping_without_false_pdf_evidence(
    inventory_module,
) -> None:
    declared = [
        {"manual": "1SPE", "scope": "manual", "variant": "eleve"},
        {"manual": "1SPE", "scope": "manual", "variant": "professeur"},
    ]
    professor = {
        "manual": "1SPE",
        "variant": "professeur",
    }
    coverage = inventory_module._observed_build_coverage(
        declared,
        [professor],
    )
    inventory = {
        "deliverable_matrix": {
            "manuals": {
                "1SPE": {
                    "blockers": [],
                    "phase0_structural_eligible": True,
                    "publication_eligible": False,
                    "variants": {
                        "manuel_eleve": {},
                        "manuel_professeur": {},
                    },
                }
            }
        },
        "observed_build_coverage": coverage,
        "pdfs": [
            {
                "manual": "1SPE",
                "path": "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf",
                "variant": "eleve",
            }
        ],
    }

    gate = inventory_module._release_strict_gate(inventory)

    assert "1SPE:build_observé_absent:manuel_eleve" in gate["reasons"]
    assert "1SPE:build_observé_absent:manuel_professeur" not in gate["reasons"]


def test_release_execution_dimension_passes_when_static_and_observed_are_ready(
    inventory_module,
) -> None:
    inventory = {
        "deliverable_matrix": {
            "manuals": {
                "1SPE": {
                    "blockers": [],
                    "phase0_structural_eligible": True,
                    "publication_eligible": True,
                    "variants": {
                        "manuel_eleve": {},
                        "manuel_professeur": {},
                    },
                }
            }
        },
        "observed_build_coverage": {
            "1SPE": {
                "observed_build_ready": True,
                "variants": {
                    "manuel_eleve": {
                        "declared_variants": ["eleve"],
                        "observed_variants": ["eleve"],
                        "ready": True,
                    },
                    "manuel_professeur": {
                        "declared_variants": ["professeur"],
                        "observed_variants": ["professeur"],
                        "ready": True,
                    },
                },
            }
        },
    }

    gate = inventory_module._release_strict_gate(inventory)

    assert gate["dimensions"]["execution"] == "passed"
    assert not any(
        "build_observé_absent" in reason
        or "assemblage_déclaré_absent" in reason
        for reason in gate["reasons"]
    )


def test_release_keeps_unintegrated_build_receipt_as_explicit_debt(
    inventory_module,
) -> None:
    inventory = {
        "deliverable_matrix": {
            "manuals": {
                "1SPE": {
                    "blockers": [],
                    "phase0_structural_eligible": True,
                    "publication_eligible": True,
                    "variants": {},
                }
            }
        },
        "observed_build_coverage": {
            "1SPE": {
                "observed_build_ready": True,
                "variants": {},
            }
        },
        "observed_build_integration": {
            "entrypoint": (
                "python scripts/build_manifest.py "
                "--receipt <build-receipt.json>"
            ),
            "status": "not_integrated",
        },
    }

    gate = inventory_module._release_strict_gate(inventory)

    assert gate["dimensions"]["execution"] == "failed"
    assert "build_receipt_producteurs_non_intégrés" in gate["reasons"]


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("head", "git_sha"),
        ("source", "source_digest"),
        ("model", "model_digest"),
        ("manual", "manual"),
        ("variant", "variant"),
        ("trace", "ordered_trace"),
        ("digest", "pdf_sha256"),
        ("pages", "page_count"),
        ("compile", "compile"),
        ("preflight", "preflight"),
        ("overlap", "included_objects"),
        ("dependency", "generated_dependencies"),
        ("coverage", "excluded_objects"),
        ("reproducibility", "reproducibility"),
    ],
)
def test_manifest_rejects_stale_or_corrupt_build(
    tmp_path: Path,
    inventory_module,
    mutation: str,
    expected: str,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    if mutation == "head":
        build["git_sha"] = "0" * 40
    elif mutation == "source":
        build["source_digest"] = "sha256:" + "0" * 64
    elif mutation == "model":
        build["model_digest"] = "sha256:" + "0" * 64
    elif mutation == "manual":
        build["manual"] = "UNKNOWN"
    elif mutation == "variant":
        build["variant"] = "eleve"
    elif mutation == "trace":
        build["ordered_trace"] = ["OBJ-1", "OBJ-2"]
    elif mutation == "digest":
        build["pdf_sha256"] = "sha256:" + "0" * 64
    elif mutation == "pages":
        build["page_count"] = 8
    elif mutation == "compile":
        build["gates"]["compile"]["passed"] = False  # type: ignore[index]
    elif mutation == "preflight":
        build["gates"]["preflight"]["passed"] = False  # type: ignore[index]
    elif mutation == "overlap":
        build["excluded_objects"] = ["OBJ-1"]
    elif mutation == "dependency":
        build["generated_dependencies"] = ["bad//generated.tex"]
        build["generated_dependency_digests"] = {
            "bad//generated.tex": (
                "sha256:"
                + hashlib.sha256(b"% generated dependency").hexdigest()
            )
        }
    elif mutation == "coverage":
        build["excluded_objects"] = []
    elif mutation == "reproducibility":
        del build["reproducibility"]
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match=expected):
        _load(inventory_module, tmp_path)


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        ("missing", None),
        ("extra", True),
        ("config_path", "config/repro.json"),
        ("source_commit", "A" * 40),
        ("source_date_epoch", True),
        ("source_date_epoch", 0),
        ("force_source_date", "0"),
        ("timezone", "Europe/Paris"),
        ("locale", "fr_FR.UTF-8"),
        ("pythonhashseed", "random"),
    ],
)
def test_manifest_schema_rejects_noncanonical_reproducibility(
    tmp_path: Path,
    inventory_module,
    mutation: str,
    value: object,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    reproducibility = build["reproducibility"]
    assert isinstance(reproducibility, dict)
    if mutation == "missing":
        del reproducibility["config_path"]
    else:
        reproducibility[mutation] = value
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match="reproducibility"):
        _load(inventory_module, tmp_path)


def test_manifest_rejects_duplicate_manual_variant(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build, deepcopy(build)]))

    with pytest.raises(inventory_module.InventoryError, match="doublon"):
        _load(inventory_module, tmp_path)


@pytest.mark.parametrize(
    "mutation",
    ["unrelated-head", "forged-branch", "clean-observed-build"],
)
def test_manifest_rejects_incoherent_envelope_provenance(
    tmp_path: Path,
    inventory_module,
    mutation: str,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    payload = _manifest(head, [_build(head, pdf_path, pdf_bytes)])
    if mutation == "unrelated-head":
        payload["provenance"]["head_sha"] = "0" * 40  # type: ignore[index]
    elif mutation == "forged-branch":
        payload["provenance"]["branch"] = "forged"  # type: ignore[index]
    else:
        payload["provenance"]["dirty"] = False  # type: ignore[index]
    _write_manifest(tmp_path, payload)

    with pytest.raises(inventory_module.InventoryError, match="provenance"):
        _load(inventory_module, tmp_path)


def test_manifest_rejects_pdf_name_for_the_other_variant(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf"
    pdf_bytes = b"%PDF-1.7 professor content under student name"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match="variante|variant"):
        _load(inventory_module, tmp_path)


def test_manifest_rejects_pdf_name_for_another_manual(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = (
        "Mathematiques/manuel-maths/build/"
        "MANUEL_TSPE_2026_2027_professeur.pdf"
    )
    pdf_bytes = b"%PDF-1.7 wrong manual name"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match="manual"):
        _load(inventory_module, tmp_path)


def test_manifest_rejects_pdf_reused_between_variants(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    professor_path = (
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    )
    student_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf"
    pdf_bytes = b"%PDF-1.7 identical student and professor artifact"
    for pdf_path in (professor_path, student_path):
        target = tmp_path / pdf_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf_bytes)
    professor = _build(head, professor_path, pdf_bytes)
    student = deepcopy(professor)
    student["variant"] = "eleve"
    student["pdf_path"] = student_path
    _write_manifest(tmp_path, _manifest(head, [professor, student]))

    with pytest.raises(inventory_module.InventoryError, match="PDF|digest"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                    "included_objects": ["OBJ-2", "OBJ-1", "OBJ-EXCLUDED"],
                },
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "eleve",
                    "included_objects": ["OBJ-2", "OBJ-1", "OBJ-EXCLUDED"],
                },
            ],
            pdfinfo_counter=lambda _path: (7, None),
            python_counter=lambda _path: (None, "unused"),
        )


def test_manifest_rejects_hardlinked_generated_dependency(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    external = tmp_path.parent / f"{tmp_path.name}-generated.tex"
    external.write_text("% external dependency", encoding="utf-8")
    dependency = tmp_path / "build/generated-index.tex"
    dependency.parent.mkdir(exist_ok=True)
    os.link(external, dependency)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match="hardlink"):
        _load(inventory_module, tmp_path)


@pytest.mark.parametrize("kind", ["outside", "symlink", "fifo", "hardlink"])
def test_manifest_rejects_unsafe_pdf_path(
    tmp_path: Path,
    inventory_module,
    kind: str,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    safe_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    if kind == "outside":
        pdf_path = "../outside.pdf"
        (tmp_path.parent / "outside.pdf").write_bytes(pdf_bytes)
    else:
        pdf_path = safe_path
        target = tmp_path / pdf_path
        target.parent.mkdir(parents=True)
        if kind == "symlink":
            external = tmp_path.parent / "external-observed.pdf"
            external.write_bytes(pdf_bytes)
            target.symlink_to(external)
        elif kind == "fifo":
            if not hasattr(os, "mkfifo"):
                pytest.skip("FIFO indisponible")
            os.mkfifo(target)
        else:
            external = tmp_path.parent / "external-observed-hardlink.pdf"
            external.write_bytes(pdf_bytes)
            os.link(external, target)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    with pytest.raises(inventory_module.InventoryError, match="PDF"):
        _load(inventory_module, tmp_path)


def test_manifest_rejects_pdf_mutated_during_snapshot(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    def mutate(_snapshot: Path) -> tuple[int, None]:
        target.write_bytes(b"X" * len(pdf_bytes))
        return 7, None

    with pytest.raises(inventory_module.InventoryError, match="modifié"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            pdfinfo_counter=mutate,
            python_counter=lambda _path: (None, "unused"),
        )


def test_manifest_rejects_dependency_deleted_during_pdf_inspection(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))
    dependency = tmp_path / "build/generated-index.tex"

    def delete_dependency(_snapshot: Path) -> tuple[int, None]:
        dependency.unlink()
        return 7, None

    with pytest.raises(
        inventory_module.InventoryError,
        match="generated_dependencies",
    ):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            pdfinfo_counter=delete_dependency,
            python_counter=lambda _path: (None, "unused"),
        )


def test_manifest_rejects_manifest_mutated_in_place_during_pdf_inspection(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))
    manifest_path = tmp_path / "audit/BUILD_MANIFEST.json"

    def mutate(_snapshot: Path) -> tuple[int, None]:
        manifest_path.write_text(
            json.dumps(_manifest(head, [])),
            encoding="utf-8",
        )
        return 7, None

    with pytest.raises(inventory_module.InventoryError, match="manifest|manifeste"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            pdfinfo_counter=mutate,
            python_counter=lambda _path: (None, "unused"),
        )


def test_manifest_rejects_head_advanced_during_pdf_inspection(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    def advance_head(_snapshot: Path) -> tuple[int, None]:
        subprocess.run(
            [
                "git",
                "-C",
                str(tmp_path),
                "-c",
                "user.name=Observed Build Tests",
                "-c",
                "user.email=observed@example.invalid",
                "commit",
                "--allow-empty",
                "-qm",
                "advance during observation",
            ],
            check=True,
        )
        return 7, None

    with pytest.raises(inventory_module.InventoryError, match="Git|git|provenance"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            pdfinfo_counter=advance_head,
            python_counter=lambda _path: (None, "unused"),
        )


def test_manifest_rejects_tracked_source_set_changed_during_pdf_inspection(
    tmp_path: Path,
    inventory_module,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    pdf_path = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    pdf_bytes = b"%PDF-1.7 observed build"
    target = tmp_path / pdf_path
    target.parent.mkdir(parents=True)
    target.write_bytes(pdf_bytes)
    build = _build(head, pdf_path, pdf_bytes)
    _write_manifest(tmp_path, _manifest(head, [build]))

    def add_source(_snapshot: Path) -> tuple[int, None]:
        source = tmp_path / "new-tracked-source.tex"
        source.write_text("new source", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(tmp_path), "add", source.name],
            check=True,
        )
        return 7, None

    with pytest.raises(inventory_module.InventoryError, match="sources suivies"):
        inventory_module._load_observed_build_manifest(
            tmp_path,
            source_digest=SHA256_A,
            model_digest=SHA256_B,
            declared_assemblies=[
                {
                    "manual": "1SPE",
                    "scope": "manual",
                    "variant": "professeur",
                }
            ],
            pdfinfo_counter=add_source,
            python_counter=lambda _path: (None, "unused"),
        )


@pytest.mark.parametrize("kind", ["symlink", "fifo", "hardlink"])
def test_loader_rejects_nonregular_manifest_control(
    tmp_path: Path,
    inventory_module,
    kind: str,
) -> None:
    head = _git_repository(tmp_path)
    _install_schema(tmp_path)
    audit = tmp_path / "audit"
    target = audit / "BUILD_MANIFEST.json"
    if kind == "symlink":
        external = tmp_path.parent / f"{tmp_path.name}-manifest.json"
        external.write_text(
            json.dumps(_manifest(head, [])),
            encoding="utf-8",
        )
        target.symlink_to(external)
    elif kind == "fifo":
        if not hasattr(os, "mkfifo"):
            pytest.skip("FIFO indisponible")
        os.mkfifo(target)
    else:
        external = tmp_path.parent / f"{tmp_path.name}-manifest-hardlink.json"
        external.write_text(
            json.dumps(_manifest(head, [])),
            encoding="utf-8",
        )
        os.link(external, target)

    with pytest.raises(inventory_module.InventoryError, match="manifest|manifeste"):
        _load(inventory_module, tmp_path)


def test_record_helper_refuses_failed_compile_or_preflight(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    build = _build(
        head,
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
        b"%PDF",
    )
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()

    with pytest.raises(manifest_module.BuildManifestError, match="compilation"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=False,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )
    with pytest.raises(manifest_module.BuildManifestError, match="préflight"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=False,
            validator=lambda _payload: None,
        )

    assert path.read_bytes() == original


@pytest.mark.parametrize("mutation", ["branch", "dirty"])
def test_record_helper_rejects_forged_repository_provenance(
    tmp_path: Path,
    manifest_module,
    mutation: str,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    forged = deepcopy(envelope)
    if mutation == "branch":
        forged["provenance"]["branch"] = "forged"  # type: ignore[index]
    else:
        forged["provenance"]["dirty"] = False  # type: ignore[index]
    build = _build(head, "build/manual.pdf", b"%PDF")

    with pytest.raises(manifest_module.BuildManifestError, match="provenance"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=forged,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert path.read_bytes() == original


def test_record_helper_merges_successful_build_atomically(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    build = _build(
        head,
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
        b"%PDF",
    )

    manifest_module.record_successful_build(
        path,
        build,
        envelope=envelope,
        compile_succeeded=True,
        preflight_succeeded=True,
        validator=lambda _payload: None,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["builds"] == [build]
    assert payload["build_state_digest"] == _state_digest([build])
    assert not list(path.parent.glob(f".{path.name}.*.tmp"))


def test_record_helper_can_version_manifest_from_clean_checkout(
    tmp_path: Path,
    manifest_module,
) -> None:
    stale_head = _git_repository(tmp_path)
    envelope = _manifest(stale_head, [])
    _write_manifest(tmp_path, envelope)
    dependency = tmp_path / "build/generated-index.tex"
    dependency.parent.mkdir(exist_ok=True)
    dependency.write_text("% generated dependency", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "audit", "build"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Observed Build Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "-qm",
            "tracked empty manifest",
        ],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    fresh_envelope = _manifest(head, [])
    fresh_envelope["provenance"]["dirty"] = False  # type: ignore[index]
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    build = _build(head, "build/MANUEL_1SPE_professeur.pdf", b"%PDF")

    manifest_module.record_successful_build(
        path,
        build,
        envelope=fresh_envelope,
        compile_succeeded=True,
        preflight_succeeded=True,
        validator=lambda _payload: None,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["builds"] == [build]
    status = subprocess.run(
        ["git", "-C", str(tmp_path), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert status.strip() == "M audit/BUILD_MANIFEST.json"


def test_record_helper_serializes_concurrent_distinct_variants(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    professor = _build(
        head,
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
        b"%PDF professor",
    )
    student = deepcopy(professor)
    student["variant"] = "eleve"
    student["pdf_path"] = (
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf"
    )
    student["pdf_sha256"] = "sha256:" + "c" * 64
    failures: list[BaseException] = []

    def record(build: dict[str, object]) -> None:
        try:
            manifest_module.record_successful_build(
                path,
                build,
                envelope=envelope,
                compile_succeeded=True,
                preflight_succeeded=True,
                validator=lambda _payload: None,
            )
        except BaseException as exc:  # pragma: no cover - asserted below
            failures.append(exc)

    threads = [
        threading.Thread(target=record, args=(professor,)),
        threading.Thread(target=record, args=(student,)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert failures == []
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert [build["variant"] for build in payload["builds"]] == [
        "eleve",
        "professeur",
    ]


def test_record_helper_detects_lock_substitution_without_lost_update(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    professor = _build(
        head,
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
        b"%PDF professor",
    )
    student = deepcopy(professor)
    student["variant"] = "eleve"
    student["pdf_path"] = (
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_eleve.pdf"
    )
    student["pdf_sha256"] = "sha256:" + "c" * 64
    professor_waiting = threading.Event()
    student_done = threading.Event()
    failures: list[tuple[str, BaseException]] = []

    def professor_validator(_payload: dict[str, object]) -> None:
        professor_waiting.set()
        assert student_done.wait(timeout=5)

    def record_professor() -> None:
        try:
            manifest_module.record_successful_build(
                path,
                professor,
                envelope=envelope,
                compile_succeeded=True,
                preflight_succeeded=True,
                validator=professor_validator,
            )
        except BaseException as exc:
            failures.append(("professeur", exc))

    professor_thread = threading.Thread(target=record_professor)
    professor_thread.start()
    assert professor_waiting.wait(timeout=5)
    lock_path = manifest_module._git_lock_path(tmp_path)
    lock_path.unlink()
    lock_path.touch(mode=0o600)

    try:
        manifest_module.record_successful_build(
            path,
            student,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )
    except BaseException as exc:
        failures.append(("eleve", exc))
    finally:
        student_done.set()
    professor_thread.join(timeout=5)

    assert [label for label, _exc in failures] == ["professeur"]
    assert "verrou" in str(failures[0][1]) or "destination" in str(
        failures[0][1]
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert [build["variant"] for build in payload["builds"]] == ["eleve"]


def test_record_helper_validates_before_replacement(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    build = _build(head, "build/manual.pdf", b"%PDF")
    original = path.read_bytes()

    def reject(_payload: dict[str, object]) -> None:
        raise ValueError("schéma invalide")

    with pytest.raises(manifest_module.BuildManifestError, match="validation"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=reject,
        )

    assert path.read_bytes() == original


def test_record_helper_rejects_manifest_symlink_without_touching_target(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    audit = tmp_path / "audit"
    audit.mkdir()
    marker = tmp_path / "build/.fixture-dirty"
    marker.parent.mkdir()
    marker.write_text("fixture", encoding="utf-8")
    external = tmp_path.parent / f"{tmp_path.name}-external-manifest.json"
    external.write_text(json.dumps(envelope), encoding="utf-8")
    path = audit / "BUILD_MANIFEST.json"
    path.symlink_to(external)
    original = external.read_bytes()
    build = _build(head, "build/manual.pdf", b"%PDF")

    with pytest.raises(manifest_module.BuildManifestError, match="symbolique"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert external.read_bytes() == original


def test_record_helper_rejects_manifest_hardlink(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    audit = tmp_path / "audit"
    audit.mkdir()
    marker = tmp_path / "build/.fixture-dirty"
    marker.parent.mkdir()
    marker.write_text("fixture", encoding="utf-8")
    external = tmp_path.parent / f"{tmp_path.name}-hardlink-manifest.json"
    external.write_text(json.dumps(envelope), encoding="utf-8")
    path = audit / "BUILD_MANIFEST.json"
    os.link(external, path)
    original = external.read_bytes()
    build = _build(head, "build/manual.pdf", b"%PDF")

    with pytest.raises(manifest_module.BuildManifestError, match="lien|régulier"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert external.read_bytes() == original


def test_record_helper_does_not_leave_adjacent_lock(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    build = _build(head, "build/manual.pdf", b"%PDF")

    manifest_module.record_successful_build(
        path,
        build,
        envelope=envelope,
        compile_succeeded=True,
        preflight_succeeded=True,
        validator=lambda _payload: None,
    )

    assert not path.with_suffix(path.suffix + ".lock").exists()


def test_record_helper_rolls_back_if_parent_is_substituted(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    audit = tmp_path / "audit"
    path = audit / "BUILD_MANIFEST.json"
    original = path.read_bytes()
    external_audit = tmp_path.parent / f"{tmp_path.name}-external-audit"
    external_audit.mkdir()
    external_manifest = external_audit / "BUILD_MANIFEST.json"
    external_manifest.write_bytes(original)
    external_original = external_manifest.read_bytes()
    parked = tmp_path / "audit-parked"
    real_replace = manifest_module.os.replace
    attacked = False

    def substitute_parent(
        source: str,
        destination: str,
        *,
        src_dir_fd: int,
        dst_dir_fd: int,
    ) -> None:
        nonlocal attacked
        if destination == "BUILD_MANIFEST.json" and not attacked:
            attacked = True
            audit.rename(parked)
            audit.symlink_to(external_audit, target_is_directory=True)
        real_replace(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
        )

    monkeypatch.setattr(manifest_module.os, "replace", substitute_parent)
    build = _build(head, "build/manual.pdf", b"%PDF")

    with pytest.raises(manifest_module.BuildManifestError, match="parent modifié"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert external_manifest.read_bytes() == external_original
    assert (parked / "BUILD_MANIFEST.json").read_bytes() == original


def test_record_helper_rolls_back_when_directory_fsync_fails_after_replace(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    build = _build(head, "build/manual.pdf", b"%PDF")
    real_fsync = manifest_module.os.fsync
    failed = False

    def fail_first_directory_fsync(descriptor: int) -> None:
        nonlocal failed
        metadata = os.fstat(descriptor)
        if stat.S_ISDIR(metadata.st_mode) and not failed:
            failed = True
            raise OSError(errno.EIO, "simulated directory fsync failure")
        real_fsync(descriptor)

    monkeypatch.setattr(manifest_module.os, "fsync", fail_first_directory_fsync)

    with pytest.raises(manifest_module.BuildManifestError, match="transaction"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert failed is True
    assert path.read_bytes() == original


def test_record_helper_rejects_same_size_in_place_lost_update(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    mutated = original.replace(b"build_manifest.py", b"build_manifest.px")
    assert len(mutated) == len(original)
    build = _build(head, "build/manual.pdf", b"%PDF")
    real_parent_check = manifest_module._parent_is_pinned
    attacked = False

    def mutate_then_check(
        root_descriptor: int,
        audit_fingerprint: tuple[int, int, int],
    ) -> bool:
        nonlocal attacked
        if not attacked:
            attacked = True
            path.write_bytes(mutated)
        return real_parent_check(root_descriptor, audit_fingerprint)

    monkeypatch.setattr(
        manifest_module,
        "_parent_is_pinned",
        mutate_then_check,
    )

    with pytest.raises(manifest_module.BuildManifestError, match="destination"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert attacked is True
    assert path.read_bytes() == mutated


def test_record_helper_rejects_source_mutation_while_worktree_stays_dirty(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    source = tmp_path / "tracked-source.tex"
    source.write_text("initial", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked-source.tex"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Observed Build Tests",
            "-c",
            "user.email=observed@example.invalid",
            "commit",
            "-qm",
            "tracked source",
        ],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source.write_text("dirty-before", encoding="utf-8")
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    build = _build(head, "build/manual.pdf", b"%PDF")

    def mutate_source(_payload: dict[str, object]) -> None:
        source.write_text("dirty-after", encoding="utf-8")

    with pytest.raises(manifest_module.BuildManifestError, match="destination"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=mutate_source,
        )

    assert path.read_bytes() == original
    assert source.read_text(encoding="utf-8") == "dirty-after"


def test_record_helper_refreshes_envelope_provenance_for_current_head(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    stale_envelope = _manifest("0" * 40, [])
    fresh_envelope = _manifest(head, [])
    _write_manifest(tmp_path, stale_envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    build = _build(head, "build/manual.pdf", b"%PDF")

    manifest_module.record_successful_build(
        path,
        build,
        envelope=fresh_envelope,
        compile_succeeded=True,
        preflight_succeeded=True,
        validator=lambda _payload: None,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["provenance"] == fresh_envelope["provenance"]


def test_record_helper_rejects_corrupt_current_state_digest(
    tmp_path: Path,
    manifest_module,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    envelope["build_state_digest"] = "sha256:" + "0" * 64
    _write_manifest(tmp_path, envelope)
    path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = path.read_bytes()
    fresh_envelope = _manifest(head, [])
    build = _build(head, "build/manual.pdf", b"%PDF")

    with pytest.raises(manifest_module.BuildManifestError, match="digest"):
        manifest_module.record_successful_build(
            path,
            build,
            envelope=fresh_envelope,
            compile_succeeded=True,
            preflight_succeeded=True,
            validator=lambda _payload: None,
        )

    assert path.read_bytes() == original


def test_receipt_derivation_recomputes_all_derived_evidence(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, _paths, source_commit, source_date_epoch = (
        _install_receipt_evidence(tmp_path, manifest_module, monkeypatch)
    )
    head = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    envelope, build, validator = manifest_module._derive_receipt_evidence(
        tmp_path,
        receipt,
    )

    assert envelope["source_digest"] == SHA256_A
    assert envelope["model_digest"] == SHA256_B
    assert envelope["provenance"] == {
        "branch": "master",
        "dirty": True,
        "head_sha": head,
    }
    assert build["git_sha"] == head
    assert build["source_digest"] == SHA256_A
    assert build["model_digest"] == SHA256_B
    assert build["pdf_sha256"] == receipt["evidence_sha256"]["pdf"]
    assert build["page_count"] == 11
    assert build["included_objects"] == ["OBJ-2", "OBJ-1"]
    assert build["excluded_objects"] == ["OBJ-EXCLUDED"]
    assert build["ordered_trace"] == ["OBJ-2", "OBJ-1"]
    assert build["tool_versions"] == TOOL_VERSIONS
    assert build["reproducibility"] == _reproducibility(
        source_commit,
        source_date_epoch,
    )
    proposed = dict(envelope)
    proposed["builds"] = [build]
    proposed["build_state_digest"] = _state_digest([build])
    validator(proposed)


def _refresh_receipt_digest(
    receipt: dict[str, object],
    paths: dict[str, Path],
    name: str,
) -> None:
    digests = receipt["evidence_sha256"]
    assert isinstance(digests, dict)
    digests[name] = "sha256:" + hashlib.sha256(paths[name].read_bytes()).hexdigest()


def _rewrite_preflight_reproducibility(
    receipt: dict[str, object],
    paths: dict[str, Path],
    reproducibility: dict[str, object],
) -> None:
    preflight = json.loads(paths["preflight"].read_text(encoding="utf-8"))
    preflight["reproducibility"] = reproducibility
    paths["preflight"].write_text(json.dumps(preflight), encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, "preflight")


@pytest.mark.parametrize("mutation", ["missing", "extra"])
def test_receipt_reader_requires_exact_closed_shape(
    tmp_path: Path,
    manifest_module,
    mutation: str,
) -> None:
    _git_repository(tmp_path)
    payload = _receipt()
    if mutation == "missing":
        del payload["run_id"]
    else:
        payload["unexpected"] = True
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(manifest_module.BuildManifestError, match="champs"):
        manifest_module._read_receipt(receipt, tmp_path)


def test_receipt_reader_accepts_new_closed_shape(
    tmp_path: Path,
    manifest_module,
) -> None:
    _git_repository(tmp_path)
    payload = _receipt()
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    assert manifest_module._read_receipt(receipt, tmp_path) == payload


@pytest.mark.parametrize(
    ("mutation", "name"),
    [
        ("missing", "master"),
        ("missing", "log"),
        ("missing", "fls"),
        ("missing", "pdf"),
        ("missing", "preflight"),
        ("malformed", "master"),
        ("malformed", "log"),
        ("malformed", "fls"),
        ("malformed", "pdf"),
        ("malformed", "preflight"),
        ("wrong", "master"),
        ("wrong", "log"),
        ("wrong", "fls"),
        ("wrong", "pdf"),
        ("wrong", "preflight"),
        ("extra", "foreign"),
    ],
)
def test_receipt_rejects_incomplete_or_forged_evidence_digests(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    name: str,
) -> None:
    receipt, _paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    digests = receipt["evidence_sha256"]
    assert isinstance(digests, dict)
    if mutation == "missing":
        del digests[name]
    elif mutation == "extra":
        digests[name] = SHA256_A
    elif mutation == "malformed":
        digests[name] = "SHA256:" + "0" * 64
    else:
        digests[name] = "sha256:" + "0" * 64

    with pytest.raises(
        manifest_module.BuildManifestError,
        match="empreinte|digest|evidence",
    ):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize("run_id", ["0" * 31, "0" * 33, "G" * 32, 7, True])
def test_receipt_rejects_malformed_run_id(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    run_id: object,
) -> None:
    receipt, _paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    receipt["run_id"] = run_id

    with pytest.raises(manifest_module.BuildManifestError, match="run_id"):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize(
    ("surface", "mutation"),
    [
        ("master", "missing"),
        ("master", "duplicate"),
        ("master", "foreign"),
        ("log", "missing"),
        ("log", "duplicate"),
        ("log", "foreign"),
        ("preflight", "missing"),
        ("preflight", "foreign"),
    ],
)
def test_receipt_rejects_run_marker_mismatch_or_duplication(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    surface: str,
    mutation: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    if surface == "preflight":
        report = json.loads(paths["preflight"].read_text(encoding="utf-8"))
        if mutation == "missing":
            del report["run_id"]
        else:
            report["run_id"] = "f" * 32
        paths["preflight"].write_text(json.dumps(report), encoding="utf-8")
    else:
        marker = f"NEXUS_BUILD_RUN:{RUN_ID}"
        payload = paths[surface].read_text(encoding="utf-8")
        if mutation == "missing":
            payload = payload.replace(marker, "")
        elif mutation == "duplicate":
            payload += f"\n{marker}\n"
        else:
            payload += f"\nNEXUS_BUILD_RUN:{'f' * 32}\n"
        paths[surface].write_text(payload, encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, surface)

    with pytest.raises(
        manifest_module.BuildManifestError,
        match="run_id|marqueur|préflight",
    ):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize("surface", ["master", "log"])
@pytest.mark.parametrize(
    "mutation",
    ["underscore_suffix", "hyphen_suffix", "line_prefix", "line_suffix"],
)
def test_receipt_requires_exact_full_run_marker_line(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    surface: str,
    mutation: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    marker = f"NEXUS_BUILD_RUN:{RUN_ID}"
    payload = paths[surface].read_text(encoding="utf-8")
    if mutation == "underscore_suffix":
        payload = payload.replace(marker, f"{marker}_forged")
    elif mutation == "hyphen_suffix":
        payload = payload.replace(marker, f"{marker}-forged")
    elif mutation == "line_prefix":
        payload = payload.replace(marker, f"forged {marker}")
    else:
        payload = payload.replace(marker, f"{marker} forged")
    paths[surface].write_text(payload, encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, surface)

    with pytest.raises(manifest_module.BuildManifestError, match="marqueur|run_id"):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


def test_receipt_requires_master_in_fls_inputs(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    master_line = f"INPUT {receipt['master_path']}\n"
    fls = paths["fls"].read_text(encoding="utf-8")
    paths["fls"].write_text(fls.replace(master_line, ""), encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, "fls")

    with pytest.raises(manifest_module.BuildManifestError, match="master|maître"):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


def test_external_absolute_texlive_fls_input_is_ignored(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, _paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )

    _envelope, build, _validator = manifest_module._derive_receipt_evidence(
        tmp_path,
        receipt,
    )

    assert build["included_objects"] == ["OBJ-2", "OBJ-1"]
    assert not any(
        str(value).startswith("/usr/share/texlive")
        for value in build["included_objects"]
    )


@pytest.mark.parametrize("kind", ["missing", "symlink", "hardlink"])
def test_receipt_confines_every_traced_object_proof(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    target = paths["object_2"]
    payload = target.read_bytes()
    target.unlink()
    if kind != "missing":
        external = tmp_path / "external-object-2.tex"
        external.write_bytes(payload)
        if kind == "symlink":
            target.symlink_to(external)
        else:
            os.link(external, target)

    with pytest.raises(
        manifest_module.BuildManifestError,
        match="objet|inaccessible|symbolique|hardlink",
    ):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


def test_final_validator_rejects_traced_object_drift(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    envelope, build, validator = manifest_module._derive_receipt_evidence(
        tmp_path,
        receipt,
    )
    paths["object_2"].write_text("objet 2 forgé", encoding="utf-8")
    proposed = dict(envelope)
    proposed["builds"] = [build]
    proposed["build_state_digest"] = _state_digest([build])

    with pytest.raises(manifest_module.BuildManifestError, match="objet|modifié"):
        validator(proposed)


@pytest.mark.parametrize("field", ["master_path", "log_path"])
@pytest.mark.parametrize(
    "kind",
    ["symlink", "hardlink", "absolute", "backslash", "dot", "parent"],
)
def test_receipt_rejects_unsafe_master_and_proof_paths(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    kind: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    name = "master" if field == "master_path" else "log"
    target = paths[name]
    if kind in {"symlink", "hardlink"}:
        payload = target.read_bytes()
        target.unlink()
        external = tmp_path / f"external-{name}"
        external.write_bytes(payload)
        if kind == "symlink":
            target.symlink_to(external)
        else:
            os.link(external, target)
    elif kind == "absolute":
        receipt[field] = str(target)
    elif kind == "backslash":
        receipt[field] = str(receipt[field]).replace("/", "\\")
    elif kind == "dot":
        raw = str(receipt[field])
        parent, separator, leaf = raw.rpartition("/")
        receipt[field] = f"{parent}{separator}./{leaf}"
    else:
        raw = str(receipt[field])
        parent, separator, leaf = raw.rpartition("/")
        receipt[field] = f"{parent}{separator}../{parent.rsplit('/', 1)[-1]}/{leaf}"

    with pytest.raises(
        manifest_module.BuildManifestError,
        match="canonique|symbolique|hardlink|régulier|inaccessible",
    ):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "receipt_mismatch", "preflight_mismatch"],
)
def test_receipt_rejects_missing_forged_or_mismatched_tool_versions(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    report = json.loads(paths["preflight"].read_text(encoding="utf-8"))
    if mutation == "missing":
        del receipt["tool_versions"]["pdffonts"]  # type: ignore[index]
        del report["tool_versions"]["pdffonts"]
    elif mutation == "extra":
        receipt["tool_versions"]["foreign"] = "forged"  # type: ignore[index]
        report["tool_versions"]["foreign"] = "forged"
    elif mutation == "receipt_mismatch":
        receipt["tool_versions"]["pdfinfo"] = "forged"  # type: ignore[index]
    else:
        report["tool_versions"]["pdfinfo"] = "forged"
    paths["preflight"].write_text(json.dumps(report), encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, "preflight")

    with pytest.raises(manifest_module.BuildManifestError, match="tool|outil|version"):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


def test_tool_version_collection_uses_exact_commands_and_sanitized_environment(
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], dict[str, str], int]] = []
    outputs = {
        "lualatex": "  LuaHBTeX,   Version 1.17.0\nsecond line",
        "pdfinfo": "pdfinfo version 24.02.0",
        "pdffonts": "pdffonts version 24.02.0",
        sys.executable: f"Python {sys.version.split()[0]}",
    }

    def run(command: list[str], **kwargs):
        calls.append((command, kwargs["env"], kwargs["timeout"]))
        return SimpleNamespace(
            returncode=0,
            stdout=outputs[command[0]],
            stderr="",
        )

    monkeypatch.setattr(manifest_module.subprocess, "run", run)
    monkeypatch.setenv("UNSAFE_BUILD_FLAG", "forged")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")

    versions = manifest_module._collect_local_tool_versions(
        _reproducibility("c" * 40, 123456789)
    )

    assert versions == TOOL_VERSIONS
    assert [command for command, _env, _timeout in calls] == [
        ["lualatex", "--version"],
        ["pdfinfo", "-v"],
        ["pdffonts", "-v"],
        [sys.executable, "--version"],
    ]
    for _command, environment, timeout in calls:
        assert timeout == 20
        assert environment == {
            name: value
            for name, value in {
                "PATH": os.environ.get("PATH"),
                "HOME": os.environ.get("HOME"),
                "FORCE_SOURCE_DATE": "1",
                "TZ": "UTC",
                "LC_ALL": "C.UTF-8",
                "PYTHONHASHSEED": "0",
                "SOURCE_DATE_EPOCH": "123456789",
            }.items()
            if value is not None
        }


def test_git_commands_strip_override_environment(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environments: list[dict[str, str] | None] = []

    def run(_command: list[str], **kwargs):
        environments.append(kwargs.get("env"))
        return SimpleNamespace(returncode=0, stdout="c" * 40, stderr="")

    monkeypatch.setattr(manifest_module.subprocess, "run", run)
    monkeypatch.setenv("GIT_DIR", "/forged")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")

    assert manifest_module._git_head(tmp_path) == "c" * 40
    assert environments == [
        {
            name: os.environ[name]
            for name in ("PATH", "HOME")
            if name in os.environ
        }
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        "absent",
        "unsafe",
        "malformed",
        "untracked",
        "receipt_mismatch",
        "preflight_mismatch",
        "source_commit_missing",
        "source_commit_absent",
        "source_commit_nonancestor",
        "epoch_mismatch",
    ],
)
def test_receipt_rejects_invalid_reproducibility_control(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    receipt, paths, source_commit, epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    config = paths["config"]
    if mutation == "absent":
        config.unlink()
    elif mutation == "unsafe":
        payload = config.read_bytes()
        config.unlink()
        external = tmp_path / "external-reproducibility.json"
        external.write_bytes(payload)
        config.symlink_to(external)
    elif mutation == "malformed":
        config.write_text(
            json.dumps(
                {
                    "schema_version": True,
                    "source_commit": source_commit,
                    "source_date_epoch": epoch,
                }
            ),
            encoding="utf-8",
        )
    elif mutation == "untracked":
        subprocess.run(
            [
                "git",
                "-C",
                str(tmp_path),
                "update-index",
                "--force-remove",
                REPRO_CONFIG_PATH,
            ],
            check=True,
        )
    elif mutation == "receipt_mismatch":
        receipt["reproducibility"] = {
            **receipt["reproducibility"],  # type: ignore[arg-type]
            "timezone": "Europe/Paris",
        }
    elif mutation == "preflight_mismatch":
        _rewrite_preflight_reproducibility(
            receipt,
            paths,
            {
                **receipt["reproducibility"],  # type: ignore[arg-type]
                "timezone": "Europe/Paris",
            },
        )
    else:
        control = json.loads(config.read_text(encoding="utf-8"))
        if mutation == "source_commit_missing":
            del control["source_commit"]
        elif mutation == "source_commit_absent":
            control["source_commit"] = "0" * 40
        elif mutation == "source_commit_nonancestor":
            foreign = subprocess.run(
                [
                    "git",
                    "-C",
                    str(tmp_path),
                    "-c",
                    "user.name=Observed Build Tests",
                    "-c",
                    "user.email=observed@example.invalid",
                    "commit-tree",
                    "HEAD^{tree}",
                    "-m",
                    "foreign commit",
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            control["source_commit"] = foreign
            control["source_date_epoch"] = _git_timestamp(tmp_path, foreign)
        else:
            control["source_date_epoch"] = epoch + 1
        config.write_text(json.dumps(control), encoding="utf-8")
        if mutation != "source_commit_missing":
            reproducibility = _reproducibility(
                control["source_commit"],
                control["source_date_epoch"],
            )
            receipt["reproducibility"] = reproducibility
            _rewrite_preflight_reproducibility(receipt, paths, reproducibility)

    with pytest.raises(
        manifest_module.BuildManifestError,
        match="reproductibilité|source_commit|source_date_epoch|suivi|config",
    ):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize("mutation", ["missing", "extra"])
def test_preflight_report_requires_exact_closed_shape(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    report = json.loads(paths["preflight"].read_text(encoding="utf-8"))
    if mutation == "missing":
        del report["page_count"]
    else:
        report["unexpected"] = True
    paths["preflight"].write_text(json.dumps(report), encoding="utf-8")
    _refresh_receipt_digest(receipt, paths, "preflight")

    with pytest.raises(manifest_module.BuildManifestError, match="préflight|champs"):
        manifest_module._derive_receipt_evidence(tmp_path, receipt)


@pytest.mark.parametrize(
    "name",
    ["master", "log", "fls", "pdf", "preflight", "config"],
)
def test_final_validator_rejects_any_proof_drift(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> None:
    receipt, paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    envelope, build, validator = manifest_module._derive_receipt_evidence(
        tmp_path,
        receipt,
    )
    paths[name].write_bytes(paths[name].read_bytes() + b"\nforged")
    proposed = dict(envelope)
    proposed["builds"] = [build]
    proposed["build_state_digest"] = _state_digest([build])

    with pytest.raises(manifest_module.BuildManifestError, match="modifié|preuve"):
        validator(proposed)


def test_final_validator_rejects_tool_version_drift(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt, _paths, _source_commit, _epoch = _install_receipt_evidence(
        tmp_path,
        manifest_module,
        monkeypatch,
    )
    calls = 0

    def versions(_reproducibility: dict[str, object]) -> dict[str, str]:
        nonlocal calls
        calls += 1
        if calls == 1:
            return dict(TOOL_VERSIONS)
        return {**TOOL_VERSIONS, "pdfinfo": "pdfinfo version forged"}

    monkeypatch.setattr(manifest_module, "_collect_local_tool_versions", versions)
    envelope, build, validator = manifest_module._derive_receipt_evidence(
        tmp_path,
        receipt,
    )
    proposed = dict(envelope)
    proposed["builds"] = [build]
    proposed["build_state_digest"] = _state_digest([build])

    with pytest.raises(manifest_module.BuildManifestError, match="outil|version"):
        validator(proposed)


def test_ordered_object_trace_uses_markers_not_fls_order(
    manifest_module,
) -> None:
    log = "\n".join(
        [
            _trace_marker("BEGIN", "chapitres/objet-2.tex"),
            _trace_marker("END", "chapitres/objet-2.tex"),
            _trace_marker("BEGIN", "chapitres/objet-1.tex"),
            _trace_marker("END", "chapitres/objet-1.tex"),
        ]
    )

    trace = manifest_module._ordered_object_trace(
        log,
        traced_inputs=[
            "chapitres/objet-1.tex",
            "chapitres/non-marque.tex",
            "chapitres/objet-2.tex",
        ],
        declared_objects=[
            "chapitres/objet-1.tex",
            "chapitres/objet-2.tex",
            "chapitres/non-marque.tex",
        ],
    )

    assert trace == [
        "chapitres/objet-2.tex",
        "chapitres/objet-1.tex",
    ]


def test_ordered_object_trace_accepts_real_lualatex_log_for_long_paths(
    tmp_path: Path,
    manifest_module,
) -> None:
    objects = [
        (
            "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/"
            "exercices/1SPE-DERLOCAL-EX-001.tex"
        ),
        (
            "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/"
            "exercices/1SPE-DERLOCAL-EX-002.tex"
        ),
    ]
    for number, relative in enumerate(objects, start=1):
        source = tmp_path / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"Objet {number}.\n", encoding="utf-8")
    master = tmp_path / "trace-longue.tex"
    blocks = "\n".join(
        "\n".join(
            [
                rf"\typeout{{NEXUS_OBJECT_BEGIN:{_trace_token(path)}}}",
                rf"\input{{{path}}}",
                rf"\typeout{{NEXUS_OBJECT_END:{_trace_token(path)}}}",
            ]
        )
        for path in reversed(objects)
    )
    master.write_text(
        "\n".join(
            [
                r"\documentclass{article}",
                r"\begin{document}",
                blocks,
                r"\end{document}",
            ]
        ),
        encoding="utf-8",
    )
    build = tmp_path / "build"
    build.mkdir()

    completed = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-recorder",
            f"-output-directory={build}",
            str(master),
        ],
        cwd=tmp_path,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    log = (build / "trace-longue.log").read_text(encoding="utf-8")
    traced_inputs = []
    for line in (build / "trace-longue.fls").read_text(
        encoding="utf-8"
    ).splitlines():
        kind, separator, raw = line.partition(" ")
        if kind != "INPUT" or not separator:
            continue
        normalized = manifest_module._canonical_fls_path(tmp_path, raw.strip())
        if normalized is not None:
            traced_inputs.append(normalized)
    assert set(objects) <= set(traced_inputs)

    trace = manifest_module._ordered_object_trace(
        log,
        traced_inputs=traced_inputs,
        declared_objects=objects,
    )

    assert trace == list(reversed(objects))


@pytest.mark.parametrize(
    ("log", "traced_inputs", "declared_objects", "message"),
    [
        ("journal sans marqueur", ["objet.tex"], ["objet.tex"], "absents"),
        (
            _trace_marker("END", "objet.tex"),
            ["objet.tex"],
            ["objet.tex"],
            "ordre",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("BEGIN", "autre.tex"),
                    _trace_marker("END", "autre.tex"),
                    _trace_marker("END", "objet.tex"),
                ]
            ),
            ["objet.tex", "autre.tex"],
            ["objet.tex", "autre.tex"],
            "ordre",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("END", "autre.tex"),
                ]
            ),
            ["objet.tex", "autre.tex"],
            ["objet.tex", "autre.tex"],
            "identité",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("END", "objet.tex"),
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("END", "objet.tex"),
                ]
            ),
            ["objet.tex"],
            ["objet.tex"],
            "dupliqué",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("END", "objet.tex"),
                ]
            ),
            ["autre.tex"],
            ["objet.tex", "autre.tex"],
            "FLS",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "objet.tex"),
                    _trace_marker("END", "objet.tex"),
                ]
            ),
            ["objet.tex"],
            ["autre.tex"],
            "déclaré",
        ),
        (
            "\n".join(
                [
                    "NEXUS_OBJECT_BEGIN:identifiant-invalide",
                    "NEXUS_OBJECT_END:identifiant-invalide",
                ]
            ),
            ["objet.tex"],
            ["objet.tex"],
            "identifiant",
        ),
        (
            "\n".join(
                [
                    _trace_marker("BEGIN", "../objet.tex"),
                    _trace_marker("END", "../objet.tex"),
                ]
            ),
            ["../objet.tex"],
            ["../objet.tex"],
            "canonique",
        ),
    ],
)
def test_ordered_object_trace_rejects_invalid_evidence(
    manifest_module,
    log: str,
    traced_inputs: list[str],
    declared_objects: list[str],
    message: str,
) -> None:
    with pytest.raises(manifest_module.BuildManifestError, match=message):
        manifest_module._ordered_object_trace(
            log,
            traced_inputs=traced_inputs,
            declared_objects=declared_objects,
        )


def test_receipt_entrypoint_refuses_publication_without_build_wrapper(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    receipt_path = tmp_path / "build/build-receipt.json"
    receipt_path.parent.mkdir(exist_ok=True)
    receipt_path.write_text(json.dumps(_receipt()), encoding="utf-8")
    build = _build(
        head,
        "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf",
        b"%PDF",
    )
    monkeypatch.setattr(
        manifest_module,
        "_derive_receipt_evidence",
        lambda _root, _receipt_payload: (
            envelope,
            build,
            lambda _payload: None,
        ),
    )

    original = (tmp_path / "audit/BUILD_MANIFEST.json").read_bytes()
    with pytest.raises(manifest_module.BuildManifestError, match="non activée"):
        manifest_module.record_from_receipt(receipt_path)

    assert (tmp_path / "audit/BUILD_MANIFEST.json").read_bytes() == original


def test_receipt_cli_rejects_failed_build_without_writing(
    tmp_path: Path,
) -> None:
    head = _git_repository(tmp_path)
    envelope = _manifest(head, [])
    _write_manifest(tmp_path, envelope)
    manifest_path = tmp_path / "audit/BUILD_MANIFEST.json"
    original = manifest_path.read_bytes()
    receipt_path = tmp_path / "build/failed-receipt.json"
    receipt_path.parent.mkdir(exist_ok=True)
    receipt_path.write_text(
        json.dumps(_receipt(compile_succeeded=False)),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(MANIFEST_SCRIPT),
            "--receipt",
            str(receipt_path),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 2
    assert "compilation" in completed.stderr
    assert manifest_path.read_bytes() == original


def test_refresh_cli_subprocess_reports_success_without_receipt(
    tmp_path: Path,
) -> None:
    loader = (
        "import importlib.util, pathlib; "
        f"p=pathlib.Path({str(MANIFEST_SCRIPT)!r}); "
        "s=importlib.util.spec_from_file_location('refresh_cli_test', p); "
        "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        "m.refresh_empty_manifest=lambda _path: None; "
        "raise SystemExit(m._run(['--refresh-empty']))"
    )

    completed = subprocess.run(
        [sys.executable, "-c", loader],
        cwd=tmp_path,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stdout.strip() == "build manifest vide rafraîchi"
    assert completed.stderr == ""


def test_refresh_cli_is_mutually_exclusive_with_receipt(
    tmp_path: Path,
) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(MANIFEST_SCRIPT),
            "--refresh-empty",
            "--receipt",
            "build/receipt.json",
        ],
        cwd=tmp_path,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 2
    assert "not allowed with argument" in completed.stderr


@pytest.mark.parametrize(
    ("filename", "role"),
    [
        ("manual.log", "journal LaTeX"),
        ("manual.fls", "traceur FLS"),
        ("preflight.json", "rapport de préflight"),
    ],
)
def test_proof_reader_rejects_parent_substitution(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    role: str,
) -> None:
    build = tmp_path / "build"
    build.mkdir()
    (build / filename).write_text("trusted", encoding="utf-8")
    external = tmp_path / "external-build"
    external.mkdir()
    (external / filename).write_text("forged", encoding="utf-8")
    parked = tmp_path / "build-parked"
    real_open = manifest_module.os.open
    attacked = False

    def substitute_parent(path, flags, *args, **kwargs):
        nonlocal attacked
        if path == filename and not attacked:
            attacked = True
            build.rename(parked)
            build.symlink_to(external, target_is_directory=True)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(manifest_module.os, "open", substitute_parent)

    with pytest.raises(manifest_module.BuildManifestError, match="parent"):
        manifest_module._read_proof_file(
            tmp_path,
            f"build/{filename}",
            role=role,
        )

    assert attacked is True


def test_receipt_reader_rejects_parent_substitution(
    tmp_path: Path,
    manifest_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    build = tmp_path / "build"
    build.mkdir()
    receipt = build / "receipt.json"
    receipt.write_text(json.dumps(_receipt()), encoding="utf-8")
    external = tmp_path / "external-build"
    external.mkdir()
    (external / "receipt.json").write_text(
        json.dumps(_receipt()),
        encoding="utf-8",
    )
    parked = tmp_path / "build-parked"
    real_open = manifest_module.os.open
    attacked = False

    def substitute_parent(path, flags, *args, **kwargs):
        nonlocal attacked
        if path == "receipt.json" and not attacked:
            attacked = True
            build.rename(parked)
            build.symlink_to(external, target_is_directory=True)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(manifest_module.os, "open", substitute_parent)

    with pytest.raises(manifest_module.BuildManifestError, match="parent"):
        manifest_module._read_receipt(receipt, tmp_path)

    assert attacked is True
