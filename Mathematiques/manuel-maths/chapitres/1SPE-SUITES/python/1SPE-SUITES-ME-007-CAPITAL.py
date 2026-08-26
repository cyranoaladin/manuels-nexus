def capital(n):
    u = 1500
    for k in range(n):
        u = 1.04 * u
    return u


print(round(capital(10), 2))
