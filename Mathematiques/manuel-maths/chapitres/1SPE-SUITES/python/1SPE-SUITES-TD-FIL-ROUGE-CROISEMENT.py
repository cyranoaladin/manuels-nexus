# Recherche du premier mois n (a partir du rang 10) tel que B_n
# depasse A_n
# A_n = 200*n  (offre A : suite arithmetique)
# B_n = 1000 * 1.004**n  (offre B : suite geometrique)
n = 10
A = 200 * n
B = 1000 * 1.004**n
while B <= A:
    n = n + 1
    A = 200 * n
    B = 1000 * 1.004**n
print("Premier mois de depassement apres le rang 10 : n =", n)
print("A_n =", A, "euros")
print("B_n =", round(B, 2), "euros")
