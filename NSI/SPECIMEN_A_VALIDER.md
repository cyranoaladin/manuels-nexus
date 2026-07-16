# SPÉCIMEN À VALIDER — Charte Nexus v3.2

Statut : **validation conjointe requise**. Le spécimen est compilé en 10 pages et les PNG 150 dpi sont disponibles dans `build/specimen/png/`.

| Défaut v3.1 | Correctif v3.2 | Preuve PNG |
|---|---|---|
| Titres d'encadrés blancs et petites capitales inopérantes | `\nxboxtitle` applique la couleur explicite et des capitales réelles aux huit boîtes | `page-03.png` |
| Contraste des huit styles non contrôlable d'un regard | Page-témoin vide : définition, théorème, propriété, erreur, méthode, ★, carte et mini-projet | `page-03.png` |
| Page bleue sans identité ni motif | Numéro Thin, grille mémoire 6×4, cinq cases or, flèches, filet, titre et signature | `page-01.png` |
| Contrat sans objectifs illustrés | `\icnObjectif` devant chaque capacité et carte au style gris foncé | `page-02.png` |
| Signature intérieure et onglet absents | Mini-losange d'en-tête et onglet de tranche sur les pages impaires | `page-03.png`, `page-08.png` |
| Exemple D1 divergent du listing | Station `("Tunis-Carthage", 36.8, 10.2)` identique dans les deux | `page-04.png` |
| Q2 présentée en code inline | Petit bloc Python ; diagnostic visuellement séparé | `page-06.png` |
| Étiquette de courbe/tangente non normalisée | Courbe étiquetée en fin à droite, tangente sous sa droite, point de contact seul | `page-07.png` |
| Marges et pied de page à préserver | Identifiant/durée en marge, pagination et signature de pied | `page-08.png` |
| Accents et ASCII code régressables | Page de contrôle + gates dédiés `check_accents_contenu.py` et `check_ascii_code.py` | `page-09.png` |

Vérifications techniques du 16 juillet 2026 : spécimen 10 pages, pilote 34 pages, aucun `Overfull`, 214 tests Python verts et `make lot-gates` vert.

Décision attendue : validation visuelle et pédagogique conjointe avant toute industrialisation de la charte.
