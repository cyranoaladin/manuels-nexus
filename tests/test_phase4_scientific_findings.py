"""Les defauts scientifiques trouves dans les contenus de la phase 4.

Chacun est ici sous la forme qui l'empeche de revenir : non pas « le fichier a
ete corrige », mais « la formulation fautive est interdite, et la formulation
juste est exigee ». Un test qui se contenterait de constater la correction
laisserait la porte ouverte a sa reintroduction par une reecriture ulterieure.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPITRES = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
DISPERSION = CHAPITRES / "TCOMPL-INEGALITES" / "cours" / "10_C0_dispersion.tex"
PRODUIT_SCALAIRE = (
    CHAPITRES / "TSPE-GEOMETRIE-ESPACE" / "cours" / "12_C7_produit_scalaire.tex"
)
GALTON = CHAPITRES / "TSPE-PROBABILITES" / "cours" / "17_ALG_planche_de_galton.tex"
COS_SIN = CHAPITRES / "1SPE-TRIGONOMETRIE" / "cours" / "11_C2_cosinus_sinus.tex"


def _texte(chemin: Path) -> str:
    return chemin.read_text(encoding="utf-8")


def test_le_rapport_interdecile_compare_des_seuils_et_non_des_masses():
    """D9/D1 = 4 ne dit pas que les 10 % du haut recoivent quatre fois ce que
    recoivent les 10 % du bas.

    Sur la serie du cours, le rapport des seuils vaut 3,6 et celui des masses
    6,35 : confondre les deux fait dire au manuel quelque chose de faux sur
    une inegalite de revenus.
    """
    texte = _texte(DISPERSION)
    interdits = (
        r"les\s+\$10\\,\\%\$\s+les mieux dotés reçoivent",
        r"perçoivent\s+environ\s+\$3\{,\}6\$\s+fois\s*\n?\s*ce que perçoivent",
        r"reçoivent au moins quatre fois ce que reçoivent",
    )
    for motif in interdits:
        assert re.search(motif, texte) is None, motif
    assert "seuil du neuvième décile" in texte
    assert "valeurs seuils" in texte
    # Le contre-exemple chiffre doit rester : c'est lui qui interdit la lecture
    # en masses.
    assert "127" in texte and "6{,}35" in texte


def test_la_courbe_de_lorenz_ne_porte_pas_les_quantiles_en_abscisse():
    """Elle porte une proportion cumulee de population, et en ordonnee une
    proportion cumulee de la masse. D1 = 11 ne figure sur aucun des deux axes.
    """
    texte = _texte(DISPERSION)
    aplati = texte.replace("\n", " ")
    assert "Les quantiles sont exactement ce que la courbe de Lorenz" not in aplati
    # La seule mention autorisee est la negation explicite.
    for occurrence in re.finditer(r"quantiles en abscisse", aplati):
        debut = max(0, occurrence.start() - 60)
        assert "ne porte pas" in aplati[debut:occurrence.start()], aplati[debut:occurrence.end()]
    assert "proportion\ncumulée de population" in texte or (
        "proportion cumulée de population" in texte.replace("\n", " ")
    )
    assert "proportion cumulée du revenu" in texte.replace("\n", " ")
    assert "ne figure sur aucun des deux axes" in texte.replace("\n", " ")


def test_aucun_exemple_ne_demande_de_montrer_ce_qu_il_refute():
    """« Montrer que ABC est rectangle en A » suivi de « il ne l'est pas ».

    Une consigne et sa reponse ne peuvent pas se contredire dans un exemple
    corrige : l'eleve n'a alors aucun moyen de savoir laquelle croire.
    """
    texte = _texte(PRODUIT_SCALAIRE)
    assert "Montrer que le triangle $ABC$ est rectangle" not in texte
    assert "Determiner si le triangle $ABC$ est\nrectangle en $A$" in texte
    assert "pas} rectangle en $A$" in texte


def test_la_formule_angulaire_exige_deux_vecteurs_non_nuls():
    """La definition algebrique vaut pour le vecteur nul ; le cosinus, non."""
    texte = _texte(PRODUIT_SCALAIRE)
    aplati = texte.replace("\n", " ")
    assert "non nuls" in aplati
    assert "orthogonal a tout vecteur" in aplati or "orthogonal a $\\vec{v}$" in aplati
    assert "l'angle d'un vecteur nul" in aplati.lower()
    # Le cas nul doit etre verifie, pas seulement mentionne.
    assert "zero = (0, 0, 0)" in texte


def test_le_nombre_de_cases_centrales_depend_de_la_parite():
    """Pour n impair il y a deux cases centrales, pas une."""
    texte = _texte(GALTON)
    aplati = texte.replace("\n", " ")
    assert "Si $n$ est \\textbf{pair}" in aplati
    assert "Si $n$ est \\textbf{impair}" in aplati
    assert "deux" in aplati
    # Les deux cas sont verifies numeriquement.
    assert "modes(10) == [5]" in texte
    assert "modes(9) == [4, 5]" in texte


def test_une_demonstration_exigible_n_est_pas_rangee_sous_pour_aller_plus_loin():
    """`\\approfondissement` affiche « Pour aller plus loin ».

    Une obligation du programme presentee sous cette signaletique se lit comme
    une extension facultative. La demonstration des valeurs remarquables est
    exigible : elle doit etre dans le corps du cours.
    """
    texte = _texte(COS_SIN)
    assert "\\approfondissement{" not in texte
    assert "\\demonstration{" in texte
    assert "exigible" in texte


@pytest.mark.parametrize(
    "chemin",
    [
        CHAPITRES / "1SPE-TRIGONOMETRIE" / "cours" / "11_C2_cosinus_sinus.tex",
        CHAPITRES / "TCOMPL-INEGALITES" / "cours" / "10_C0_dispersion.tex",
        CHAPITRES / "TSPE-GEOMETRIE-ESPACE" / "cours" / "12_C7_produit_scalaire.tex",
        CHAPITRES / "TSPE-PROBABILITES" / "cours" / "17_ALG_planche_de_galton.tex",
        CHAPITRES / "TSPE-PROBABILITES" / "cours" / "18_ALG_marche_aleatoire.tex",
        CHAPITRES / "1SPE-EXPONENTIELLE" / "exercices" / "1SPE-EXPO-EX-051.tex",
        CHAPITRES / "1SPE-EXPONENTIELLE" / "corriges" / "1SPE-EXPO-CO-051.tex",
        CHAPITRES / "1SPE-SUITES" / "exercices" / "1SPE-SUITES-EX-052.tex",
        CHAPITRES / "1SPE-SUITES" / "corriges" / "1SPE-SUITES-CO-052.tex",
        CHAPITRES / "1SPE-VARIABLES-ALEATOIRES" / "exercices" / "1SPE-VARALEA-EX-055.tex",
        CHAPITRES / "1SPE-VARIABLES-ALEATOIRES" / "corriges" / "1SPE-VARALEA-CO-055.tex",
    ],
    ids=lambda p: p.name,
)
def test_chaque_contenu_de_phase_4_porte_une_verification_executable(chemin):
    """Un contenu ecrit sans oracle n'est verifie par personne."""
    texte = _texte(chemin)
    assert "% BEGIN-VERIFY" in texte, chemin.name
    assert "% END-VERIFY" in texte, chemin.name
    assert texte.count("% BEGIN-VERIFY") == texte.count("% END-VERIFY")
