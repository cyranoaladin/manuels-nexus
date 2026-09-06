"""Les quatre producteurs de dimension doivent pouvoir échouer.

Un producteur qui ne trouve jamais rien est indiscernable d'un producteur
correct. Chaque test injecte donc un défaut réel et exige qu'il soit détecté —
c'est la seule façon de distinguer une dimension `passed` d'une dimension
muette. On vérifie aussi qu'aucune preuve ancienne ne peut verdir une dimension
et que `NOT_APPLICABLE` n'est jamais traité comme `PASS`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certification_dimensions as cd  # noqa: E402

fitz = pytest.importorskip("fitz", reason="PyMuPDF requis pour les dimensions print/visual")


# --- Enveloppe de preuve ------------------------------------------------------

def _evidence(**kwargs) -> cd.DimensionEvidence:
    defaults = dict(
        dimension="visual", scope="test", producer="test", producer_version="0",
        evidence_head="a" * 40, input_digest="sha256:" + "0" * 64,
    )
    defaults.update(kwargs)
    return cd.DimensionEvidence(**defaults)


def test_a_dimension_with_no_examined_target_is_never_passed() -> None:
    """Un producteur muet ne peut pas verdir sa dimension."""
    evidence = _evidence()
    assert evidence.coverage.get("targets_examined") in (None, [])
    assert evidence.status == "failed"


def test_a_blocking_finding_forces_failed() -> None:
    evidence = _evidence()
    evidence.coverage = {"targets_examined": ["T1"]}
    assert evidence.status == "passed"
    evidence.findings.append(cd.Finding(target="T1", code="X", detail="d", blocking=True))
    assert evidence.status == "failed"


def test_a_non_blocking_finding_does_not_force_failed() -> None:
    evidence = _evidence()
    evidence.coverage = {"targets_examined": ["T1"]}
    evidence.findings.append(cd.Finding(target="T1", code="X", detail="d", blocking=False))
    assert evidence.status == "passed"


def test_not_applicable_is_not_pass() -> None:
    """Des cibles hors champ ne suffisent pas à faire passer la dimension."""
    evidence = _evidence()
    evidence.not_applicable_targets = {"objects": "4029"}
    assert evidence.status == "failed", "N/A ne doit jamais valoir PASS"


def test_stale_evidence_is_rejected_by_the_gate() -> None:
    payload = {"evidence_head": "a" * 40}
    assert cd.evidence_is_fresh(payload, "a" * 40) is True
    assert cd.evidence_is_fresh(payload, "b" * 40) is False


def test_input_digest_moves_when_an_input_moves(tmp_path: Path) -> None:
    target = tmp_path / "input.json"
    target.write_text("{}", encoding="utf-8")
    before = cd.digest_inputs([target])
    target.write_text('{"x": 1}', encoding="utf-8")
    assert cd.digest_inputs([target]) != before


# --- Mutation visuelle réelle -------------------------------------------------

def _pdf_with(tmp_path: Path, name: str, *, overlap: bool) -> Path:
    """PDF minimal, avec ou sans chevauchement de blocs de texte.

    L'anomalie est un cartouche pivoté qui traverse le paragraphe — le cas
    réaliste d'une figure ou d'un bandeau mal placé. Deux lignes simplement
    superposées ne conviendraient pas : l'extracteur les fusionnerait en un
    seul bloc, et le défaut deviendrait invisible à la mesure.
    """
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    page.insert_text((100, 300), "Produit scalaire et vecteurs orthogonaux", fontsize=12)
    if overlap:
        page.insert_textbox(
            fitz.Rect(150, 250, 400, 350), "BANDEAU PIVOTE QUI TRAVERSE",
            fontsize=14, rotate=90,
        )
    else:
        page.insert_text((100, 420), "Seconde partie du chapitre", fontsize=12)
    path = tmp_path / name
    document.save(path)
    document.close()
    return path


def _blocks(path: Path) -> list[tuple[float, float, float, float]]:
    document = fitz.open(path)
    blocks = [tuple(b[:4]) for b in document[0].get_text("blocks") if b[4].strip()]
    document.close()
    return blocks


def test_visual_producer_detects_a_synthetic_overlap(tmp_path: Path) -> None:
    """Mutation obligatoire (§16) : une anomalie visuelle injectée est vue."""
    import build_dimension_visual as visual

    clean = visual.detect_overlaps(_blocks(_pdf_with(tmp_path, "clean.pdf", overlap=False)))
    assert clean == [], "le rendu sain ne doit produire aucun chevauchement"

    mutated = visual.detect_overlaps(_blocks(_pdf_with(tmp_path, "mutated.pdf", overlap=True)))
    assert mutated, "le chevauchement injecté doit être détecté"
    assert max(ratio for _, _, ratio in mutated) > visual.OVERLAP_AREA_RATIO


def test_visual_ink_ratio_separates_blank_from_dense(tmp_path: Path) -> None:
    """Une page vide et une page saturée doivent tomber de part et d'autre des seuils."""
    import build_dimension_visual as visual

    document = fitz.open()
    document.new_page(width=595, height=842)
    document.new_page(width=595, height=842)
    # `new_page` invalide les objets Page déjà obtenus : on les relit par index.
    document[1].draw_rect(document[1].rect, color=(0, 0, 0), fill=(0, 0, 0))

    assert visual.ink_ratio(document[0]) < visual.MIN_INK_RATIO
    assert visual.ink_ratio(document[1]) > visual.MAX_INK_RATIO
    document.close()


