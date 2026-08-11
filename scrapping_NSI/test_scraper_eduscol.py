# -*- coding: utf-8 -*-
"""Tests pour scraper_eduscol.py — câblage netpolicy/provenance (Lot 1).

Réseau entièrement mocké, aucun sleep réel.
Tri/dédoublonnage ZIP testé avec de vraies archives.
Les branches zip-slip/zip-bomb restent pragma: no cover (Lot 3).
"""

from __future__ import annotations

import io
import json
import shutil
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import scraper_eduscol as eduscol_module
from scraper_eduscol import clean_name, extract_and_sort_zip, scrape_eduscol_nsi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_polite_get_response(status_code=200, text="", headers=None, chunks=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.headers = headers or {"content-type": "text/html"}
    if chunks is not None:
        resp.iter_content = MagicMock(return_value=iter(chunks))
    return resp


def _page_html_with_links(links):
    """Génère du HTML contenant une liste de liens <a href>."""
    parts = []
    for href, text in links:
        parts.append(f'<a href="{href}">{text}</a>')
    return f"<html><body>{''.join(parts)}</body></html>"


# ---------------------------------------------------------------------------
# clean_name
# ---------------------------------------------------------------------------

class TestCleanName:
    def test_normal_string(self):
        assert clean_name("Sujet NSI 2024") == "Sujet NSI 2024"

    def test_special_chars(self):
        assert clean_name("résumé@#!") == "résumé"

    def test_empty_string(self):
        assert clean_name("") == "ressource_sans_nom"

    def test_only_special_chars(self):
        assert clean_name("@#$") == "ressource_sans_nom"


# ---------------------------------------------------------------------------
# scrape_eduscol_nsi — câblage polite_get
# ---------------------------------------------------------------------------

class TestScrapeEduscolNsiCablage:

    def test_all_gets_pass_through_polite_get(self):
        """Aucun requests.get direct : tout passe par polite_get."""
        page_html = _page_html_with_links([
            ("/download/sujet.pdf", "Sujet PDF"),
        ])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(
            200, chunks=[b"pdf content"],
            headers={"content-type": "application/pdf"},
        )

        call_count = {"n": 0}

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            call_count["n"] += 1
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("builtins.open", MagicMock()), \
                patch("scraper_eduscol.compute_sha256", return_value="abc123"), \
                patch("scraper_eduscol.write_provenance_record"), \
                patch("scraper_eduscol.os.path.getsize", return_value=100):
            scrape_eduscol_nsi()

        # Au moins 2 appels : 1 page + 1 fichier
        assert call_count["n"] >= 2

    def test_page_blocked_by_robots_continues_without_error(self):
        """Page bloquée par robots → continue au lieu de planter."""
        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get",
                      return_value=(None, "Refusé par robots.txt", True)), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        output = out.getvalue()
        assert "Robots" in output
        # Pas de crash, le process se termine normalement
        assert "PROCESSUS ÉDUSCOL TERMINÉ" in output

    def test_file_blocked_by_robots_continues(self):
        """Fichier bloqué par robots → continue sans planter."""
        page_html = _page_html_with_links([("/secret.pdf", "Secret")])
        page_resp = _make_polite_get_response(200, text=page_html)

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return None, "Refusé par robots.txt", True
            return page_resp, None, False

        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        output = out.getvalue()
        assert "Robots" in output
        assert "PROCESSUS ÉDUSCOL TERMINÉ" in output

    def test_download_success_writes_provenance(self):
        """Téléchargement réussi écrit une ligne provenance conforme."""
        page_html = _page_html_with_links([("/sujet_nsi.pdf", "Sujet NSI")])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(
            200, chunks=[b"pdf data"],
            headers={"content-type": "application/pdf"},
        )

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            provenance_path = Path(tmp) / "provenance.jsonl"
            dossier = Path(tmp) / "eduscol"
            dossier.mkdir()

            with patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                    patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                    patch("scraper_eduscol.os.makedirs"), \
                    patch("scraper_eduscol.os.path.exists", return_value=False), \
                    patch("scraper_eduscol.os.path.getsize", return_value=42), \
                    patch("scraper_eduscol.compute_sha256", return_value="deadbeef" * 8), \
                    patch("builtins.open", MagicMock()):
                scrape_eduscol_nsi(provenance_path=provenance_path)

            assert provenance_path.exists()
            record = json.loads(provenance_path.read_text().strip())
            assert record["site_name"] == "Éduscol STI"
            assert record["http_status"] == 200
            assert record["robots_allowed"] is True
            assert record["bytes"] == 42

    def test_page_error_continues(self):
        """Erreur réseau sur une page → continue avec la suivante."""
        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", [
                    "https://err.eduscol.fr/",
                    "https://ok.eduscol.fr/",
                ]), \
                patch("scraper_eduscol.polite_get",
                      return_value=(None, "timeout", False)), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        output = out.getvalue()
        assert "Erreur" in output
        assert "PROCESSUS ÉDUSCOL TERMINÉ" in output

    def test_page_status_not_200_continues(self):
        """Statut ≠ 200 sur la page → continue."""
        resp_403 = _make_polite_get_response(403)

        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get",
                      return_value=(resp_403, None, False)), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        output = out.getvalue()
        assert "Code : 403" in output

    def test_file_status_not_200_logged(self):
        """Fichier avec statut ≠ 200 → affiché comme échec."""
        page_html = _page_html_with_links([("/fail.pdf", "Fail")])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(500)

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        assert "Statut HTTP 500" in out.getvalue()

    def test_file_error_continues(self):
        """Erreur réseau sur un fichier → continue sans planter."""
        page_html = _page_html_with_links([("/doc.pdf", "Doc")])
        page_resp = _make_polite_get_response(200, text=page_html)

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return None, "connection reset", False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()) as out, \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        assert "Erreur requête" in out.getvalue()

    def test_existing_file_skipped(self):
        """Fichier déjà présent → sauté, pas de polite_get pour le téléchargement."""
        page_html = _page_html_with_links([("/exist.pdf", "Exist")])
        page_resp = _make_polite_get_response(200, text=page_html)

        get_calls = {"n": 0}

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            get_calls["n"] += 1
            if stream:
                raise AssertionError("Should not download existing file")
            return page_resp, None, False

        def fake_exists(path):
            # Les dossiers principaux existent, le fichier aussi
            return True

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", side_effect=fake_exists), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.extract_and_sort_zip"):
            scrape_eduscol_nsi()

        # Seulement 1 appel polite_get (la page), pas de stream call
        assert get_calls["n"] == 1

    def test_links_without_href_skipped(self):
        """Liens sans href → ignorés silencieusement."""
        page_html = "<html><body><a>No href</a><a href=''>Empty</a></body></html>"
        page_resp = _make_polite_get_response(200, text=page_html)

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get",
                      return_value=(page_resp, None, False)), \
                patch("scraper_eduscol.os.makedirs"):
            # Ne doit pas planter
            scrape_eduscol_nsi()

    def test_download_name_fallback(self):
        """Nom 'download' → remplacé par 'ressource_officielle'."""
        page_html = _page_html_with_links([("/download", "download")])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(
            200, chunks=[b"data"],
            headers={"content-type": "application/pdf"},
        )

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.os.path.getsize", return_value=10), \
                patch("scraper_eduscol.compute_sha256", return_value="aaa"), \
                patch("builtins.open", MagicMock()):
            scrape_eduscol_nsi()

    def test_extension_detection_zip_docx_xlsx(self):
        """Détection d'extension sur les différentes variantes."""
        links = [
            ("/archive.zip", "Archive"),
            ("/doc.docx", "Document"),
            ("/data.xlsx", "Données"),
        ]
        page_html = _page_html_with_links(links)
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(200, chunks=[b"data"])

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.os.path.getsize", return_value=10), \
                patch("scraper_eduscol.compute_sha256", return_value="aaa"), \
                patch("scraper_eduscol.extract_and_sort_zip"), \
                patch("builtins.open", MagicMock()):
            scrape_eduscol_nsi()

    def test_existing_zip_triggers_extract(self):
        """ZIP déjà présent → extract_and_sort_zip appelé, pas de téléchargement."""
        page_html = _page_html_with_links([("/archive.zip", "Archive")])
        page_resp = _make_polite_get_response(200, text=page_html)

        get_calls = {"n": 0}

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            get_calls["n"] += 1
            if stream:
                raise AssertionError("Should not download existing zip")
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=True), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.extract_and_sort_zip") as mock_extract:
            scrape_eduscol_nsi()

        mock_extract.assert_called_once()
        assert get_calls["n"] == 1  # seulement la page

    def test_non_file_links_skipped(self):
        """Liens qui ne sont ni fichiers ni routes Drupal → ignorés."""
        page_html = _page_html_with_links([
            ("/about", "À propos"),
            ("/contact", "Contact"),
        ])
        page_resp = _make_polite_get_response(200, text=page_html)

        get_calls = {"n": 0}

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            get_calls["n"] += 1
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.makedirs"):
            scrape_eduscol_nsi()

        # Seulement 1 appel (la page), aucun fichier téléchargé
        assert get_calls["n"] == 1

    def test_download_with_empty_chunks(self):
        """Chunks vides dans le stream → ignorés, fichier correct."""
        page_html = _page_html_with_links([("/doc.pdf", "Doc")])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(
            200, chunks=[b"data", b"", b"more"],
            headers={"content-type": "application/pdf"},
        )

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.os.path.getsize", return_value=8), \
                patch("scraper_eduscol.compute_sha256", return_value="aaa"), \
                patch("builtins.open", MagicMock()):
            scrape_eduscol_nsi()

    def test_drupal_download_route_detected(self):
        """Route Drupal /download détectée comme lien fichier."""
        page_html = _page_html_with_links([
            ("/fichier/sujet_bac", "Sujet Bac"),
        ])
        page_resp = _make_polite_get_response(200, text=page_html)
        file_resp = _make_polite_get_response(200, chunks=[b"data"])

        calls = {"stream": 0}

        def fake_polite_get(session, url, *, robots, throttle, min_delay=1.2, stream=False):
            if stream:
                calls["stream"] += 1
                return file_resp, None, False
            return page_resp, None, False

        with redirect_stdout(io.StringIO()), \
                patch.object(eduscol_module, "EDUSCOL_NSI_URLS", ["https://fake.eduscol.fr/"]), \
                patch("scraper_eduscol.polite_get", side_effect=fake_polite_get), \
                patch("scraper_eduscol.os.path.exists", return_value=False), \
                patch("scraper_eduscol.os.makedirs"), \
                patch("scraper_eduscol.os.path.getsize", return_value=10), \
                patch("scraper_eduscol.compute_sha256", return_value="aaa"), \
                patch("builtins.open", MagicMock()):
            scrape_eduscol_nsi()

        assert calls["stream"] >= 1


