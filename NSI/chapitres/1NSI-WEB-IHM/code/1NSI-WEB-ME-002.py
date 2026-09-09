panier = {"articles": 0}

def ajouter_article():
    panier["articles"] = panier["articles"] + 1
    return panier["articles"]

ajouter_gestionnaire("bouton_ajouter", ajouter_article)
