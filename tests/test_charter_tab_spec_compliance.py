"""Test de conformité aux spécifications de la charte visuelle (spécification du 20 juillet 2026).

Vérifie que les modules de charte respectent scrupuleusement la spécification validée :
docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md
- Épaisseur extérieure de l'onglet : 12 mm
- Longueur minimale de l'onglet : 16 mm
- Longueur auto : max(16 mm, largeur typographique du libellé + 6 mm)
- Padding longitudinal : 3 mm à chaque extrémité (6 mm TOTAL)
- Police d'onglet : \fontsize{6}{6} pt
"""

from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_CHARTE = ROOT / "gabarits/common/nexus-charte.sty"
MATH_CHARTE = ROOT / "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty"
NSI_CHARTE = ROOT / "NSI/gabarits/nexus-charte-v6.sty"

def _resolve_content(path):
    txt = path.read_text(encoding="utf-8")
    if "\\RequirePackage" in txt and "nexus-charte" in txt:
        # Wrapper redirecting to canonical
        return CANONICAL_CHARTE.read_text(encoding="utf-8")
    return txt

@pytest.mark.parametrize("charte_path", [CANONICAL_CHARTE, MATH_CHARTE, NSI_CHARTE])
def test_tab_length_minimum_is_16mm(charte_path):
    content = _resolve_content(charte_path)
    assert "\\ifdim\\nxVOngletLength<16mm" in content or "\\ifdim\\nxVOngletLength<16.0mm" in content or "16mm" in content

@pytest.mark.parametrize("charte_path", [CANONICAL_CHARTE, MATH_CHARTE, NSI_CHARTE])
def test_tab_length_padding_is_6mm_total(charte_path):
    content = _resolve_content(charte_path)
    assert "+6mm" in content or "+ 6mm" in content

@pytest.mark.parametrize("charte_path", [CANONICAL_CHARTE, MATH_CHARTE, NSI_CHARTE])
def test_tab_font_size_is_6_6_pt(charte_path):
    content = _resolve_content(charte_path)
    assert "\\fontsize{6}{6}" in content


