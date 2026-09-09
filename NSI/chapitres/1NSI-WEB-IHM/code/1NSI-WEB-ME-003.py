avant = client_envoie_requete_avec_cookies("/accueil")
serveur_definit_cookie("panier", "2 articles")
apres = client_envoie_requete_avec_cookies("/paiement")
