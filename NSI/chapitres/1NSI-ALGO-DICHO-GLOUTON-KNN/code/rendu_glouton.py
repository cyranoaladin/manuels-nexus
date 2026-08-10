def rendu_glouton(montant, pieces):
    """Construit un rendu en choisissant d'abord les plus grandes pieces disponibles.

    Precondition : les valeurs des pieces sont strictement positives.
    """
    if not all(p > 0 for p in pieces):
        raise ValueError("les pieces doivent etre strictement positives")
    pieces_triees = sorted(pieces, reverse=True)
    rendu = []
    for p in pieces_triees:
        while montant >= p:
            rendu.append(p)
            montant -= p
    if montant != 0:
        raise ValueError("l'algorithme glouton n'a pas trouve de rendu exact")
    return rendu


print(rendu_glouton(78, [50, 20, 10, 5, 2, 1]))
