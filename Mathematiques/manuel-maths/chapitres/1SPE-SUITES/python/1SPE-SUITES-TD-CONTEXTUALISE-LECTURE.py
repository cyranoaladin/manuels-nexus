q = 0.9879
M = 100
n = 0
while M > 50:
    M = q * M
    n = n + 1
print("Demi-vie :", n, "siecles")
print("Masse :", round(M, 2), "g")
