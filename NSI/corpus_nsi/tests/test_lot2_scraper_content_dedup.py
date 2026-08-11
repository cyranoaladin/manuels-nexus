from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
SCRAPER_DIR = ROOT / "scrapping_NSI"
if str(SCRAPER_DIR) not in sys.path:
    sys.path.insert(0, str(SCRAPER_DIR))

import scraper_nsi_v2 as scraper
from provenance import compute_sha256, generate_notice_sources, validate_provenance_record


def _mock_netpolicy() -> tuple[MagicMock, MagicMock, MagicMock]:
    session = MagicMock()
    robots = MagicMock()
    throttle = MagicMock()
    return session, robots, throttle


def _response(content: bytes, content_type: str = "application/pdf") -> MagicMock:
    response = MagicMock()
    response.status_code = 200
    response.headers = {"content-type": content_type}
    response.iter_content.return_value = iter([content])
    return response


def _download(
    *,
    url: str,
    folder: Path,
    content: bytes,
    index: scraper.DuplicateIndex,
    provenance_path: Path,
    stats: scraper.SiteStats | None = None,
    site_name: str = "Site",
) -> scraper.SiteStats:
    session, robots, throttle = _mock_netpolicy()
    stats = stats or scraper.SiteStats(site_name, "https://example.test/")
    with patch("scraper_nsi_v2.polite_get", return_value=(_response(content), None, False)):
        assert scraper.download_file(
            url,
            folder,
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=index,
            provenance_path=provenance_path,
            site_name=site_name,
            page_url=f"https://{site_name.lower()}.test/",
            page_html="<html></html>",
        )
    return stats


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_duplicate_index_no_longer_indexes_basenames(tmp_path: Path) -> None:
    existing = tmp_path / "site_a" / "pdf"
    existing.mkdir(parents=True)
    (existing / "cours.pdf").write_bytes(b"already here")

    index = scraper.DuplicateIndex.from_roots([tmp_path])

    assert not hasattr(index, "filenames")
    assert not hasattr(index, "has_filename")


def test_cross_run_bootstraps_from_provenance_without_redownloading(tmp_path: Path) -> None:
    provenance_path = tmp_path / "provenance.jsonl"
    first_index = scraper.DuplicateIndex.from_roots([tmp_path], provenance_path=provenance_path)
    first_stats = _download(
        url="https://example.test/cours.pdf",
        folder=tmp_path / "pass1" / "pdf",
        content=b"first content",
        index=first_index,
        provenance_path=provenance_path,
    )
    assert first_stats.files_downloaded == 1

    second_index = scraper.DuplicateIndex.from_roots([tmp_path], provenance_path=provenance_path)
    session, robots, throttle = _mock_netpolicy()
    second_stats = scraper.SiteStats("Site", "https://example.test/")
    with patch("scraper_nsi_v2.polite_get") as polite_get:
        assert scraper.download_file(
            "https://example.test/cours.pdf#page=2",
            tmp_path / "pass2" / "pdf",
            second_stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=second_index,
            provenance_path=provenance_path,
        )

    polite_get.assert_not_called()
    assert second_stats.files_downloaded == 0
    assert second_stats.files_skipped == 1


def test_same_basename_with_different_content_is_preserved_across_sites(tmp_path: Path) -> None:
    provenance_path = tmp_path / "provenance.jsonl"
    index = scraper.DuplicateIndex.from_roots([tmp_path], provenance_path=provenance_path)

    site_a = _download(
        url="https://site-a.test/cours.pdf",
        folder=tmp_path / "site_a" / "pdf",
        content=b"contenu A",
        index=index,
        provenance_path=provenance_path,
        site_name="Site A",
    )
    site_b = _download(
        url="https://site-b.test/cours.pdf",
        folder=tmp_path / "site_b" / "pdf",
        content=b"contenu B",
        index=index,
        provenance_path=provenance_path,
        site_name="Site B",
    )

    assert site_a.files_downloaded == 1
    assert site_b.files_downloaded == 1
    assert (tmp_path / "site_a" / "pdf" / "cours.pdf").read_bytes() == b"contenu A"
    assert (tmp_path / "site_b" / "pdf" / "cours.pdf").read_bytes() == b"contenu B"
    assert len({record["sha256"] for record in _jsonl(provenance_path)}) == 2


