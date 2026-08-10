def copier_grille_deux_niveaux(grille):
    """Copie la liste externe et chaque ligne.

    Precondition : les cellules sont des valeurs scalaires atomiques non mutables,
    sans conteneur imbrique.
    """
    return [list(ligne) for ligne in grille]
