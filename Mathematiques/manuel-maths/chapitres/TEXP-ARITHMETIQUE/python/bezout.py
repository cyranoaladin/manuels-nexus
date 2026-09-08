def bezout(a, b):
    """Renvoie (d, u, v) avec d = PGCD(a, b) = a*u + b*v."""
    if a == 0 and b == 0:
        raise ValueError("Les deux entiers ne peuvent pas etre nuls.")
    if b == 0:
        signe = 1 if a > 0 else -1
        return abs(a), signe, 0
    d, u, v = bezout(b, a % b)
    return d, v, u - (a // b) * v
