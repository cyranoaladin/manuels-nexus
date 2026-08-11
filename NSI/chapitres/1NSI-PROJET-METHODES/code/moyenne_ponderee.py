def moyenne_ponderee(valeurs, poids):
    """Renvoie la moyenne ponderee pour des poids valides."""
    if len(valeurs) != len(poids):
        raise ValueError("valeurs et poids doivent avoir la meme longueur")
    if not all(poids_i >= 0 for poids_i in poids):
        raise ValueError("les poids doivent etre non negatifs")
    somme_poids = sum(poids)
    if somme_poids <= 0:
        raise ValueError("la somme des poids doit etre strictement positive")
    total = 0
    for i in range(len(valeurs)):
        total += valeurs[i] * poids[i]
    return total / somme_poids
