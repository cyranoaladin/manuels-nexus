"""Verrouille la separation des remediations et corriges 1NSI."""

import hashlib
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapitres"
META_RE = re.compile(r"^% META: (\{.*\})$", re.MULTILINE)
EXERCISE_RE = re.compile(r"\\begin\{exercice\}\{([^}]+)\}")
CORRECTION_RE = re.compile(
    r"\\begin\{corrige\}\{([^}]+)\}.*?\\end\{corrige\}",
    re.DOTALL,
)

EXPECTED = {
    "1NSI-ALGO-DICHO-GLOUTON-KNN/remediation/1NSI-ADGK-RE-C1.tex": (
        "1NSI-ALGO-DICHO-GLOUTON-KNN/corriges/1NSI-ADGK-RE-C1-CORRIGE.tex",
        "1NSI-ADGK-RE-C1-EX1",
        "38bf1cadf40b1e6d4edf301aeff79f28c12ccf8e423c434c4c948940fdf8510c",
    ),
    "1NSI-ALGO-PARCOURS-TRIS/remediation/1NSI-AGT-RE-C5.tex": (
        "1NSI-ALGO-PARCOURS-TRIS/corriges/1NSI-AGT-RE-C5-CORRIGE.tex",
        "1NSI-AGT-RE-C5-EX1",
        "1b940570a28f3516b319ad22928181987eaa5ff6a80c3acee6f34afca0aa0bfe",
    ),
    "1NSI-ARCHITECTURE-OS/remediation/1NSI-ARCHITECTURE-OS-RE-C5.tex": (
        "1NSI-ARCHITECTURE-OS/corriges/1NSI-ARCHITECTURE-OS-RE-C5-CORRIGE.tex",
        "1NSI-ARCHOS-RE-C5-EX1",
        "1fd440fa840751c3aeef1bf55584673685097a2456c93b552efa56622ea3226c",
    ),
    "1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex": (
        "1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex",
        "1NSI-LANG-RE-C4-EX1",
        "666c755695eb32f52c596f5739df7a3c990be37a2fbdc96f7b588c11cc3cfb12",
    ),
    "1NSI-PROJET-METHODES/remediation/1NSI-PM-RE-C3.tex": (
        "1NSI-PROJET-METHODES/corriges/1NSI-PM-RE-C3-CORRIGE.tex",
        "1NSI-PM-RE-C3-EX1",
        "6fb8fab1aa6155dcffc4872c8bc8337cedb207a03a61d8ae08ca0f4c7db18e47",
    ),
    "1NSI-RESEAUX/remediation/1NSI-RESEAUX-RE-C1.tex": (
        "1NSI-RESEAUX/corriges/1NSI-RESEAUX-RE-C1-CORRIGE.tex",
        "1NSI-RES-RE-C1-EX1",
        "e4c71b57e92a33a93a9d90ff33431a59aec8773c57e54ea387253aac5d85498f",
    ),
    "1NSI-TABLES/remediation/1NSI-TABLES-RE-C2.tex": (
        "1NSI-TABLES/corriges/1NSI-TABLES-RE-C2-CORRIGE.tex",
        "1NSI-TAB-RE-C2-EX1",
        "b7d1f5b9fe97b2d1ad141c55674e44aead8703474b54230c06e489512f4c0a1c",
    ),
    "1NSI-TYPES-BASE/remediation/1NSI-TYPES-BASE-RE-C3.tex": (
        "1NSI-TYPES-BASE/corriges/1NSI-TYPES-BASE-RE-C3-CORRIGE.tex",
        "1NSI-TB-RE-C3-EX1",
        "9e8590d3c4acb329724df9071e03624d196ed8899ee6b6fabf349ad1533a0ca4",
    ),
    "1NSI-WEB-IHM/remediation/1NSI-WEB-IHM-RE-C9.tex": (
        "1NSI-WEB-IHM/corriges/1NSI-WEB-IHM-RE-C9-CORRIGE.tex",
        "1NSI-WEB-RE-C9-EX1",
        "4869644f9734c9d79a43e66e2aab5b15d955cb9f776773bc3050674c93e5a96a",
    ),
}


def _read(relative_path: str) -> tuple[Path, str]:
    path = CHAPTERS / relative_path
    return path, path.read_text(encoding="utf-8")


def _meta(text: str) -> dict:
    match = META_RE.search(text)
    assert match is not None, "en-tete META manquant"
    return json.loads(match.group(1))


@pytest.mark.parametrize("source_relative", EXPECTED)
def test_remediation_source_contains_only_one_exercise(source_relative):
    _, source_text = _read(source_relative)

    assert "\\begin{corrige}" not in source_text
    assert len(EXERCISE_RE.findall(source_text)) == 1


@pytest.mark.parametrize("source_relative", EXPECTED)
def test_companion_metadata_and_environment_match_source(source_relative):
    companion_relative, expected_environment_id, _ = EXPECTED[source_relative]
    source_path, source_text = _read(source_relative)
    companion_path, companion_text = _read(companion_relative)
    source_meta = _meta(source_text)
    companion_meta = _meta(companion_text)
    chapter = source_path.relative_to(CHAPTERS).parts[0]

    assert companion_meta["id"] == companion_path.stem
    assert companion_meta["chapitre"] == source_meta["chapitre"] == chapter
    assert companion_meta["type_objet"] == "corrige"
    assert companion_meta["exercice_ref"] == source_meta["id"]
    assert companion_meta["capacites"] == source_meta["capacites"]
    assert companion_meta["status"] == "needs_review"
    assert EXERCISE_RE.findall(source_text) == [expected_environment_id]
    assert CORRECTION_RE.findall(companion_text) == [expected_environment_id]


@pytest.mark.parametrize("source_relative", EXPECTED)
def test_companion_preserves_exact_correction_block(source_relative):
    companion_relative, _, expected_sha256 = EXPECTED[source_relative]
    _, companion_text = _read(companion_relative)
    matches = list(CORRECTION_RE.finditer(companion_text))

    assert len(matches) == 1
    actual_sha256 = hashlib.sha256(matches[0].group(0).encode("utf-8")).hexdigest()
    assert actual_sha256 == expected_sha256
