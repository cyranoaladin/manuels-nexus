C = 120000
t = 0.005
m = 800
n = 0

while C > 0:
    C = (1 + t) * C - m
    n = n + 1

print(n)
