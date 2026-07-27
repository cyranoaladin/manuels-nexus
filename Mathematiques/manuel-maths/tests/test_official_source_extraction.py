from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import signal
import shutil
import stat
import subprocess
import sys

import yaml
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_official_source.py"
REGISTRY = ROOT / "sources" / "registry.yaml"
SOURCE = ROOT / "sources" / "BO2026_1SPE_specialite.pdf"
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
)
EXPECTED_TEXT_SHA256 = (
    "4e70f1989cdb47caf184cb138d839799e895fcdc5addec3737f0216b6bfa33df"
)
EXPERIMENT_LINES = (
    "Simuler une variable aléatoire avec Python ou un tableur.",
    "Lire, comprendre et écrire une fonction Python renvoyant la moyenne",
    "Étudier sur des exemples la distance entre la moyenne",
    "Simuler, avec Python ou un tableur, N échantillons",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def official_entry() -> dict:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return next(
        source
        for source in registry["sources"]
        if source["id"] == "SRC-BO2026-1SPE-MATHS"
    )


@pytest.fixture
def extractor_module():
    spec = importlib.util.spec_from_file_location("extract_official_source", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_extractor(
    source: Path,
    output: Path,
    cwd: Path,
    registry: Path = REGISTRY,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source",
            str(source),
            "--output",
            str(output),
            "--registry",
            str(registry),
        ],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_registry_pins_the_official_2026_source() -> None:
    entry = official_entry()
    assert entry["nor"] == "MENE2602917A"
    assert entry["decree_date"] == "2026-02-26"
    assert entry["publication_date"] == "2026-03-27"
    assert entry["bo_date"] == "2026-04-02"
    assert entry["normative_from"] == "2026-09-01"
    assert entry["sha256"] == EXPECTED_PDF_SHA256
    assert entry["local_path"] == "sources/BO2026_1SPE_specialite.pdf"
    assert entry["normative"] is True


def test_two_real_extractions_are_identical_and_cwd_independent(tmp_path: Path) -> None:
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    first = tmp_path / "first" / "programme.txt"
    second = tmp_path / "second" / "programme.txt"
    unrelated_cwd = tmp_path / "unrelated cwd"
    unrelated_cwd.mkdir()

    first_result = run_extractor(SOURCE, first, unrelated_cwd)
    second_result = run_extractor(SOURCE, second, unrelated_cwd)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    assert first.read_bytes() == second.read_bytes()
    extracted = first.read_text(encoding="utf-8")
    assert "\r" not in extracted
    assert all(line in extracted for line in EXPERIMENT_LINES)
    assert stat.S_IMODE(first.stat().st_mode) == 0o644


def test_default_source_and_registry_do_not_depend_on_cwd(tmp_path: Path) -> None:
    unrelated_cwd = tmp_path / "unrelated"
    unrelated_cwd.mkdir()
    output = tmp_path / "programme.txt"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output)],
        cwd=unrelated_cwd,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    assert output.read_bytes() == (
        ROOT / "sources" / "txt" / "BO2026_1SPE_specialite.txt"
    ).read_bytes()


def test_wrong_source_hash_is_rejected_without_replacing_output(tmp_path: Path) -> None:
    wrong_source = tmp_path / "wrong.pdf"
    wrong_source.write_bytes(b"%PDF-1.7\nnot the official source\n")
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(wrong_source)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    output = tmp_path / "programme.txt"
    output.write_text("last known valid output\n", encoding="utf-8")

    result = run_extractor(wrong_source, output, tmp_path, registry)

    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "last known valid output\n"
    assert "SHA-256" in result.stderr


def test_output_cannot_replace_a_regular_registered_source(tmp_path: Path) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    before = sha256(source_copy)

    result = run_extractor(source_copy, source_copy, tmp_path, registry)

    assert result.returncode == 2
    assert sha256(source_copy) == before == EXPECTED_PDF_SHA256
    assert "source" in result.stderr.lower()


