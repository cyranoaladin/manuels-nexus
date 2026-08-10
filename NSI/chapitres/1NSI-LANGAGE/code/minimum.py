def minimum(liste):
    """Renvoie le plus petit element.

    Precondition : liste est non vide.
    """
    assert len(liste) > 0, "liste doit etre non vide"
    mini = liste[0]
    for x in liste[1:]:
        if x < mini:
            mini = x
    return mini
