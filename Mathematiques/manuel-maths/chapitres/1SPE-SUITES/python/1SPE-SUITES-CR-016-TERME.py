# Calcul du n-ieme terme d'une suite definie par recurrence
# Exemple : u_0 = 3, u_{n+1} = 2*u_n + 1
def terme(u0, n):
    u = u0
    for k in range(n):
        u = 2 * u + 1
    return u


print(terme(3, 5))