def test_output_cannot_replace_the_resolved_target_of_registered_source_symlink(
    tmp_path: Path,
) -> None:
    resolved_source = tmp_path / "official-target.pdf"
    shutil.copyfile(SOURCE, resolved_source)
    registered_source = tmp_path / "official-link.pdf"
    registered_source.symlink_to(resolved_source)
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(registered_source)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    before = resolved_source.read_bytes()

    result = run_extractor(
        registered_source,
        registered_source.resolve(),
        tmp_path,
        registry,
    )

    assert result.returncode == 2
    assert resolved_source.read_bytes() == before
    assert registered_source.is_symlink()
    assert "source" in result.stderr.lower()


def test_output_hardlink_alias_of_registered_source_is_rejected(
    tmp_path: Path,
) -> None:
    registered_source = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, registered_source)
    output_alias = tmp_path / "programme.txt"
    os.link(registered_source, output_alias)
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(registered_source)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    before = registered_source.read_bytes()

    result = run_extractor(registered_source, output_alias, tmp_path, registry)

    assert result.returncode == 2
    assert registered_source.read_bytes() == before
    assert output_alias.read_bytes() == before
    assert "source" in result.stderr.lower()


def test_symlink_output_is_rejected_without_touching_target(tmp_path: Path) -> None:
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    target = tmp_path / "target.txt"
    target.write_text("do not replace\n", encoding="utf-8")
    output = tmp_path / "programme.txt"
    output.symlink_to(target)

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 2
    assert target.read_text(encoding="utf-8") == "do not replace\n"
    assert output.is_symlink()
    assert "symbolique" in result.stderr.lower()


def test_symlink_output_parent_is_rejected_without_touching_external_directory(
    tmp_path: Path,
) -> None:
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    external = tmp_path / "external"
    external.mkdir()
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(external, target_is_directory=True)
    output = linked_parent / "programme.txt"

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 2
    assert not (external / "programme.txt").exists()
    assert "symbolique" in result.stderr.lower()


def test_missing_parents_are_never_created_behind_a_nested_symlink(
    tmp_path: Path,
) -> None:
    external = tmp_path / "external"
    external.mkdir()
    output_root = tmp_path / "output-root"
    output_root.mkdir()
    (output_root / "linked").symlink_to(external, target_is_directory=True)
    output = output_root / "linked" / "created" / "nested" / "programme.txt"

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 2
    assert not (external / "created").exists()
    assert "Traceback" not in result.stderr


def test_symlink_loop_output_is_a_controlled_failure_without_traceback(
    tmp_path: Path,
) -> None:
    output = tmp_path / "programme.txt"
    output.symlink_to(output.name)

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 2
    assert output.is_symlink()
    assert "Traceback" not in result.stderr


def test_source_symlink_is_allowed_only_at_the_registered_lexical_path(
    tmp_path: Path,
) -> None:
    assert SOURCE.is_symlink()
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    outside = tmp_path / "outside.pdf"
    outside.symlink_to(SOURCE.resolve())
    output = tmp_path / "programme.txt"

    result = run_extractor(outside, output, tmp_path)

    assert result.returncode == 2
    assert not output.exists()
    assert "source" in result.stderr.lower()


def test_registered_source_symlink_loop_is_a_controlled_failure(
    tmp_path: Path,
) -> None:
    source_loop = tmp_path / "official-loop.pdf"
    source_loop.symlink_to(source_loop.name)
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(source_loop)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    output = tmp_path / "programme.txt"

    result = run_extractor(source_loop, output, tmp_path, registry)

    assert result.returncode == 2
    assert not output.exists()
    assert "Traceback" not in result.stderr
    assert "source" in result.stderr.lower()


def test_pdftotext_symlink_loop_is_a_controlled_resolution_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extractor_module,
) -> None:
    executable_loop = tmp_path / "pdftotext"
    executable_loop.symlink_to(executable_loop.name)
    monkeypatch.setattr(
        extractor_module.shutil,
        "which",
        lambda _name: str(executable_loop),
    )

    with pytest.raises(
        extractor_module.ExtractionError,
        match="pdftotext",
    ):
        extractor_module.resolve_pdftotext()


