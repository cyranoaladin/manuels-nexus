def decomposition(n):
    """Decompose un entier n >= 1 ; 1 correspond au produit vide."""
    if n < 1:
        raise ValueError("L'entier doit etre superieur ou egal a 1.")
    facteurs, p = {}, 2
    while p * p <= n:
        while n % p == 0:
            facteurs[p] = facteurs.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        facteurs[n] = facteurs.get(n, 0) + 1
    return facteurs
