def fusionner(table1, table2, cle):
    """Fusionne table1 et table2 sur les valeurs communes de `cle`.

    Preconditions : `cle` est presente dans les deux tables et les autres
    colonnes sont disjointes.
    """
    colonnes1 = {nom for ligne in table1 for nom in ligne if nom != cle}
    colonnes2 = {nom for ligne in table2 for nom in ligne if nom != cle}
    if not colonnes1.isdisjoint(colonnes2):
        raise ValueError("les colonnes hors cle doivent etre disjointes")
    index2 = {ligne[cle]: ligne for ligne in table2}
    fusion = []
    for ligne1 in table1:
        if ligne1[cle] in index2:
            complement = {
                k: v for k, v in index2[ligne1[cle]].items() if k != cle
            }
            fusion.append({**ligne1, **complement})
    return fusion


adherents = [
    {"nom": "Ali", "age": 16},
    {"nom": "Sami", "age": 15},
    {"nom": "Yasmine", "age": 22},
]
presences = [
    {"nom": "Ali", "seances": 12},
    {"nom": "Sami", "seances": 9},
    {"nom": "Yasmine", "seances": 15},
]
resultat = fusionner(adherents, presences, "nom")
print(resultat)
