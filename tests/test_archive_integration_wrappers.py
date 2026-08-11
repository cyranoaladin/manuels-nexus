from __future__ import annotations

import io
import tarfile
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

import scripts.check_archive_portability as check_archive_portability
import scripts.check_audit_extracted_runtime_budget as runtime_budget
import scrapping_NSI.organizer_nsi as organizer
import scrapping_NSI.scraper_eduscol as eduscol


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def write_tar(path: Path, files: dict[str, bytes]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))


def test_eduscol_wrapper_calls_safe_extract_zip_and_preserves_normal_sort(
    tmp_path: Path,
) -> None:
    base = tmp_path / "output"
    base.mkdir()
    archive = tmp_path / "clean.zip"
    write_zip(archive, {"placeholder.txt": b"placeholder"})

    def fake_safe_extract_zip(zip_path: Path, destination: Path) -> None:
        assert zip_path == archive
        destination.mkdir(parents=True)
        (destination / "script.py").write_text("print('ok')\n", encoding="utf-8")

    with patch.object(eduscol, "safe_extract_zip", side_effect=fake_safe_extract_zip) as safe_extract:
        with redirect_stdout(io.StringIO()):
            eduscol.extract_and_sort_zip(str(archive), str(base))

    assert safe_extract.call_count == 1
    assert (base / "Archives_Extraites_Triees" / "01_Codes_Python" / "script.py").is_file()
    assert not (base / "_temp_zip_extraction").exists()
    assert not (base / "_temp_zip_extraction.part").exists()


def test_organizer_wrapper_calls_safe_extract_zip_and_removes_processed_archive(
    tmp_path: Path,
) -> None:
    transit = tmp_path / "transit"
    transit.mkdir()
    archive = transit / "bundle.zip"
    write_zip(archive, {"placeholder.txt": b"placeholder"})

    def fake_safe_extract_zip(zip_path: Path, destination: Path) -> None:
        assert zip_path == archive
        destination.mkdir(parents=True)
        (destination / "cours.pdf").write_bytes(b"pdf")

    with patch.object(organizer, "safe_extract_zip", side_effect=fake_safe_extract_zip) as safe_extract:
        extracted = organizer.extract_zip_to_transit(archive, transit)

    assert extracted == 1
    assert safe_extract.call_count == 1
    assert not archive.exists()
    assert (transit / organizer.EXTRACTED_ZIP_DIR / "bundle" / "cours.pdf").is_file()
    assert not (transit / organizer.EXTRACTED_ZIP_DIR / "bundle.part").exists()


def test_organizer_malicious_zip_fails_loudly_without_outside_write(
    tmp_path: Path,
) -> None:
    transit = tmp_path / "transit"
    transit.mkdir()
    archive = transit / "evil.zip"
    write_zip(archive, {"../../evil.txt": b"owned"})

    with redirect_stdout(io.StringIO()):
        extracted = organizer.extract_zip_to_transit(archive, transit)

    assert extracted == 0
    assert not (tmp_path / "evil.txt").exists()
    assert not (transit / organizer.EXTRACTED_ZIP_DIR / "evil").exists()
    assert not (transit / organizer.EXTRACTED_ZIP_DIR / "evil.part").exists()


def test_archive_portability_uses_safe_extract_tar(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    dist = root / "dist"
    dist.mkdir(parents=True)
    archive = dist / "source_clean.tar.gz"
    write_tar(archive, {"placeholder.txt": b"placeholder"})

    def fake_safe_extract_tar(archive_path: Path, destination: Path) -> None:
        assert archive_path == archive
        repo = destination / "nsi-enseignement"
        repo.mkdir()
        for required in check_archive_portability.REQUIRED_FILES:
            target = repo / required
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("ok\n", encoding="utf-8")
        for script in check_archive_portability.CHECKS:
            target = repo / script
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("print('PASS')\n", encoding="utf-8")

    with patch.object(check_archive_portability, "safe_extract_tar", side_effect=fake_safe_extract_tar) as safe_extract:
        result = check_archive_portability.analyze_archive_portability(root)

    assert safe_extract.call_count == 1
    assert result.errors == []


def test_archive_portability_rejects_malicious_archive_without_outside_write(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    dist = root / "dist"
    dist.mkdir(parents=True)
    archive = dist / "source_clean.tar.gz"
    write_tar(archive, {"../../evil.txt": b"owned"})

    result = check_archive_portability.analyze_archive_portability(root)

    assert any("archive extraction failed" in error for error in result.errors)
    assert not (tmp_path / "evil.txt").exists()


def test_runtime_budget_extract_source_clean_uses_safe_extract_tar(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    dist = root / "dist"
    dist.mkdir(parents=True)
    archive = dist / "source_clean.tar.gz"
    write_tar(archive, {"placeholder.txt": b"placeholder"})

    def fake_safe_extract_tar(archive_path: Path, destination: Path) -> None:
        assert archive_path == archive
        extracted = destination / "nsi-enseignement"
        extracted.mkdir()
        (extracted / "Makefile").write_text("audit-extracted-source:\n\t@true\n", encoding="utf-8")

    with patch.object(runtime_budget, "safe_extract_tar", side_effect=fake_safe_extract_tar) as safe_extract:
        temp, extracted = runtime_budget.extract_source_clean(root)

    try:
        assert safe_extract.call_count == 1
        assert extracted.name == "nsi-enseignement"
        assert (extracted / "Makefile").is_file()
    finally:
        temp.cleanup()


def test_runtime_budget_malicious_archive_cleans_staging_and_writes_nothing_outside(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    dist = root / "dist"
    dist.mkdir(parents=True)
    archive = dist / "source_clean.tar.gz"
    write_tar(archive, {"../../evil.txt": b"owned"})

    try:
        runtime_budget.extract_source_clean(root)
    except Exception as exc:
        assert "Zip-Slip" in str(exc) or "hors du repertoire cible" in str(exc)
    else:
        raise AssertionError("archive malveillante acceptée")

    assert not (tmp_path / "evil.txt").exists()
