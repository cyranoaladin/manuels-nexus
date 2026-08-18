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


CANONICAL_CLASS = ROOT / "gabarits/common/nexus-manuel.cls"


@pytest.mark.parametrize("source_path", [CANONICAL_CHARTE, CANONICAL_CLASS])
def test_tab_outer_thickness_is_12mm(source_path):
    """Épaisseur extérieure contractuelle : 12 mm visibles sur la page.

    Page impaire : rectangle de xshift=-12mm au bord (le +1mm hors page est
    l'arête de coupe). Page paire : miroir jusqu'à xshift=12mm. L'ancienne
    géométrie -10mm/+10mm (11 mm dont 10 visibles) violait la spec du
    2026-07-20 et est interdite.
    """
    content = source_path.read_text(encoding="utf-8")
    assert "xshift=-12mm" in content
    assert "xshift=12mm" in content
    assert "xshift=-10mm" not in content
    assert (
        "[xshift=10mm,yshift=\\ongletY" not in content
    ), "géométrie 10mm interdite pour l'onglet"
    assert "xshift=-6mm]current page.north east" in content
    assert "xshift=6mm]current page.north west" in content


