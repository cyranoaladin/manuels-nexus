def moyenne(notes):
    """Renvoie la moyenne des notes.
    Precondition : notes est une liste non vide de nombres.
    Postcondition : le resultat est compris entre min(notes) et max(notes).
    """
    return sum(notes) / len(notes)
