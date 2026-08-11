# -*- coding: utf-8 -*-
"""Tests pour provenance.py — aucun réseau, disque sur tmp_path."""

from __future__ import annotations

import json

from scrapping_NSI.provenance import (
    PROVENANCE_REQUIRED_KEYS,
    compute_sha256,
    generate_notice_sources,
    guess_license,
    validate_provenance_record,
    write_provenance_record,
)


# ---------------------------------------------------------------------------
# compute_sha256
# ---------------------------------------------------------------------------

class TestComputeSha256:

    def test_consistent_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        h1 = compute_sha256(f)
        h2 = compute_sha256(f)
        assert h1 == h2
        assert len(h1) == 64  # sha256 hex

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"aaa")
        f2.write_bytes(b"bbb")
        assert compute_sha256(f1) != compute_sha256(f2)


# ---------------------------------------------------------------------------
# guess_license
# ---------------------------------------------------------------------------

class TestGuessLicense:

    def test_unknown_when_no_html(self):
        assert guess_license(None) == "unknown"

    def test_unknown_when_empty(self):
        assert guess_license("") == "unknown"

    def test_unknown_when_no_markers(self):
        assert guess_license("<html><body>Cours de NSI</body></html>") == "unknown"

    def test_detects_creative_commons_generic(self):
        html = '<footer>Contenu sous Creative Commons</footer>'
        result = guess_license(html)
        assert "Creative Commons" in result

    def test_detects_cc_by_sa(self):
        html = '<p>Licence CC BY-SA 4.0</p>'
        result = guess_license(html)
        assert "CC BY" in result.upper()

    def test_detects_mit(self):
        html = '<p>Released under the Licence MIT</p>'
        assert guess_license(html) == "MIT"

    def test_detects_gpl(self):
        html = '<p>Code under GPL v3</p>'
        assert "GPL" in guess_license(html)

    def test_detects_license_link(self):
        html = '<a href="/LICENSE">Licence</a>'
        result = guess_license(html)
        assert "licence" in result.lower() or "license" in result.lower()

    def test_creativecommons_org_link(self):
        html = '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY</a>'
        result = guess_license(html)
        assert "CC BY" in result.upper() or "Creative Commons" in result


# ---------------------------------------------------------------------------
# write_provenance_record
# ---------------------------------------------------------------------------

