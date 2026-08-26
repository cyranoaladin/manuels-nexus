# Affichage de M_n pour n = 0, 10, 20, ..., 100
q = 0.9879
for n in range(0, 101, 10):
    M_n = 100 * q**n
    print(f"n = {n} siecles : M_n = {round(M_n, 2)} g")
