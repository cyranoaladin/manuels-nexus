def minimum(liste):
    """Renvoie le plus petit element.

    Precondition : liste est non vide.
    """
    assert len(liste) > 0
    mini = liste[0]
    for x in liste[1:]:
        if x < mini:
            mini = x
    return mini
