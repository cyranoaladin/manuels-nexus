assert est_majeur(30) is True    # cas ordinaire
assert est_majeur(5) is False    # cas ordinaire
assert est_majeur(18) is True    # seuil exact
assert est_majeur(17) is False   # juste sous le seuil
