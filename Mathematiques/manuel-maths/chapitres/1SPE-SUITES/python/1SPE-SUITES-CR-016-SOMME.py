# Calcul de la somme u_0 + u_1 + ... + u_n
# Exemple : suite geometrique u_k = 2 * 3**k
def somme(u0, q, n):
    u = u0
    S = u0
    for k in range(n):
        u = q * u
        S = S + u
    return S


print(somme(2, 3, 4))
