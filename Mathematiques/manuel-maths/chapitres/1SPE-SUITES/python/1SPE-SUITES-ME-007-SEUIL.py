u = 1500
n = 0
while u < 3000:
    u = 1.04 * u
    n = n + 1
print("Rang :", n)
print("Capital :", round(u, 2))
