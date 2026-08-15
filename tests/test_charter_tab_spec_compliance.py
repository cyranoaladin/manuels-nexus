"""Test de conformité aux spécifications de la charte visuelle (spécification du 20 juillet 2026).

Vérifie que les modules de charte respectent scrupuleusement la spécification validée :
docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md
- Longueur minimale de l'onglet : 16 mm
- Padding longitudinal : +6 mm (3 mm de chaque côté)
- Police d'onglet : \\fontsize{6}{6}
"""

from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

MATH_CHARTE = ROOT / "Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty"
NSI_CHARTE = ROOT / "NSI/gabarits/nexus-charte-v6.sty"

@pytest.mark.parametrize("charte_path", [MATH_CHARTE, NSI_CHARTE])
def test_tab_length_minimum_is_16mm(charte_path):
    content = charte_path.read_text(encoding="utf-8")
    assert "\\ifdim\\nxVOngletLength<16mm" in content
    assert "\\setlength{\\nxVOngletLength}{16mm}" in content

@pytest.mark.parametrize("charte_path", [MATH_CHARTE, NSI_CHARTE])
def test_tab_length_padding_is_6mm(charte_path):
    content = charte_path.read_text(encoding="utf-8")
    assert "\\dimexpr\\wd\\nxVOngletTextBox+6mm\\relax" in content

@pytest.mark.parametrize("charte_path", [MATH_CHARTE, NSI_CHARTE])
def test_tab_font_size_is_6_pt(charte_path):
    content = charte_path.read_text(encoding="utf-8")
    assert "\\fontsize{6}{6}" in content
