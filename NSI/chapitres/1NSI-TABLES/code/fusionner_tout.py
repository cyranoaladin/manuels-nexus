def fusionner_tout(table1, table2, cle, defauts):
    index2 = {}
    for ligne2 in table2:
        index2.setdefault(ligne2[cle], []).append(ligne2)

    fusion = []
    for ligne1 in table1:
        correspondances = index2.get(ligne1[cle], [defauts])
        for ligne2 in correspondances:
            complement = {k: v for k, v in ligne2.items() if k != cle}
            colonnes1 = set(ligne1) - {cle}
            colonnes2 = set(complement)
            if not colonnes1.isdisjoint(colonnes2):
                raise ValueError("les colonnes hors cle doivent etre disjointes")
            fusion.append({**ligne1, **complement})
    return fusion
