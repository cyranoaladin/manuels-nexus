from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_official_source.py"
REGISTRY = ROOT / "sources" / "registry.yaml"
SOURCE = ROOT / "sources" / "BO2026_1SPE_specialite.pdf"
EXPECTED_PDF_SHA256 = (
    "5303df0fcf6335f06d00c969a61dcd82cc3fdfd105271ae5c2ef580ff49b6c08"
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


def run_extractor(
    source: Path,
    output: Path,
    cwd: Path,
    registry: Path = REGISTRY,
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


def test_extractor_does_not_leave_temporary_files(tmp_path: Path) -> None:
    assert sha256(SOURCE) == EXPECTED_PDF_SHA256
    output = tmp_path / "nested" / "programme.txt"

    result = run_extractor(SOURCE, output, tmp_path)

    assert result.returncode == 0, result.stderr
    assert sorted(path.name for path in output.parent.iterdir()) == [output.name]
    assert os.path.isfile(output)
