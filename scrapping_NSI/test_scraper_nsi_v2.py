from __future__ import annotations

import io
import json
import unittest
import requests
import csv
from contextlib import redirect_stdout
from collections import deque
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch, MagicMock

import scraper_nsi_v2 as scraper_module
from scraper_nsi_v2 import (
    DuplicateIndex,
    clean_filename,
    clean_folder_name,
    dedupe_preserve_order,
    download_file,
    dynamic_site_name,
    extract_links_from_html,
    fetch_html,
    filename_from_url,
    github_archive_urls,
    internal_scope_prefix,
    is_html_like_url,
    is_internal_html_url,
    is_annuaire_site,
    is_target_file_url,
    normalize_href,
    process_target_files,
    scrape_site,
    should_ignore_external_domain,
    site_output_folder,
    load_csv_sites,
    SiteStats,
)


# ---------------------------------------------------------------------------
# Helpers pour les mocks netpolicy
# ---------------------------------------------------------------------------

def _mock_netpolicy():
    """Retourne (session, robots, throttle) mockés pour les tests."""
    session = MagicMock(spec=requests.Session)
    robots = MagicMock()
    robots.can_fetch.return_value = True
    robots.crawl_delay.return_value = None
    throttle = MagicMock()
    return session, robots, throttle