# ---------------------------------------------------------------------------
# extract_and_sort_zip — tri et dédoublonnage avec de vraies archives
# ---------------------------------------------------------------------------

def _create_zip(path: Path, files: dict[str, bytes]) -> None:
    """Crée une vraie archive ZIP contenant les fichiers donnés."""
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)


class TestExtractAndSortZipReal:

    def test_two_same_named_files_from_different_archives_both_kept(self):
        """Deux archives contenant notes.py (contenus différents) → les deux survivent."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            zip1 = Path(tmp) / "archive1.zip"
            zip2 = Path(tmp) / "archive2.zip"
            _create_zip(zip1, {"notes.py": b"# version A\nprint('hello')\n"})
            _create_zip(zip2, {"notes.py": b"# version B\nprint('world')\n"})

            with redirect_stdout(io.StringIO()):
                extract_and_sort_zip(str(zip1), str(base))
                extract_and_sort_zip(str(zip2), str(base))

            python_dir = base / "Archives_Extraites_Triees" / "01_Codes_Python"
            assert python_dir.exists()
            files = sorted(f.name for f in python_dir.iterdir())
            assert "notes.py" in files
            assert "notes_doublon_1.py" in files
            # Contenus différents
            contents = {f.name: f.read_bytes() for f in python_dir.iterdir()}
            assert contents["notes.py"] != contents["notes_doublon_1.py"]

    def test_three_same_named_files_all_kept(self):
        """Trois archives avec le même fichier → notes.py, _doublon_1, _doublon_2."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            for i in range(3):
                zp = Path(tmp) / f"archive{i}.zip"
                _create_zip(zp, {"script.py": f"# v{i}\n".encode()})
                with redirect_stdout(io.StringIO()):
                    extract_and_sort_zip(str(zp), str(base))

            python_dir = base / "Archives_Extraites_Triees" / "01_Codes_Python"
            files = sorted(f.name for f in python_dir.iterdir())
            assert files == ["script.py", "script_doublon_1.py", "script_doublon_2.py"]

    def test_categorization_by_extension(self):
        """Fichiers de différentes extensions → triés dans les bonnes catégories."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            zp = Path(tmp) / "mixed.zip"
            _create_zip(zp, {
                "cours.pdf": b"PDF",
                "algo.py": b"# python",
                "data.csv": b"a,b",
                "page.html": b"<html>",
                "rapport.docx": b"docx",
                "photo.png": b"PNG",
                "other.xyz": b"xyz",
                "noext": b"noext",
            })
            with redirect_stdout(io.StringIO()):
                extract_and_sort_zip(str(zp), str(base))

            tree = base / "Archives_Extraites_Triees"
            assert (tree / "01_Codes_Python" / "algo.py").exists()
            assert (tree / "02_Sujets_et_Cours_PDF" / "cours.pdf").exists()
            assert (tree / "06_Donnees_et_Configuration" / "data.csv").exists()
            assert (tree / "05_Ressources_Web" / "page.html").exists()
            assert (tree / "03_Documents_Texte" / "rapport.docx").exists()
            assert (tree / "04_Images_et_Graphiques" / "photo.png").exists()
            assert (tree / "07_Autres_XYZ" / "other.xyz").exists()

    def test_hidden_and_macosx_files_skipped(self):
        """Fichiers cachés et __MACOSX sont ignorés."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            zp = Path(tmp) / "mac.zip"
            _create_zip(zp, {
                ".DS_Store": b"junk",
                "__MACOSX/resource.py": b"junk",
                "real.py": b"# real",
            })
            with redirect_stdout(io.StringIO()):
                extract_and_sort_zip(str(zp), str(base))

            python_dir = base / "Archives_Extraites_Triees" / "01_Codes_Python"
            files = [f.name for f in python_dir.iterdir()] if python_dir.exists() else []
            assert "real.py" in files
            assert ".DS_Store" not in files

    def test_temp_dir_cleaned_up(self):
        """Le dossier temporaire d'extraction est nettoyé après traitement."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            zp = Path(tmp) / "clean.zip"
            _create_zip(zp, {"a.py": b"ok"})
            with redirect_stdout(io.StringIO()):
                extract_and_sort_zip(str(zp), str(base))

            temp_dir = base / "_temp_zip_extraction"
            assert not temp_dir.exists()

    def test_temp_dir_absent_does_not_crash(self):
        """Si le dossier temp n'existe pas dans le finally, pas de crash."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "output"
            base.mkdir()

            zp = Path(tmp) / "ok.zip"
            _create_zip(zp, {"a.py": b"ok"})

            # Supprimer le temp_dir avant que finally ne tente le rmtree
            original_extractall = zipfile.ZipFile.extractall

            def extract_then_remove_temp(self, path=None, *args, **kwargs):
                original_extractall(self, path, *args, **kwargs)
                temp = Path(path)
                if temp.exists():
                    shutil.rmtree(temp)

            with redirect_stdout(io.StringIO()), \
                    patch.object(zipfile.ZipFile, "extractall", extract_then_remove_temp):
                extract_and_sort_zip(str(zp), str(base))
