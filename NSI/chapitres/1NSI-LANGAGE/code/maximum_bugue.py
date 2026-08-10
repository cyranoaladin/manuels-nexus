def maximum_bugue(liste):
    maxi = 0
    for x in liste:
        if x > maxi:
            maxi = x
    return maxi

print(maximum_bugue([3, 7, 2]))
