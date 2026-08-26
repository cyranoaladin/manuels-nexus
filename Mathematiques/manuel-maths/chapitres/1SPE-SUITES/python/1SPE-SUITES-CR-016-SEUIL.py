# Recherche du plus petit n tel que u_n > seuil
# Exemple : u_0 = 1, u_{n+1} = 1.05 * u_n, seuil = 2
def recherche_seuil(u0, q, seuil):
    u = u0
    n = 0
    while u <= seuil:
        u = q * u
        n = n + 1
    return n, u


n, val = recherche_seuil(1, 1.05, 2)
print(f"n = {n}, u_n = {val:.4f}")
