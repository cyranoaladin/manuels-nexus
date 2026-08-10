def distance(p1, p2):
    """Distance euclidienne entre deux points (x, y)."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def k_plus_proches_voisins(points_classes, nouveau_point, k):
    """Predit la classe de `nouveau_point` a partir de ses k plus proches voisins.

    `points_classes` : liste de triplets (x, y, classe) deja etiquetes.
    Precondition : k est un entier et 1 <= k <= len(points_classes).
    """
    if type(k) is not int or not 1 <= k <= len(points_classes):
        raise ValueError(
            "k doit etre un entier compris entre 1 et le nombre de points"
        )
    distances = [
        (distance((x, y), nouveau_point), classe)
        for (x, y, classe) in points_classes
    ]
    distances.sort(key=lambda d: d[0])
    k_plus_proches = distances[:k]
    classes = [c for (_, c) in k_plus_proches]
    return max(set(classes), key=classes.count)


points = [
    (1, 1, "A"), (2, 1, "A"), (1, 2, "A"),
    (8, 8, "B"), (9, 8, "B"), (8, 9, "B"),
]
print(k_plus_proches_voisins(points, (1.5, 1.5), 3))
print(k_plus_proches_voisins(points, (8.5, 8.5), 3))