def test_visual_is_not_an_alias_of_print() -> None:
    """Les deux dimensions doivent poser des questions différentes."""
    import build_dimension_print as printer
    import build_dimension_visual as visual

    print_source = Path(printer.__file__).read_text(encoding="utf-8")
    visual_source = Path(visual.__file__).read_text(encoding="utf-8")
    print_codes = {"MISSING_FONT", "MISSING_GLYPH", "BROKEN_BOOKMARK",
                   "OUTSIDE_PROVISIONAL_SAFE_PRINT_AREA"}
    visual_codes = {"OVERLAPPING_TEXT_BLOCKS", "PAGE_SATURATED", "BLOCK_WIDER_THAN_TEXT_COLUMN"}
    assert print_codes <= set(re_codes(print_source))
    assert visual_codes <= set(re_codes(visual_source))
    assert not (print_codes & set(re_codes(visual_source)))


def re_codes(source: str) -> list[str]:
    import re

    return re.findall(r'code="([A-Z_]+)"', source)


# --- Mutation mathématique réelle --------------------------------------------

def test_mathematics_producer_fails_on_a_false_assertion() -> None:
    import build_dimension_mathematics as maths

    # Le bloc déclare lui-même ses symboles, comme le font les fiches réelles.
    preamble = ["from sympy import symbols, sin, cos, simplify", "x = symbols('x')"]

    ok, _ = maths._run_assertions(
        preamble + ["assert simplify(sin(x)**2 + cos(x)**2 - 1) == 0"]
    )
    assert ok is True

    bad, detail = maths._run_assertions(
        preamble + ["assert simplify(sin(x)**2 + cos(x)**2) == 0"]
    )
    assert bad is False and detail, "une assertion fausse doit être signalée"


def test_mathematics_extracts_the_program_behind_the_percent_signs() -> None:
    """Les blocs réels s'écrivent en commentaires LaTeX : `% assert ...`."""
    import build_dimension_mathematics as maths

    block = "\n".join([
        "% from sympy import symbols, simplify",
        "% x = symbols('x', positive=True)",
        "% assert simplify(x/x - 1) == 0",
        "",
    ])
    program = maths.extract_program(block)
    assert program == [
        "from sympy import symbols, simplify",
        "x = symbols('x', positive=True)",
        "assert simplify(x/x - 1) == 0",
    ]
    ok, _ = maths._run_assertions(program)
    assert ok is True


# --- Régulation : les alias locaux ne sont pas du hors-programme --------------

def test_regulation_distinguishes_local_aliases_from_out_of_programme() -> None:
    import build_dimension_regulation as regulation

    for alias in ("C1", "C12", "TSPE-TRIGONOMETRIE-C1", "BO-PREAMBULE-DEMARCHE-DE-PROJET"):
        assert regulation.LOCAL_ALIAS.match(alias), alias
    for real in ("T-ALGO-01D", "INVENTED-CODE-42"):
        assert not regulation.LOCAL_ALIAS.match(real), real
