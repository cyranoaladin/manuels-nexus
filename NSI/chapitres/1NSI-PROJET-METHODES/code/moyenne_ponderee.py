def moyenne_ponderee(valeurs, poids):
    """Renvoie la moyenne ponderee pour des poids valides."""
    assert len(valeurs) == len(poids), "valeurs et poids doivent avoir la meme longueur"
    assert all(poids_i >= 0 for poids_i in poids), "les poids doivent etre non negatifs"
    assert sum(poids) > 0, "la somme des poids doit etre strictement positive"
    total = 0
    for i in range(len(valeurs)):
        total += valeurs[i] * poids[i]
    return total / sum(poids)