def test_extractor_does_not_leave_temporary_files(tmp_path: Path) -> None:
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    output = tmp_path / "nested" / "programme.txt"

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 0, result.stderr
    assert sorted(path.name for path in output.parent.iterdir()) == [output.name]
    assert os.path.isfile(output)


def test_fake_pdftotext_from_path_cannot_publish_noncanonical_text(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    (fake_bin / "pdftotext").symlink_to("/bin/echo")
    output = tmp_path / "programme.txt"
    output.write_text("last known valid output\n", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = str(fake_bin)

    result = run_extractor(SOURCE, output, tmp_path, env=env)

    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "last known valid output\n"
    assert "pdftotext" in result.stderr.lower()


def test_extraction_uses_a_private_snapshot_and_allowlisted_environment(
    tmp_path: Path,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    registry = tmp_path / "registry.yaml"
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    registry.write_text(
        yaml.safe_dump({"sources": [entry]}, allow_unicode=True),
        encoding="utf-8",
    )
    observed_input = tmp_path / "observed-input.txt"
    observed_env = tmp_path / "observed-env.txt"
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "pdftotext"
    fake.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-v\" ]; then\n"
        "  echo 'pdftotext version 24.02.0' >&2\n"
        "  exit 0\n"
        "fi\n"
        f"printf '%s' \"$2\" > '{observed_input}'\n"
        f"printf '%s|%s|%s|%s' \"$LANG\" \"$LC_ALL\" \"$TZ\" "
        f"\"$UNTRUSTED_MARKER\" > '{observed_env}'\n"
        f"printf '%%s' '%%PDF-1.7\\nchanged after validation\\n' > '{source_copy}'\n"
        "exec /usr/bin/pdftotext \"$@\"\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    output = tmp_path / "programme.txt"
    env = os.environ.copy()
    env["PATH"] = str(fake_bin)
    env["UNTRUSTED_MARKER"] = "must-not-leak"

    result = run_extractor(source_copy, output, tmp_path, registry, env)

    assert result.returncode == 0, result.stderr
    assert sha256(output) == EXPECTED_TEXT_SHA256
    snapshot = Path(observed_input.read_text(encoding="utf-8"))
    assert snapshot != source_copy.resolve()
    assert not snapshot.exists()
    assert observed_env.read_text(encoding="utf-8") == "C|C|UTC|"


def test_directory_fsync_failure_before_commit_rolls_back_previous_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extractor_module,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    source = extractor_module.open_registered_source(source_copy, entry)
    output = tmp_path / "programme.txt"
    previous = b"last known valid output\n"
    output.write_bytes(previous)
    output, directory_descriptor = extractor_module.open_output_directory(output)
    real_fsync = extractor_module._fsync_directory
    calls = 0

    def fail_post_publish_directory_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected directory fsync failure")
        real_fsync(descriptor)

    monkeypatch.setattr(
        extractor_module,
        "_fsync_directory",
        fail_post_publish_directory_fsync,
    )
    try:
        with pytest.raises(extractor_module.ExtractionError, match="avant commit"):
            extractor_module.atomic_write(
                output,
                directory_descriptor,
                b"new canonical output\n",
                source,
            )
    finally:
        os.close(directory_descriptor)
        os.close(source.descriptor)

    assert output.read_bytes() == previous
    assert calls >= 3


def test_rename_failure_before_commit_rolls_back_previous_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extractor_module,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    source = extractor_module.open_registered_source(source_copy, entry)
    output = tmp_path / "programme.txt"
    previous = b"last known valid output\n"
    output.write_bytes(previous)
    output, directory_descriptor = extractor_module.open_output_directory(output)
    real_replace = extractor_module.os.replace

    def fail_new_output_rename(src, dst, *args, **kwargs):
        if str(src).endswith(".tmp"):
            raise OSError("injected rename failure")
        return real_replace(src, dst, *args, **kwargs)

    monkeypatch.setattr(extractor_module.os, "replace", fail_new_output_rename)
    try:
        with pytest.raises(extractor_module.ExtractionError, match="avant commit"):
            extractor_module.atomic_write(
                output,
                directory_descriptor,
                b"new canonical output\n",
                source,
            )
    finally:
        os.close(directory_descriptor)
        os.close(source.descriptor)

    assert output.read_bytes() == previous


def test_process_killed_after_first_replace_never_removes_existing_output(
    tmp_path: Path,
    extractor_module,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    source = extractor_module.open_registered_source(source_copy, entry)
    output = tmp_path / "programme.txt"
    output.write_bytes(b"last known valid output\n")
    output, directory_descriptor = extractor_module.open_output_directory(output)

    child = os.fork()
    if child == 0:
        real_replace = extractor_module.os.replace
        replace_calls = 0

        def kill_after_first_replace(src, dst, *args, **kwargs):
            nonlocal replace_calls
            result = real_replace(src, dst, *args, **kwargs)
            replace_calls += 1
            if replace_calls == 1:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        extractor_module.os.replace = kill_after_first_replace
        try:
            extractor_module.atomic_write(
                output,
                directory_descriptor,
                b"new canonical output\n",
                source,
            )
        finally:
            os._exit(97)

    try:
        _, status = os.waitpid(child, 0)
    finally:
        os.close(directory_descriptor)
        os.close(source.descriptor)

    assert os.WIFSIGNALED(status)
    assert os.WTERMSIG(status) == signal.SIGKILL
    assert output.exists()
    assert output.read_bytes() in {
        b"last known valid output\n",
        b"new canonical output\n",
    }


def test_initial_output_stays_published_if_post_replace_fsync_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extractor_module,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    source = extractor_module.open_registered_source(source_copy, entry)
    output = tmp_path / "programme.txt"
    output, directory_descriptor = extractor_module.open_output_directory(output)
    calls = 0

    def fail_first_directory_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("injected directory fsync failure")
        os.fsync(descriptor)

    monkeypatch.setattr(
        extractor_module,
        "_fsync_directory",
        fail_first_directory_fsync,
    )
    try:
        with pytest.raises(extractor_module.ExtractionError, match="durabilité"):
            extractor_module.atomic_write(
                output,
                directory_descriptor,
                b"new canonical output\n",
                source,
            )
    finally:
        os.close(directory_descriptor)
        os.close(source.descriptor)

    assert output.read_bytes() == b"new canonical output\n"


def test_atomic_write_retries_temporary_and_backup_name_collisions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extractor_module,
) -> None:
    source_copy = tmp_path / "official.pdf"
    shutil.copyfile(SOURCE, source_copy)
    entry = official_entry()
    entry["local_path"] = str(source_copy)
    source = extractor_module.open_registered_source(source_copy, entry)
    output = tmp_path / "programme.txt"
    output.write_bytes(b"last known valid output\n")
    temp_collision = tmp_path / f".{output.name}.temp-collision.tmp"
    backup_collision = tmp_path / f".{output.name}.backup-collision.bak"
    temp_collision.write_bytes(b"foreign temp\n")
    backup_collision.write_bytes(b"foreign backup\n")
    candidates = iter(
        (
            "temp-collision",
            "fresh-temp",
            "backup-collision",
            "fresh-backup",
        )
    )
    monkeypatch.setattr(
        extractor_module.tempfile,
        "_get_candidate_names",
        lambda: candidates,
    )
    output, directory_descriptor = extractor_module.open_output_directory(output)
    try:
        extractor_module.atomic_write(
            output,
            directory_descriptor,
            b"new canonical output\n",
            source,
        )
    finally:
        os.close(directory_descriptor)
        os.close(source.descriptor)

    assert output.read_bytes() == b"new canonical output\n"
    assert temp_collision.read_bytes() == b"foreign temp\n"
    assert backup_collision.read_bytes() == b"foreign backup\n"
