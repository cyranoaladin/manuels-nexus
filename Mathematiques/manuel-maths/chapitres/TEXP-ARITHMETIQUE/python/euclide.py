def euclide(a, b):
    """PGCD de deux entiers non tous deux nuls."""
    if a == 0 and b == 0:
        raise ValueError("Les deux entiers ne peuvent pas etre nuls.")
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a
