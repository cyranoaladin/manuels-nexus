from math import isqrt


def crible(n):
    """Liste les nombres premiers <= n, pour un entier n."""
    if n < 2:
        return []
    prem = [True] * (n + 1)
    prem[0] = prem[1] = False
    for p in range(2, isqrt(n) + 1):
        if prem[p]:
            for m in range(p * p, n + 1, p):
                prem[m] = False
    return [p for p in range(2, n + 1) if prem[p]]
