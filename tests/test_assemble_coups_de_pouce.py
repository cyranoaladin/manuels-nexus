import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assemble import collect, ouverture_depuis_contrat  # noqa: E402


def test_collect_places_companion_coups_de_pouce_after_exercises(tmp_path):
    for name in ("cours", "methodes", "exercices"):
        (tmp_path / name).mkdir()
    (tmp_path / "cours" / "10_C1.tex").write_text("", encoding="utf-8")
    (tmp_path / "exercices" / "EX-001.tex").write_text("", encoding="utf-8")
    (tmp_path / "exercices" / "EX-001-CDP.tex").write_text("", encoding="utf-8")

    files = collect(tmp_path, "complet")

    assert [f.name for f in files] == ["10_C1.tex", "EX-001.tex", "EX-001-CDP.tex"]


def test_ouverture_depuis_contrat_uses_capacites_et_temps(tmp_path):
    (tmp_path / "contrat.yaml").write_text(
        """titre: Chapitre test
capacites:
  - { code: C1, libelle_eleve: Je sais raisonner }
  - { code: C2, libelle_eleve: Je sais vérifier }
situation_accroche: Une situation concrète.
temps_estime_h: { parcours1: 8, parcours2: 6, parcours3: 5 }
""",
        encoding="utf-8",
    )

    ouverture = ouverture_depuis_contrat(tmp_path)

    assert "\\ouverturechapitre{Chapitre test}" in ouverture
    assert "\\textbf{C1} — Je sais raisonner" in ouverture
    assert "Une situation concrète." in ouverture
    assert "\\parcoursUn~8 h" in ouverture
