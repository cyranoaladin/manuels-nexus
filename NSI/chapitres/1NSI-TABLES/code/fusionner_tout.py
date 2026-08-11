def fusionner_tout(table1, table2, cle, defauts):
    colonnes1 = {
        colonne for ligne in table1 for colonne in ligne if colonne != cle
    }
    colonnes2 = {
        colonne for ligne in table2 for colonne in ligne if colonne != cle
    }
    colonnes2.update(colonne for colonne in defauts if colonne != cle)
    if not colonnes1.isdisjoint(colonnes2):
        raise ValueError("les colonnes hors cle doivent etre disjointes")

    index2 = {}
    for ligne2 in table2:
        index2.setdefault(ligne2[cle], []).append(ligne2)

    fusion = []
    for ligne1 in table1:
        correspondances = index2.get(ligne1[cle], [defauts])
        for ligne2 in correspondances:
            complement = {k: v for k, v in ligne2.items() if k != cle}
            fusion.append({**ligne1, **complement})
    return fusion
