"""Régressions scientifiques du chapitre 1SPE Variables aléatoires."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COURSE = (
    ROOT
    / "chapitres/1SPE-VARIABLES-ALEATOIRES/cours/11_C2_esperance_variance.tex"
)
FR_R2 = (
    ROOT
    / "chapitres/1SPE-VARIABLES-ALEATOIRES/remediation/1SPE-VARALEA-FR-R2.tex"
)


def test_ecart_type_n_est_pas_decrit_comme_un_ecart_moyen() -> None:
    text = COURSE.read_text(encoding="utf-8")
    assert "mesure l'écart moyen" not in text
    assert "racine carrée de la moyenne des carrés des écarts" in text


def test_formule_probabilites_totales_est_isolee_pour_rester_lisible() -> None:
    text = FR_R2.read_text(encoding="utf-8")
    assert "partition de $\\Omega$ :\n\\[" in text
    assert "\\sum_{i=1}^{n} P(A|B_i) P(B_i)\n\\]" in text
