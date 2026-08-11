jalons = [
    {"nom": "Cahier des charges", "termine": True},
    {"nom": "Prototype minimal", "termine": True},
    {"nom": "Fonctionnalites completes", "termine": False},
    {"nom": "Tests et correction de bugs", "termine": False},
    {"nom": "Presentation finale", "termine": False},
]


def avancement(jalons):
    """Renvoie le pourcentage de jalons termines.

    Precondition : la liste contient au moins un jalon.
    """
    if len(jalons) == 0:
        raise ValueError("au moins un jalon est requis")
    nb_termines = sum(1 for j in jalons if j["termine"])
    return nb_termines / len(jalons) * 100


def prochain_jalon(jalons):
    """Renvoie le nom du premier jalon non termine, ou None si tout est fini."""
    for j in jalons:
        if not j["termine"]:
            return j["nom"]
    return None


print(avancement(jalons))
print(prochain_jalon(jalons))
