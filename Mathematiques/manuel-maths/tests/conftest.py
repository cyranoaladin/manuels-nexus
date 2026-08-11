"""Rend la racine du depot importable depuis la suite de tests du manuel.

Deux modules de tests importent `scripts.build_manifest`, qui vit dans le
`scripts/` de la racine du depot et non dans celui du manuel. Lances depuis
`Mathematiques/manuel-maths`, ils echouaient a la collecte avec
`ModuleNotFoundError: No module named 'scripts.build_manifest'`, ce qui
interrompait toute la suite : `make test` ne rapportait alors aucun resultat.

On insere donc la racine du depot en tete de `sys.path`. Le paquet `scripts`
resolu reste celui de la racine, qui expose aussi bien `build_manifest` que les
autres modules d'inventaire ; les scripts propres au manuel sont importes par
les tests via un chemin explicite.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE_MANUEL = Path(__file__).resolve().parents[1]
RACINE_DEPOT = RACINE_MANUEL.parents[1]

for chemin in (RACINE_DEPOT, RACINE_MANUEL):
    if str(chemin) not in sys.path:
        sys.path.insert(0, str(chemin))
