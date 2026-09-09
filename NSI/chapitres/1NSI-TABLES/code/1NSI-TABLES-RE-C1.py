plus_age = max(ligne["age"] for ligne in eleves)
majeurs = [ligne["nom"] for ligne in eleves if ligne["age"] >= "18"]
