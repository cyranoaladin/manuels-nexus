"""Un devoir declare sa variante ; son corrige declare le devoir.

Cinq chapitres de 1SPE livraient des devoirs A et B dont aucun ne declarait
`version`, et des corriges dont aucun ne declarait `evaluation_ref`. Les
fichiers existaient et se correspondaient, mais rien dans les objets ne le
DISAIT : la matrice les comptait donc comme corriges orphelins, sujets sans
corrige et variantes manquantes.

L'appariement n'est pas devine a partir du nom de fichier ni de l'ordre du
repertoire : c'est l'identifiant de l'objet lui-meme qui le porte, un corrige
s'appelant `<identifiant du sujet>-corrige`.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "Mathematiques/manuel-maths/chapitres"

SUFFIX = "-corrige"


def _meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0])


def _premiere() -> list[Path]:
    return sorted(p for p in CHAPTERS.iterdir() if p.name.startswith("1SPE-"))


def test_every_written_assessment_declares_its_variant() -> None:
    undeclared = []
    for chapter in _premiere():
        directory = chapter / "evaluations"
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.tex")):
            meta = _meta(path)
            if meta.get("type_objet") != "evaluation":
                continue
            if str(meta.get("version") or "").strip().upper() not in {"A", "B"}:
                undeclared.append(meta.get("id"))
    assert undeclared == [], f"devoirs sans variante declaree : {undeclared}"


def test_every_assessment_correction_declares_the_subject_it_corrects() -> None:
    unlinked = []
    for chapter in _premiere():
        directory = chapter / "evaluations"
        if not directory.is_dir():
            continue
        subjects = {
            _meta(p)["id"]
            for p in directory.glob("*.tex")
            if _meta(p).get("type_objet") == "evaluation"
        }
        for path in sorted(directory.glob("*.tex")):
            meta = _meta(path)
            if meta.get("type_objet") != "corrige_evaluation":
                continue
            reference = meta.get("evaluation_ref")
            if reference not in subjects:
                unlinked.append(meta.get("id"))
            else:
                # La preuve de l'appariement est portee par l'identifiant.
                assert meta["id"] == reference + SUFFIX, meta["id"]
    assert unlinked == [], f"corriges sans devoir declare : {unlinked}"


def test_assessment_corrections_use_one_vocabulary_across_the_collection() -> None:
    """Deux orthographes du meme type rendaient deux objets invisibles.

    `build_1spe_suites_human_review_packet` et `review_1nsi_content` ne
    reconnaissent que `corrige_evaluation` : un corrige orthographie
    `evaluation_corrige` passait au travers sans qu'aucune verdict ne soit
    rouge. L'invariant porte donc sur toute la collection, pas sur 1SPE.
    """
    spellings: dict[str, list[str]] = {}
    for path in sorted(ROOT.glob("*/**/evaluations/*.tex")):
        meta = _meta(path)
        kind = meta.get("type_objet")
        if kind and kind != "evaluation":
            spellings.setdefault(kind, []).append(meta.get("id"))
    assert sorted(spellings) == ["corrige_evaluation"], {
        k: v[:3] for k, v in spellings.items()
    }


def test_each_written_subject_has_exactly_one_correction() -> None:
    for chapter in _premiere():
        directory = chapter / "evaluations"
        if not directory.is_dir():
            continue
        subjects, references = set(), []
        for path in sorted(directory.glob("*.tex")):
            meta = _meta(path)
            if meta.get("type_objet") == "evaluation":
                subjects.add(meta["id"])
            elif meta.get("type_objet") == "corrige_evaluation":
                references.append(meta.get("evaluation_ref"))
        assert sorted(references) == sorted(subjects), chapter.name
        assert len(references) == len(set(references)), chapter.name
