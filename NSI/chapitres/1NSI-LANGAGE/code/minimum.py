def minimum(liste):
    """Renvoie le plus petit element.

    Precondition : liste est non vide.
    """
    if len(liste) == 0:
        raise ValueError("liste doit etre non vide")
    mini = liste[0]
    for x in liste[1:]:
        if x < mini:
            mini = x
    return mini
