# Recherche du plus petit n tel que u_n > seuil
# Exemple : u_0 = 1, u_{n+1} = 1.05 * u_n, seuil = 2
from math import isfinite


def seuil_geometrique(u0, q, seuil):
    """Renvoie le plus petit rang avec u_n > seuil, pour u0 > 0 et q > 1."""
    try:
        parametres_finis = isfinite(u0) and isfinite(q) and isfinite(seuil)
    except (TypeError, ValueError, OverflowError):
        parametres_finis = False
    if not parametres_finis:
        raise ValueError("Les paramètres doivent être des nombres réels finis.")
    if u0 <= 0:
        raise ValueError("u0 doit être strictement positif.")
    if q <= 1:
        raise ValueError("q doit être strictement supérieur à 1.")

    u = u0
    n = 0
    while u <= seuil:
        u_suivant = q * u
        if u_suivant <= u:
            raise ValueError("La précision numérique empêche la suite de progresser.")
        u = u_suivant
        n = n + 1
    return n, u


n, val = seuil_geometrique(1, 1.05, 2)
print(f"n = {n}, u_n = {val:.4f}")