class TestWriteProvenanceRecord:

    def _write_one(self, tmp_path, **overrides):
        defaults = {
            "sha256": "abc123" * 10 + "abcd",
            "filename": "cours.pdf",
            "source_url": "https://example.com/cours.pdf",
            "site_name": "Example NSI",
            "page_url": "https://example.com/nsi/",
            "http_status": 200,
            "content_type": "application/pdf",
            "byte_count": 12345,
            "robots_allowed": True,
            "license_guess": "unknown",
        }
        defaults.update(overrides)
        out = tmp_path / "provenance.jsonl"
        write_provenance_record(out, **defaults)
        return out

    def test_writes_valid_jsonl(self, tmp_path):
        out = self._write_one(tmp_path)
        lines = out.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert validate_provenance_record(record)

    def test_schema_has_exactly_11_required_keys(self, tmp_path):
        """L'enregistrement contient exactement les 11 clés spécifiées."""
        out = self._write_one(tmp_path, byte_count=9876)
        record = json.loads(out.read_text(encoding="utf-8").strip())

        expected_keys = {
            "sha256", "filename", "source_url", "site_name", "page_url",
            "http_status", "content_type", "bytes", "retrieved_at",
            "license_guess", "robots_allowed",
        }
        assert expected_keys.issubset(record.keys())
        # bytes = taille réelle passée en paramètre
        assert record["bytes"] == 9876
        # retrieved_at ISO-8601 avec fuseau
        from datetime import datetime
        dt = datetime.fromisoformat(record["retrieved_at"])
        assert dt.tzinfo is not None, "retrieved_at doit avoir un fuseau horaire"
        # license_guess par défaut
        assert record["license_guess"] == "unknown"
        # robots_allowed est booléen
        assert isinstance(record["robots_allowed"], bool)

    def test_all_required_keys_present_no_unknown(self, tmp_path):
        """Sans duplicate_of, l'enregistrement contient exactement les 11 clés requises."""
        out = self._write_one(tmp_path)
        record = json.loads(out.read_text(encoding="utf-8").strip())
        assert set(record.keys()) == PROVENANCE_REQUIRED_KEYS

    def test_with_duplicate_of_still_valid(self, tmp_path):
        """Avec duplicate_of (optionnel autorisé), la validation passe."""
        out = self._write_one(tmp_path, duplicate_of="abc")
        record = json.loads(out.read_text(encoding="utf-8").strip())
        assert validate_provenance_record(record)
        assert "duplicate_of" in record

    def test_append_mode(self, tmp_path):
        """Deux écritures successives → deux lignes."""
        out = self._write_one(tmp_path, filename="a.pdf")
        write_provenance_record(
            out,
            sha256="def456" * 10 + "defg",
            filename="b.pdf",
            source_url="https://example.com/b.pdf",
            site_name="Example NSI",
            page_url="https://example.com/nsi/",
            http_status=200,
            content_type="application/pdf",
            byte_count=9999,
            robots_allowed=True,
        )
        lines = out.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_duplicate_of_field(self, tmp_path):
        out = self._write_one(tmp_path, duplicate_of="original_sha256")
        record = json.loads(out.read_text(encoding="utf-8").strip())
        assert record["duplicate_of"] == "original_sha256"

    def test_no_duplicate_of_by_default(self, tmp_path):
        out = self._write_one(tmp_path)
        record = json.loads(out.read_text(encoding="utf-8").strip())
        assert "duplicate_of" not in record

    def test_retrieved_at_is_iso(self, tmp_path):
        out = self._write_one(tmp_path)
        record = json.loads(out.read_text(encoding="utf-8").strip())
        # ISO-8601 parse check
        from datetime import datetime
        datetime.fromisoformat(record["retrieved_at"])

    def test_writes_to_file_object(self, tmp_path):
        """Accepte aussi un TextIO."""
        import io
        buf = io.StringIO()
        write_provenance_record(
            buf,
            sha256="aaa",
            filename="x.pdf",
            source_url="https://x.com/x.pdf",
            site_name="X",
            page_url="https://x.com/",
            http_status=200,
            content_type="application/pdf",
            byte_count=100,
            robots_allowed=True,
        )
        record = json.loads(buf.getvalue().strip())
        assert record["filename"] == "x.pdf"


# ---------------------------------------------------------------------------
# validate_provenance_record
# ---------------------------------------------------------------------------

class TestValidateProvenanceRecord:

    def test_valid_record(self):
        record = {
            "sha256": "abc", "filename": "f.pdf", "source_url": "http://x",
            "site_name": "X", "page_url": "http://x/", "http_status": 200,
            "content_type": "application/pdf", "bytes": 100,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown", "robots_allowed": True,
        }
        assert validate_provenance_record(record) is True

    def test_missing_key_invalid(self):
        record = {"sha256": "abc", "filename": "f.pdf"}
        assert validate_provenance_record(record) is False

    def test_each_required_key_removal_invalidates(self):
        """Retirer n'importe laquelle des 11 clés requises → invalide."""
        full = {
            "sha256": "abc", "filename": "f.pdf", "source_url": "http://x",
            "site_name": "X", "page_url": "http://x/", "http_status": 200,
            "content_type": "application/pdf", "bytes": 100,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown", "robots_allowed": True,
        }
        for key in PROVENANCE_REQUIRED_KEYS:
            partial = {k: v for k, v in full.items() if k != key}
            assert validate_provenance_record(partial) is False, f"Manque {key} devrait invalider"

    def test_unknown_key_invalidates(self):
        """Une clé inconnue (hors requises + optionnelles) → invalide."""
        record = {
            "sha256": "abc", "filename": "f.pdf", "source_url": "http://x",
            "site_name": "X", "page_url": "http://x/", "http_status": 200,
            "content_type": "application/pdf", "bytes": 100,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown", "robots_allowed": True,
            "rogue_field": "should fail",
        }
        assert validate_provenance_record(record) is False

    def test_duplicate_of_optional_key_valid(self):
        """duplicate_of est une clé optionnelle autorisée."""
        record = {
            "sha256": "abc", "filename": "f.pdf", "source_url": "http://x",
            "site_name": "X", "page_url": "http://x/", "http_status": 200,
            "content_type": "application/pdf", "bytes": 100,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown", "robots_allowed": True,
            "duplicate_of": "xyz",
        }
        assert validate_provenance_record(record) is True


