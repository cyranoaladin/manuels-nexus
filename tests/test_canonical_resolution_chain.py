"""Régression infra: résolution canonique des gabarits à toutes les profondeurs.

Bug corrigé (2026-08-19): l'assembleur NSI compile avec cwd=NSI/ (profondeur 1)
alors que les chaînes de résolution ne testaient que `gabarits/common/…`
(racine) et `../../gabarits/common/…` (profondeur 2, ex. Mathematiques/
manuel-maths). Le fallback silencieux `\\RequirePackage{nexus-charte}` était
alors insoluble et cassait les 4 builds NSI.

Contrat: source canonique UNIQUE sous gabarits/common ; les adaptateurs de
discipline et la macro canonique \\nxRequireCommonModule doivent résoudre
explicitement les trois profondeurs, sans copie divergente ni symlink.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

WRAPPERS = [
    "nexus-manuel.cls",
    "nexus-manuel-v5.cls",
    "nexus-charte-v6.sty",
    "nexus-pont-v6.sty",
    "nexus-decor.sty",
    "nexus-figures-bib.sty",
    "nexus-exercices-v6.sty",
    "nexus-couverture.sty",
    "nexus-boites-v6.sty",
    "nexus-pages-froides.sty",
]


@pytest.mark.parametrize("name", WRAPPERS)
def test_discipline_wrappers_resolve_all_depths_and_stay_identical(name):
    maths = ROOT / "Mathematiques/manuel-maths/gabarits" / name
    nsi = ROOT / "NSI/gabarits" / name
    for wrapper in (maths, nsi):
        content = wrapper.read_text(encoding="utf-8")
        assert "../../gabarits/common/" in content, wrapper
        assert "../gabarits/common/" in content.replace(
            "../../gabarits/common/", ""
        ), f"{wrapper}: branche profondeur 1 absente"
    assert maths.read_bytes() == nsi.read_bytes(), (
        "adaptateurs Math/NSI divergents: " + name
    )


def test_canonical_module_macro_resolves_all_depths():
    charte = (ROOT / "gabarits/common/nexus-charte.sty").read_text(
        encoding="utf-8"
    )
    macro = charte.split("\\newcommand{\\nxRequireCommonModule}", 1)[1]
    macro = macro.split("\n}\n", 1)[0]
    assert "gabarits/common/#1.sty" in macro
    assert "../../gabarits/common/#1.sty" in macro
    assert "../gabarits/common/#1.sty" in macro.replace(
        "../../gabarits/common/#1.sty", ""
    ), "branche profondeur 1 absente de nxRequireCommonModule"


def test_no_stray_canonical_copies():
    """La source canonique reste unique: aucun nexus-charte.sty ni
    nexus-manuel.cls hors gabarits/common (les adaptateurs portent d'autres
    noms de fichiers, sauf les wrappers de redirection déclarés)."""
    allowed = {
        ROOT / "gabarits/common/nexus-charte.sty",
        ROOT / "gabarits/common/nexus-manuel.cls",
        ROOT / "Mathematiques/manuel-maths/gabarits/nexus-manuel.cls",
        ROOT / "NSI/gabarits/nexus-manuel.cls",
    }
    for pattern in ("nexus-charte.sty", "nexus-manuel.cls"):
        for path in ROOT.glob(f"Mathematiques/**/{pattern}"):
            if ".worktrees" in path.parts or "build" in path.parts:
                continue
            assert path in allowed, f"copie non canonique: {path}"
        for path in ROOT.glob(f"NSI/**/{pattern}"):
            if ".worktrees" in path.parts or "build" in path.parts:
                continue
            assert path in allowed, f"copie non canonique: {path}"
        for path in ROOT.glob(f"gabarits/**/{pattern}"):
            assert path in allowed, f"copie non canonique: {path}"
