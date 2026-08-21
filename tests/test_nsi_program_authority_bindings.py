from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_PATH = ROOT / "docs/programmes/PROGRAMMES_2026_2027.yaml"
SOURCES_MD_PATH = ROOT / "NSI/sources/SOURCES.md"

BINDINGS = {
    "SRC-BO2019-NSI-PREMIERE": {
        "arrete": "MENE1901633A",
        "fichier": (
            "NSI/corpus_nsi/00_programmes_officiels/"
            "programme_nsi_premiere.pdf"
        ),
        "sha256": (
            "7ca9a32e1823be6c1120cb0417324c3c"
            "b01688d1d194c7614a88ea851ccc60b0"
        ),
        "url": "https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm",
        "annexe_pdf": (
            "https://cache.media.education.gouv.fr/file/"
            "SP1-MEN-22-1-2019/26/8/spe633_annexe_1063268.pdf"
        ),
    },
    "SRC-BO2019-NSI-TERMINALE": {
        "arrete": "MENE1921247A",
        "fichier": (
            "NSI/corpus_nsi/00_programmes_officiels/"
            "programme_nsi_terminale.pdf"
        ),
        "sha256": (
            "10ce34666edd722a3d8d86642a9f1ac2"
            "05c7a9d128d6142a17effcba2fb85e69"
        ),
        "url": "https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm",
        "annexe_pdf": (
            "https://cache.media.education.gouv.fr/file/"
            "SPE8_MENJ_25_7_2019/93/3/spe247_annexe_1158933.pdf"
        ),
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_nsi_program_authority_bindings_match_tracked_official_copies() -> None:
    authority = yaml.safe_load(AUTHORITY_PATH.read_text(encoding="utf-8"))
    sources = authority["sources"]

    for authority_key, expected in BINDINGS.items():
        record = sources[authority_key]
        for field, value in expected.items():
            assert record[field] == value

        relative_path = expected["fichier"]
        pdf_path = ROOT / relative_path
        assert pdf_path.is_file()
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative_path],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert _sha256(pdf_path) == expected["sha256"]


def test_nsi_sources_ledger_names_the_same_tracked_copies() -> None:
    sources_md = SOURCES_MD_PATH.read_text(encoding="utf-8")

    for expected in BINDINGS.values():
        row = (
            f"| `{expected['fichier']}` | `{expected['arrete']}` | "
            f"`{expected['url']}` | `{expected['annexe_pdf']}` | "
            f"`{expected['sha256']}` |"
        )
        assert sources_md.count(row) == 1