def _make_polite_get_response(status_code=200, chunks=None, headers=None, text=""):
    """Crée un mock de réponse compatible avec polite_get."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {"content-type": "text/html"}
    resp.text = text
    if chunks is not None:
        resp.iter_content = MagicMock(return_value=iter(chunks))
    return resp


class ScraperNsiV2HelpersTest(unittest.TestCase):
    def test_normalize_href_replaces_backslashes_before_resolution(self):
        self.assertEqual(
            normalize_href(r"NSI_premiere\NSI_premierePDF\cours.pdf"),
            "NSI_premiere/NSI_premierePDF/cours.pdf",
        )

    def test_detects_target_files_after_backslash_normalization(self):
        base = "https://prolifaxe.github.io/coursdecourtois/NSI_1ere.html"
        links = extract_links_from_html(
            '<a href="NSI_premiere\\NSI_premierePDF\\cours.pdf">PDF</a>',
            base,
        )
        self.assertEqual(len(links.target_files), 1)
        self.assertTrue(links.target_files[0].endswith("/NSI_premiere/NSI_premierePDF/cours.pdf"))
        self.assertTrue(is_target_file_url(links.target_files[0]))

    def test_extract_links_ignores_empty_mailto_javascript_ftp_and_social_external(self):
        links = extract_links_from_html(
            """
            <a href="">Vide</a>
            <a href="mailto:test@example.test">Mail</a>
            <a href="javascript:void(0)">JS</a>
            <a href="ftp://example.test/file.pdf">FTP</a>
            <a href="https://youtube.com/watch?v=1">Social</a>
            """,
            "https://annuaire.example/",
            annuaire=True,
        )

        self.assertEqual(links.target_files, [])
        self.assertEqual(links.internal_pages, [])
        self.assertEqual(links.external_sites, [])

    def test_detects_same_domain_html_pages_for_depth_one_crawl(self):
        base = "https://glassus.github.io/premiere_nsi/"
        url = "https://glassus.github.io/premiere_nsi/T1_Demarrer_en_Python/1.1_Variables/cours/"
        self.assertTrue(is_internal_html_url(url, base))

    def test_annuaire_mode_collects_external_html_sites(self):
        base = "https://annuaire.example/cours/"
        links = extract_links_from_html(
            """
            <a href="https://collegue.example/nsi/">Site collègue</a>
            <a href="https://annuaire.example/cours/page2/">Interne</a>
            <a href="https://collegue.example/nsi/sujet.pdf">PDF direct externe</a>
            """,
            base,
            annuaire=True,
        )
        self.assertIn("https://collegue.example/nsi/", links.external_sites)
        self.assertNotIn("https://collegue.example/nsi/sujet.pdf", links.external_sites)

    def test_annuaire_can_be_detected_from_site_name(self):
        self.assertTrue(is_annuaire_site("Nathalie Bessonnet - Annuaire", "Forge HTML/MkDocs"))
        self.assertFalse(
            is_annuaire_site(
                "Annuaire - collegue.example",
                "Découvert via annuaire",
                discovered=True,
            )
        )

    def test_internal_scope_blocks_math93_college_from_nsi_entrypoint(self):
        base = "https://www.math93.com/index.php/lycee/1re-spe-nsi"
        scope = internal_scope_prefix(base)
        self.assertTrue(
            is_internal_html_url(
                "https://www.math93.com/index.php/lycee/1re-spe-nsi",
                base,
                scope_prefix=scope,
            )
        )
        self.assertFalse(
            is_internal_html_url(
                "https://www.math93.com/index.php/college/troisieme",
                base,
                scope_prefix=scope,
            )
        )

    def test_annuaire_external_sites_exclude_same_domain_navigation(self):
        base = "https://annuaire.example/cours/sites/"
        links = extract_links_from_html(
            """
            <a href="https://annuaire.example/cours/autre/">Même site</a>
            <a href="https://collegue.example/nsi/">Site collègue</a>
            """,
            base,
            annuaire=True,
            scope_prefix="/cours/sites/",
        )
        self.assertEqual(links.external_sites, ["https://collegue.example/nsi/"])

    def test_duplicate_index_detects_existing_file_hashes_across_roots(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "site_a" / "pdf"
            existing.mkdir(parents=True)
            file_path = existing / "Cours NSI.pdf"
            file_path.write_bytes(b"deja extrait")

            index = DuplicateIndex.from_roots([root])

            self.assertIn(scraper_module.compute_sha256(file_path), index.content_hashes)
            self.assertFalse(hasattr(index, "has_filename"))
            self.assertFalse(hasattr(index, "filenames"))

    def test_duplicate_index_ignores_absent_roots_and_registers_url(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = DuplicateIndex.from_roots([root / "absent"])
            target = root / "cours.pdf"
            target.write_bytes(b"cours")

            index.register_file("https://example.test/cours.pdf#section", target)

            self.assertTrue(index.has_url("https://example.test/cours.pdf"))
            self.assertIn(scraper_module.compute_sha256(target), index.content_hashes)

    def test_filename_and_url_helpers_cover_fallbacks(self):
        self.assertEqual(clean_filename("!?"), "ressource")
        self.assertEqual(clean_folder_name("!?"), "site")
        self.assertEqual(filename_from_url("https://example.test/"), "")
        self.assertEqual(dedupe_preserve_order(["a", "b", "a"]), ["a", "b"])
        self.assertFalse(is_html_like_url("ftp://example.test/index.html"))
        self.assertTrue(is_html_like_url("https://example.test/"))
        self.assertFalse(is_html_like_url("https://example.test/style.css"))
        self.assertTrue(is_html_like_url("https://example.test/page.php"))
        self.assertEqual(internal_scope_prefix("https://example.test/cours/page.html"), "/cours/")
        self.assertEqual(internal_scope_prefix("https://example.test/cours"), "/cours/")
        self.assertTrue(should_ignore_external_domain("https://youtube.com/watch?v=1"))
        self.assertEqual(site_output_folder("Site Test"), scraper_module.OUTPUT_ROOT / "Site Test")

    def test_out_of_scope_platforms_are_explicitly_configured(self):
        self.assertIn("Éduscol STI - Hub Spécialité NSI", scraper_module.OUT_OF_SCOPE_SCRAPE_TARGETS)
        self.assertIn("Wikibooks - Communauté NSI", scraper_module.OUT_OF_SCOPE_SCRAPE_TARGETS)

    def test_download_does_not_skip_same_basename_without_matching_url_or_hash(self):
        session, robots, throttle = _mock_netpolicy()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "site_a" / "pdf"
            target = root / "site_b" / "pdf"
            existing.mkdir(parents=True)
            (existing / "fiche.pdf").write_bytes(b"deja extrait")
            index = DuplicateIndex.from_roots([root])
            stats = SiteStats("Site B", "https://example.test/")

            resp_pdf = _make_polite_get_response(
                status_code=200,
                chunks=[b"contenu different"],
                headers={"content-type": "application/pdf"},
            )
            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_pdf, None, False),
            ) as polite_get:
                self.assertTrue(
                    download_file(
                        "https://example.test/nouveau/fiche.pdf",
                        target,
                        stats,
                        session=session,
                        robots=robots,
                        throttle=throttle,
                        duplicate_index=index,
                    )
                )

            self.assertEqual(stats.files_downloaded, 1)
            self.assertEqual(stats.files_skipped, 0)
            self.assertTrue((target / "fiche.pdf").exists())
            self.assertEqual(polite_get.call_count, 1)

    def test_download_handles_missing_filename_existing_file_http_error_and_success(self):
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "pdf"
            stats = SiteStats("Site", "https://example.test/")
            duplicate_index = DuplicateIndex()

            # Nom de fichier absent
            with redirect_stdout(io.StringIO()):
                self.assertFalse(
                    download_file(
                        "https://example.test/", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )
            self.assertIn("Nom de fichier absent", stats.errors[0])

            # Fichier déjà présent
            existing = target / "cours.pdf"
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b"existing")
            with redirect_stdout(io.StringIO()):
                self.assertTrue(
                    download_file(
                        "https://example.test/cours.pdf",
                        target,
                        stats,
                        session=session, robots=robots, throttle=throttle,
                        duplicate_index=duplicate_index,
                    )
            )
            self.assertEqual(stats.files_skipped, 1)
            self.assertIn(scraper_module.compute_sha256(existing), duplicate_index.content_hashes)

            # Erreur HTTP 404
            resp_404 = _make_polite_get_response(status_code=404)
            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_404, None, False),
            ):
                self.assertFalse(
                    download_file(
                        "https://example.test/absent.pdf", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )
            self.assertIn("Statut 404", stats.errors[-1])

            # Succès 200 avec .part existant
            partial = target / "ok.pdf.part"
            partial.write_bytes(b"old")
            resp_ok = _make_polite_get_response(
                status_code=200, chunks=[b"new", b"", b" file"],
                headers={"content-type": "application/pdf"},
            )
            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_ok, None, False),
            ):
                self.assertTrue(
                    download_file(
                        "https://example.test/ok.pdf",
                        target,
                        stats,
                        session=session, robots=robots, throttle=throttle,
                        duplicate_index=duplicate_index,
                    )
                )
            self.assertEqual((target / "ok.pdf").read_bytes(), b"new file")
            self.assertFalse(partial.exists())
            self.assertTrue(duplicate_index.has_url("https://example.test/ok.pdf"))

    def test_github_repo_html_adds_default_branch_archive_url(self):
        html = '<a href="/DLatreyte/dlatreyte.github.io/tree/master">master</a>'

        self.assertEqual(
            github_archive_urls("https://github.com/DLatreyte/dlatreyte.github.io", html),
            ["https://github.com/DLatreyte/dlatreyte.github.io/archive/refs/heads/master.zip"],
        )

    def test_github_archive_filename_is_repo_specific_to_avoid_master_zip_collision(self):
        self.assertEqual(
            filename_from_url(
                "https://github.com/DLatreyte/dlatreyte.github.io/archive/refs/heads/master.zip"
            ),
            "DLatreyte_dlatreyte.github.io_master.zip",
        )

    def test_github_archive_urls_handles_non_repo_and_default_main(self):
        self.assertEqual(github_archive_urls("https://example.test/repo", ""), [])
        self.assertEqual(github_archive_urls("https://github.com/owner", ""), [])
        self.assertEqual(
            github_archive_urls("https://github.com/owner/repo", "<html></html>"),
            ["https://github.com/owner/repo/archive/refs/heads/main.zip"],
        )

    def test_fetch_html_covers_status_content_type_and_exception(self):
        session, robots, throttle = _mock_netpolicy()

        # Erreur HTTP 500
        resp_500 = _make_polite_get_response(status_code=500)
        with patch("scraper_nsi_v2.polite_get", return_value=(resp_500, None, False)):
            html, error, blocked = fetch_html(
                "https://example.test/", session=session, robots=robots, throttle=throttle,
            )
        self.assertIsNone(html)
        self.assertIn("Statut 500", error)
        self.assertFalse(blocked)

        # Contenu non HTML
        resp_pdf = _make_polite_get_response(
            status_code=200, headers={"content-type": "application/pdf"},
        )
        with patch("scraper_nsi_v2.polite_get", return_value=(resp_pdf, None, False)):
            html, error, blocked = fetch_html(
                "https://example.test/file.pdf", session=session, robots=robots, throttle=throttle,
            )
        self.assertIsNone(html)
        self.assertIn("Contenu non HTML", error)

        # Succès content-type vide
        resp_ok = _make_polite_get_response(
            status_code=200, headers={"content-type": ""}, text="<h1>OK</h1>",
        )
        with patch("scraper_nsi_v2.polite_get", return_value=(resp_ok, None, False)):
            html, error, blocked = fetch_html(
                "https://example.test/page", session=session, robots=robots, throttle=throttle,
            )
        self.assertEqual((html, error, blocked), ("<h1>OK</h1>", None, False))

        # Exception réseau
        with patch(
            "scraper_nsi_v2.polite_get",
            return_value=(None, "Exception requête pour https://example.test/slow: timeout", False),
        ):
            html, error, blocked = fetch_html(
                "https://example.test/slow", session=session, robots=robots, throttle=throttle,
            )
        self.assertIsNone(html)
        self.assertIn("Exception requête", error)

        # Bloqué par robots
        with patch(
            "scraper_nsi_v2.polite_get",
            return_value=(None, "Refusé par robots.txt : https://example.test/secret", True),
        ):
            html, error, blocked = fetch_html(
                "https://example.test/secret", session=session, robots=robots, throttle=throttle,
            )
        self.assertIsNone(html)
        self.assertTrue(blocked)
        self.assertIn("robots.txt", error)

    def test_download_failure_does_not_leave_partial_final_file(self):
        session, robots, throttle = _mock_netpolicy()

        resp_broken = _make_polite_get_response(status_code=200)
        resp_broken.iter_content = MagicMock(
            side_effect=requests.exceptions.ChunkedEncodingError("connexion coupee")
        )

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "site" / "zip"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_broken, None, False),
            ):
                self.assertFalse(
                    download_file(
                        "https://example.test/archive.zip", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )

            self.assertFalse((target / "archive.zip").exists())
            self.assertFalse((target / "archive.zip.part").exists())
            self.assertEqual(len(stats.errors), 1)

    def test_download_request_exception_before_partial_path_is_recorded(self):
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "site" / "zip"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(None, "Exception requête pour https://example.test/archive.zip: timeout", False),
            ):
                self.assertFalse(
                    download_file(
                        "https://example.test/archive.zip", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )

            self.assertEqual(len(stats.errors), 1)
            self.assertIn("timeout", stats.errors[0])

    def test_download_oserror_after_partial_created(self):
        """OSError pendant écriture iter_content — .part nettoyé."""
        session, robots, throttle = _mock_netpolicy()

        resp = _make_polite_get_response(status_code=200)
        resp.iter_content = MagicMock(side_effect=OSError("disk full"))

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "site" / "pdf"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp, None, False),
            ):
                self.assertFalse(
                    download_file(
                        "https://example.test/file.pdf", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )
            self.assertEqual(len(stats.errors), 1)
            self.assertIn("disk full", stats.errors[0])

    def test_download_mkdir_failure_partial_path_none(self):
        """OSError avant création du .part — partial_path reste None."""
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            # Créer un fichier là où mkdir attend un répertoire
            blocker = Path(tmp) / "blocker"
            blocker.write_bytes(b"x")
            broken_target = blocker / "sub" / "pdf"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()):
                result = download_file(
                    "https://example.test/file.pdf", broken_target, stats,
                    session=session, robots=robots, throttle=throttle,
                )

            self.assertFalse(result)
            self.assertEqual(len(stats.errors), 1)

    def test_download_existing_file_without_duplicate_index_and_success_without_index(self):
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "pdf"
            stats = SiteStats("Site", "https://example.test/")
            existing = target / "cours.pdf"
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b"existing")

            with redirect_stdout(io.StringIO()):
                self.assertTrue(
                    download_file(
                        "https://example.test/cours.pdf", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )
            self.assertEqual(stats.files_skipped, 1)

            resp_ok = _make_polite_get_response(
                status_code=200, chunks=[b"ok"],
                headers={"content-type": "application/pdf"},
            )
            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_ok, None, False),
            ):
                self.assertTrue(
                    download_file(
                        "https://example.test/new.pdf", target, stats,
                        session=session, robots=robots, throttle=throttle,
                    )
                )
            self.assertEqual((target / "new.pdf").read_bytes(), b"ok")
            self.assertEqual(stats.files_downloaded, 1)

    def test_download_robots_blocked_counts_as_blocked_not_error(self):
        """URL bloquée par robots → robots_blocked incrémenté, pas erreur."""
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "pdf"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(None, "Refusé par robots.txt", True),
            ):
                result = download_file(
                    "https://example.test/secret.pdf", target, stats,
                    session=session, robots=robots, throttle=throttle,
                )

            self.assertTrue(result)
            self.assertEqual(stats.robots_blocked, 1)
            self.assertEqual(len(stats.errors), 0)

    def test_download_writes_provenance_on_success(self):
        """Un téléchargement réussi écrit une ligne conforme dans provenance.jsonl."""
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "pdf"
            provenance_path = Path(tmp) / "provenance.jsonl"
            stats = SiteStats("Site Test", "https://example.test/")

            resp_ok = _make_polite_get_response(
                status_code=200, chunks=[b"pdf content here"],
                headers={"content-type": "application/pdf"},
            )
            with redirect_stdout(io.StringIO()), patch(
                "scraper_nsi_v2.polite_get",
                return_value=(resp_ok, None, False),
            ):
                download_file(
                    "https://example.test/cours.pdf", target, stats,
                    session=session, robots=robots, throttle=throttle,
                    provenance_path=provenance_path,
                    site_name="Site Test",
                    page_url="https://example.test/",
                    page_html="<html><body>Cours</body></html>",
                )

            self.assertTrue(provenance_path.exists())
            record = json.loads(provenance_path.read_text().strip())
            # Exactement les 11 clés requises (pas de duplicate_of ici)
            expected_keys = {
                "sha256", "filename", "source_url", "site_name", "page_url",
                "http_status", "content_type", "bytes", "retrieved_at",
                "license_guess", "robots_allowed",
            }
            self.assertEqual(set(record.keys()), expected_keys)
            self.assertEqual(record["filename"], "cours.pdf")
            self.assertEqual(record["source_url"], "https://example.test/cours.pdf")
            self.assertEqual(record["site_name"], "Site Test")
            self.assertEqual(record["page_url"], "https://example.test/")
            self.assertEqual(record["http_status"], 200)
            self.assertEqual(record["content_type"], "application/pdf")
            self.assertEqual(record["bytes"], len(b"pdf content here"))
            self.assertTrue(record["robots_allowed"])
            self.assertEqual(record["license_guess"], "unknown")
            self.assertIn("sha256", record)
            # retrieved_at ISO-8601 avec fuseau
            from datetime import datetime
            dt = datetime.fromisoformat(record["retrieved_at"])
            self.assertIsNotNone(dt.tzinfo)

    def test_download_skip_does_not_write_provenance(self):
        """Un fichier sauté (déjà présent) n'ajoute pas de ligne provenance."""
        session, robots, throttle = _mock_netpolicy()

        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "pdf"
            target.mkdir(parents=True)
            (target / "cours.pdf").write_bytes(b"existing")
            provenance_path = Path(tmp) / "provenance.jsonl"
            stats = SiteStats("Site", "https://example.test/")

            with redirect_stdout(io.StringIO()):
                download_file(
                    "https://example.test/cours.pdf", target, stats,
                    session=session, robots=robots, throttle=throttle,
                    provenance_path=provenance_path,
                )

            self.assertFalse(provenance_path.exists())

    def test_process_target_files_routes_by_extension(self):
        session, robots, throttle = _mock_netpolicy()
        stats = SiteStats("Site", "https://example.test/")
        with TemporaryDirectory() as tmp:
            site_folder = Path(tmp)
            with patch("scraper_nsi_v2.download_file") as download:
                process_target_files(
                    ["https://example.test/a.PDF", "https://example.test/notebook.ipynb"],
                    site_folder,
                    stats,
                    session=session, robots=robots, throttle=throttle,
                    duplicate_index=None,
                )

            self.assertEqual(download.call_count, 2)
            self.assertEqual(download.call_args_list[0].args[1], site_folder / "pdf")
            self.assertEqual(download.call_args_list[1].args[1], site_folder / "ipynb")

    def test_scrape_site_crawls_internal_pages_and_collects_annuaire_external_sites(self):
        session, robots, throttle = _mock_netpolicy()
        base = "https://annuaire.example/cours/"
        page_html = """
        <a href="fiche.pdf">PDF</a>
        <a href="page2/">Interne</a>
        <a href="https://collegue.example/nsi/">Collègue</a>
        """
        page2_html = '<a href="tp.py">TP</a>'

        def fake_fetch(url, *, session, robots, throttle):
            if url == base:
                return page_html, None, False
            if url == "https://annuaire.example/cours/page2/":
                return page2_html, None, False
            return None, f"unexpected {url}", False

        with redirect_stdout(io.StringIO()), patch.object(
            scraper_module,
            "MAX_DEPTH",
            1,
        ), patch.object(scraper_module, "MAX_SUBPAGES_PER_SITE", 10), patch(
            "scraper_nsi_v2.fetch_html",
            side_effect=fake_fetch,
        ), patch("scraper_nsi_v2.process_target_files") as process_files:
            stats, external = scrape_site(
                "Annuaire NSI",
                base,
                "Annuaire",
                session=session, robots=robots, throttle=throttle,
                duplicate_index=DuplicateIndex(),
            )

        self.assertEqual(stats.pages_seen, 2)
        self.assertEqual(external, ["https://collegue.example/nsi/"])
        self.assertEqual(stats.external_sites_discovered, 1)
        self.assertEqual(process_files.call_count, 2)

    def test_scrape_site_records_page_errors_and_limits_subpages(self):
        session, robots, throttle = _mock_netpolicy()
        base = "https://example.test/root/"
        html = """
        <a href="a/">A</a>
        <a href="b/">B</a>
        """

        def fake_fetch(url, *, session, robots, throttle):
            if url == base:
                return html, None, False
            return None, "boom", False

        with redirect_stdout(io.StringIO()), patch.object(
            scraper_module,
            "MAX_DEPTH",
            1,
        ), patch.object(scraper_module, "MAX_SUBPAGES_PER_SITE", 1), patch(
            "scraper_nsi_v2.fetch_html",
            side_effect=fake_fetch,
        ), patch("scraper_nsi_v2.process_target_files"):
            stats, external = scrape_site(
                "Site", base, "Cours",
                session=session, robots=robots, throttle=throttle,
            )

        self.assertEqual(stats.pages_seen, 2)
        self.assertEqual(len(stats.errors), 1)
        self.assertEqual(external, [])

    def test_scrape_site_handles_none_html_and_self_links_without_queue_growth(self):
        session, robots, throttle = _mock_netpolicy()
        base = "https://example.test/root/"

        with redirect_stdout(io.StringIO()), patch.object(
            scraper_module,
            "MAX_DEPTH",
            1,
        ), patch(
            "scraper_nsi_v2.fetch_html",
            return_value=(None, None, False),
        ), patch("scraper_nsi_v2.process_target_files") as process_files:
            stats, external = scrape_site(
                "Site", base, "Cours",
                session=session, robots=robots, throttle=throttle,
            )

        self.assertEqual(stats.pages_seen, 1)
        self.assertEqual(stats.errors, [])
        self.assertEqual(external, [])
        process_files.assert_not_called()

        html = '<a href="https://example.test/root/">Self</a>'
        with redirect_stdout(io.StringIO()), patch.object(
            scraper_module,
            "MAX_DEPTH",
            1,
        ), patch(
            "scraper_nsi_v2.fetch_html",
            return_value=(html, None, False),
        ), patch("scraper_nsi_v2.process_target_files"):
            stats, _external = scrape_site(
                "Site", base, "Cours",
                session=session, robots=robots, throttle=throttle,
            )

        self.assertEqual(stats.pages_seen, 1)

    def test_scrape_site_skips_url_already_visited_if_queue_contains_duplicate(self):
        session, robots, throttle = _mock_netpolicy()
        base = "https://example.test/root/"

        def duplicate_deque(initial):
            queue = deque(initial)
            if initial:
                queue.append(initial[0])
            return queue

        with redirect_stdout(io.StringIO()), patch(
            "scraper_nsi_v2.deque",
            side_effect=duplicate_deque,
        ), patch(
            "scraper_nsi_v2.fetch_html", return_value=(None, None, False)
        ), patch(
            "scraper_nsi_v2.process_target_files"
        ):
            stats, external = scrape_site(
                "Site", base, "Cours",
                session=session, robots=robots, throttle=throttle,
            )

        self.assertEqual(stats.pages_seen, 1)
        self.assertEqual(external, [])

    def test_scrape_site_robots_blocked_page_counted_not_as_error(self):
        """Une page bloquée par robots est comptée dans robots_blocked, pas dans errors."""
        session, robots, throttle = _mock_netpolicy()
        base = "https://example.test/root/"

        with redirect_stdout(io.StringIO()), patch(
            "scraper_nsi_v2.fetch_html",
            return_value=(None, "Refusé par robots.txt", True),
        ), patch("scraper_nsi_v2.process_target_files"):
            stats, external = scrape_site(
                "Site", base, "Cours",
                session=session, robots=robots, throttle=throttle,
            )

        self.assertEqual(stats.robots_blocked, 1)
        self.assertEqual(len(stats.errors), 0)
        self.assertEqual(stats.pages_seen, 1)

    def test_load_csv_dynamic_name_and_main_are_exercised_without_network(self):
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "sites.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Nom_Site", "URL", "Type_Structure"])
                writer.writeheader()
                writer.writerow(
                    {
                        "Nom_Site": "Annuaire",
                        "URL": "https://annuaire.example/#top",
                        "Type_Structure": "Annuaire",
                    }
                )
                writer.writerow(
                    {"Nom_Site": "", "URL": "https://ignored.example/", "Type_Structure": ""}
                )

            with redirect_stdout(io.StringIO()) as csv_output:
                loaded_sites = load_csv_sites(str(csv_path))
            self.assertEqual(
                loaded_sites,
                [("Annuaire", "https://annuaire.example/", "Annuaire")],
            )
            self.assertIn("[CSV IGNORÉ] ligne 3 incomplète", csv_output.getvalue())
            self.assertEqual(
                dynamic_site_name("https://collegue.example/nsi/cours/"),
                "Annuaire - collegue.example - nsi_cours",
            )
            self.assertEqual(
                dynamic_site_name("https://collegue.example/"),
                "Annuaire - collegue.example",
            )

            with self.assertRaises(SystemExit):
                with redirect_stdout(io.StringIO()):
                    load_csv_sites(str(Path(tmp) / "missing.csv"))

            def fake_scrape(site_name, url, structure, *,
                            session, robots, throttle,
                            discovered=False, duplicate_index=None,
                            provenance_path=None):
                if not discovered:
                    return SiteStats(site_name, url, pages_seen=1), [
                        "https://annuaire.example/",
                        "https://new.example/nsi/",
                    ]
                return SiteStats(site_name, url, discovered_from_annuaire=True, pages_seen=1), []

            with redirect_stdout(io.StringIO()), patch.object(
                scraper_module,
                "CSV_FILE",
                str(csv_path),
            ), patch.object(
                scraper_module,
                "DUPLICATE_SCAN_ROOTS",
                (Path(tmp) / "missing",),
            ), patch(
                "scraper_nsi_v2.scrape_site",
                side_effect=fake_scrape,
            ):
                scraper_module.main()


if __name__ == "__main__":
    unittest.main()
