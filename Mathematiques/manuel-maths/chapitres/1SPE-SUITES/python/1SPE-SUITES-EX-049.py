u = 100
v = 100

for n in range(1, 21):
    u = 1.05 * u
    v = v + 0.05 * v * (1 - v / 500)
    if n in [5, 10, 20]:
        print(f"n={n} : u={u:.1f}, v={v:.1f}")
