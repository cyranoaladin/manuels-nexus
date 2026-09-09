def moyenne(valeurs):
    if len(valeurs) == 0:
        raise ValueError("la liste ne doit pas etre vide")
    return sum(valeurs) / len(valeurs)