def test_canonical_url_fragments_download_once(tmp_path: Path) -> None:
    provenance_path = tmp_path / "provenance.jsonl"
    index = scraper.DuplicateIndex.from_roots([tmp_path], provenance_path=provenance_path)
    session, robots, throttle = _mock_netpolicy()
    stats = scraper.SiteStats("Site", "https://example.test/")

    with patch("scraper_nsi_v2.polite_get", return_value=(_response(b"pdf"), None, False)) as polite_get:
        assert scraper.download_file(
            "https://example.test/cours.pdf#page1",
            tmp_path / "pdf",
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=index,
            provenance_path=provenance_path,
        )
        assert scraper.download_file(
            "https://example.test/cours.pdf#page2",
            tmp_path / "other" / "pdf",
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=index,
            provenance_path=provenance_path,
        )

    assert polite_get.call_count == 1
    assert stats.files_downloaded == 1
    assert stats.files_skipped == 1


def test_duplicate_content_writes_valid_provenance_without_final_or_part(tmp_path: Path) -> None:
    provenance_path = tmp_path / "provenance.jsonl"
    index = scraper.DuplicateIndex.from_roots([tmp_path], provenance_path=provenance_path)
    content = b"same pdf content"

    first_stats = _download(
        url="https://site-a.test/a.pdf",
        folder=tmp_path / "site_a" / "pdf",
        content=content,
        index=index,
        provenance_path=provenance_path,
        site_name="Site A",
    )
    duplicate_stats = _download(
        url="https://site-b.test/b.pdf",
        folder=tmp_path / "site_b" / "pdf",
        content=content,
        index=index,
        provenance_path=provenance_path,
        site_name="Site B",
    )

    duplicate_final = tmp_path / "site_b" / "pdf" / "b.pdf"
    assert first_stats.files_downloaded == 1
    assert duplicate_stats.files_downloaded == 0
    assert duplicate_stats.files_duplicate_content == 1
    assert not duplicate_final.exists()
    assert not duplicate_final.with_name("b.pdf.part").exists()

    records = _jsonl(provenance_path)
    assert len(records) == 2
    original_sha = compute_sha256(tmp_path / "site_a" / "pdf" / "a.pdf")
    duplicate_record = records[1]
    assert duplicate_record["sha256"] == original_sha
    assert duplicate_record["source_url"] == "https://site-b.test/b.pdf"
    assert duplicate_record["duplicate_of"] == original_sha
    assert validate_provenance_record(duplicate_record) is True


def test_seeded_content_hash_duplicate_is_atomic(tmp_path: Path) -> None:
    content = b"known bytes"
    known_sha = hashlib.sha256(content).hexdigest()
    provenance_path = tmp_path / "provenance.jsonl"
    index = scraper.DuplicateIndex(content_hashes={known_sha})
    stats = _download(
        url="https://example.test/new.pdf",
        folder=tmp_path / "pdf",
        content=content,
        index=index,
        provenance_path=provenance_path,
    )

    final_path = tmp_path / "pdf" / "new.pdf"
    assert stats.files_duplicate_content == 1
    assert stats.files_skipped == 0
    assert stats.files_downloaded == 0
    assert not final_path.exists()
    assert not final_path.with_name("new.pdf.part").exists()


