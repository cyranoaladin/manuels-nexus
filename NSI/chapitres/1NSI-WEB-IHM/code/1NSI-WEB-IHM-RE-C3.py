compteur = {"valeur": 0}

def incrementer():
    compteur["valeur"] = compteur["valeur"] + 1
    return compteur["valeur"]

ajouter_gestionnaire("bouton", incrementer())