# ---------------------------------------------------------------------------
# generate_notice_sources
# ---------------------------------------------------------------------------

class TestGenerateNoticeSources:

    def test_empty_provenance(self, tmp_path):
        prov = tmp_path / "provenance.jsonl"
        notice = tmp_path / "NOTICE_SOURCES.md"
        # Pas de fichier provenance
        generate_notice_sources(prov, notice)
        content = notice.read_text(encoding="utf-8")
        assert "Aucune provenance" in content

    def test_generates_table(self, tmp_path):
        prov = tmp_path / "provenance.jsonl"
        records = [
            {
                "sha256": "a", "filename": "cours.pdf",
                "source_url": "https://site-a.fr/cours.pdf",
                "site_name": "Site A", "page_url": "https://site-a.fr/",
                "http_status": 200, "content_type": "application/pdf",
                "bytes": 100, "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license_guess": "CC BY-SA 4.0", "robots_allowed": True,
            },
            {
                "sha256": "b", "filename": "tp.pdf",
                "source_url": "https://site-b.fr/tp.pdf",
                "site_name": "Site B", "page_url": "https://site-b.fr/",
                "http_status": 200, "content_type": "application/pdf",
                "bytes": 200, "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license_guess": "unknown", "robots_allowed": True,
            },
        ]
        with prov.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        notice = tmp_path / "NOTICE_SOURCES.md"
        generate_notice_sources(prov, notice)
        content = notice.read_text(encoding="utf-8")
        assert "Site A" in content
        assert "Site B" in content
        assert "matière première de réécriture" in content
        assert "| Site B" in content
        # Site B a licence unknown → à vérifier = oui
        for line in content.split("\n"):
            if "Site B" in line:
                assert "oui" in line
                break

    def test_skips_blank_lines_in_jsonl(self, tmp_path):
        prov = tmp_path / "provenance.jsonl"
        record = {
            "sha256": "a", "filename": "f.pdf",
            "source_url": "https://s.fr/f.pdf",
            "site_name": "S", "page_url": "https://s.fr/",
            "http_status": 200, "content_type": "application/pdf",
            "bytes": 100, "retrieved_at": "2026-01-01T00:00:00+00:00",
            "license_guess": "unknown", "robots_allowed": True,
        }
        # Écrire avec une ligne vide intercalée
        with prov.open("w", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n\n" + json.dumps(record) + "\n")

        notice = tmp_path / "NOTICE_SOURCES.md"
        generate_notice_sources(prov, notice)
        content = notice.read_text(encoding="utf-8")
        assert "| S |" in content

    def test_aggregates_same_site(self, tmp_path):
        prov = tmp_path / "provenance.jsonl"
        records = [
            {
                "sha256": f"h{i}", "filename": f"f{i}.pdf",
                "source_url": f"https://s.fr/f{i}.pdf",
                "site_name": "Same Site", "page_url": "https://s.fr/",
                "http_status": 200, "content_type": "application/pdf",
                "bytes": 100, "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license_guess": "unknown", "robots_allowed": True,
            }
            for i in range(3)
        ]
        with prov.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        notice = tmp_path / "NOTICE_SOURCES.md"
        generate_notice_sources(prov, notice)
        content = notice.read_text(encoding="utf-8")
        assert "3" in content  # 3 fichiers