def test_content_hash_bootstrap_uses_provenance_then_bounded_scan(tmp_path: Path) -> None:
    scan_root = tmp_path / "scan"
    outside = tmp_path / "outside"
    scan_root.mkdir()
    outside.mkdir()
    inside_file = scan_root / "inside.pdf"
    outside_file = outside / "outside.pdf"
    inside_file.write_bytes(b"inside")
    outside_file.write_bytes(b"outside")
    provenance_path = tmp_path / "provenance.jsonl"
    provenance_hash = hashlib.sha256(b"from provenance").hexdigest()
    provenance_path.write_text(
        json.dumps(
            {
                "sha256": provenance_hash,
                "filename": "known.pdf",
                "source_url": "https://example.test/known.pdf#p1",
                "site_name": "Known",
                "page_url": "https://example.test/",
                "http_status": 200,
                "content_type": "application/pdf",
                "bytes": 10,
                "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license_guess": "unknown",
                "robots_allowed": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    from_provenance = scraper.DuplicateIndex.from_roots([scan_root], provenance_path=provenance_path)
    assert from_provenance.content_hashes == {provenance_hash}
    assert from_provenance.has_url("https://example.test/known.pdf#p2")

    provenance_path.write_text('{"filename": "incomplete"}\n', encoding="utf-8")
    from_scan = scraper.DuplicateIndex.from_roots([scan_root], provenance_path=provenance_path)
    assert compute_sha256(inside_file) in from_scan.content_hashes
    assert compute_sha256(outside_file) not in from_scan.content_hashes


def test_content_hash_bootstrap_treats_invalid_jsonl_as_incomplete(tmp_path: Path) -> None:
    scan_root = tmp_path / "scan"
    scan_root.mkdir()
    file_path = scan_root / "inside.pdf"
    file_path.write_bytes(b"inside")
    provenance_path = tmp_path / "provenance.jsonl"
    provenance_path.write_text("\n{not json}\n[]\n", encoding="utf-8")

    index = scraper.DuplicateIndex.from_roots([scan_root], provenance_path=provenance_path)

    assert index.bootstrap_source == "provenance+disk"
    assert index.disk_scan_performed is True
    assert compute_sha256(file_path) in index.content_hashes


def test_register_file_with_missing_path_only_registers_url(tmp_path: Path) -> None:
    index = scraper.DuplicateIndex()

    index.register_file("https://example.test/missing.pdf#fragment", tmp_path / "missing.pdf")

    assert index.has_url("https://example.test/missing.pdf")
    assert index.content_hashes == set()


def test_duplicate_content_without_provenance_is_atomic(tmp_path: Path) -> None:
    content = b"known duplicate"
    known_sha = hashlib.sha256(content).hexdigest()
    index = scraper.DuplicateIndex(content_hashes={known_sha})
    session, robots, throttle = _mock_netpolicy()
    stats = scraper.SiteStats("Site", "https://example.test/")

    with patch("scraper_nsi_v2.polite_get", return_value=(_response(content), None, False)):
        assert scraper.download_file(
            "https://example.test/no-provenance.pdf",
            tmp_path / "pdf",
            stats,
            session=session,
            robots=robots,
            throttle=throttle,
            duplicate_index=index,
            provenance_path=None,
        )

    final_path = tmp_path / "pdf" / "no-provenance.pdf"
    assert stats.files_duplicate_content == 1
    assert not final_path.exists()
    assert not final_path.with_name("no-provenance.pdf.part").exists()


def test_notice_counts_unique_content_and_duplicate_content_separately(tmp_path: Path) -> None:
    provenance_path = tmp_path / "provenance.jsonl"
    original_sha = hashlib.sha256(b"original").hexdigest()
    other_sha = hashlib.sha256(b"other").hexdigest()
    records = [
        {
            "sha256": original_sha,
            "filename": "a.pdf",
            "source_url": "https://site.test/a.pdf",
            "site_name": "Site",
            "page_url": "https://site.test/",
            "http_status": 200,
            "content_type": "application/pdf",
            "bytes": 8,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown",
            "robots_allowed": True,
        },
        {
            "sha256": original_sha,
            "filename": "a-copy.pdf",
            "source_url": "https://site.test/a-copy.pdf",
            "site_name": "Site",
            "page_url": "https://site.test/",
            "http_status": 200,
            "content_type": "application/pdf",
            "bytes": 8,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown",
            "robots_allowed": True,
            "duplicate_of": original_sha,
        },
        {
            "sha256": other_sha,
            "filename": "b.pdf",
            "source_url": "https://site.test/b.pdf",
            "site_name": "Site",
            "page_url": "https://site.test/",
            "http_status": 200,
            "content_type": "application/pdf",
            "bytes": 5,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown",
            "robots_allowed": True,
        },
    ]
    provenance_path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )

    notice_path = tmp_path / "NOTICE_SOURCES.md"
    generate_notice_sources(provenance_path, notice_path)
    content = notice_path.read_text(encoding="utf-8")

    assert "files_downloaded: 2" in content
    assert "files_skipped: 0" in content
    assert "files_duplicate_content: 1" in content
    assert "| Site | https://site.test/ | unknown | 2 | oui |" in content
