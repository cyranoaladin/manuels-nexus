# Recherche du premier n tel que M_n <= 50
q = 0.9879
M = 100.0
n = 0
while M > 50:
    M = q * M
    n = n + 1
print("Demi-vie :", n, "siecles, soit", n * 100, "ans")
print("Masse atteinte :", round(M, 2), "g")
