COMMANDES = {"AUTO": None, "ON": True, "OFF": False}
etat = {"chauffage": False, "override_manuel": None}


def traiter_evenement(commande):
    commande = commande.strip().upper()
    if commande not in COMMANDES:
        raise ValueError("commande attendue : AUTO, ON ou OFF")
    etat["override_manuel"] = COMMANDES[commande]


def decider_chauffage(temperature, seuil=18):
    if etat["override_manuel"] is not None:
        return etat["override_manuel"]
    return temperature < seuil


def actionner_chauffage(temperature, seuil=18):
    etat["chauffage"] = decider_chauffage(temperature, seuil)
    return etat["chauffage"]


def afficher_etat(temperature):
    override = etat["override_manuel"]
    if override is None:
        mode = "AUTO"
    elif override:
        mode = "ON manuel"
    else:
        mode = "OFF manuel"
    chauffage = "ON" if etat["chauffage"] else "OFF"
    return f"temperature={temperature} C | mode={mode} | chauffage={chauffage}"


def interface_thermostat(commande, temperature, seuil=18):
    traiter_evenement(commande)
    actionner_chauffage(temperature, seuil)
    return afficher_etat(temperature)


def lancer_ihm(temperature, seuil=18, lire=input, ecrire=print):
    ecrire("Commandes : AUTO | ON | OFF")
    commande = lire("Commande : ")
    ecrire(interface_thermostat(commande, temperature, seuil))
