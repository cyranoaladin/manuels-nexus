def premier_depassement(valeur_initiale, taux, seuil):
    valeur = valeur_initiale
    n = 0
    while valeur <= seuil:
        valeur = valeur * (1 + taux)
        n = n + 1
    return n, valeur


n, v = premier_depassement(500, 0.08, 2000)
print(f"n={n}, v={v:.2f}")
