# PREUVE GÉOMÉTRIE ONGLET — CONTRAT 12 MM (HISTORICAL SNAPSHOT)

Preuve de mesure raster 300 dpi de l'onglet de rubrique, avant/après la
correction d'épaisseur. Snapshot historique attaché au commit de correction ;
ne se régénère pas. Autorité contractuelle :
`Mathematiques/manuel-maths/docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md`.

## Méthode

- Maquette V5 réelle (15 pages), producteur `build_maquette_v5.py` puis
  3 passes LuaLaTeX (`-recorder`), rasterisation `pdftoppm -r 300`.
- Mesure des rectangles saturés au bord extérieur (impaire : droite ;
  paire : gauche) et des extents du texte blanc dans la bande.
- Contre-preuve `pdftotext -bbox-layout` sur les mots d'onglet.
- Tolérance de rasterisation documentée : 1 px = 0,0847 mm à 300 dpi
  (les mesures portent ±1 px, soit ±0,09 mm).

## CASE T2 — mesure AVANT correction (bug confirmé)

| grandeur | page impaire | page paire |
| --- | --- | --- |
| outer_thickness_measured_mm (visible) | 10,08 | 9,99 |
| visible_inside_page_mm | 10,08 | 9,99 |
| bleed_outside_page_mm | 1,0 (hors page) | 1,0 |
| total_rectangle_mm | 11,0 | 11,0 |

Contrat : 12 mm → **écart réel ≈ 1 mm : BUG DE CHARTE.** L'analyse statique
(-10 mm → +1 mm) était donc correcte et confirmée par la mesure. Origine du
bug : commit `ab62fb62` (2026-07-31, `[CHARTE][V5.B-it2]`) qui a remplacé la
géométrie historique `rectangle +(-12mm, …)` (12 mm exacts) par
`-10mm → +1mm` (11 mm). La spec validée du 2026-07-20 exigeait « épaisseur
extérieure : 12 mm, inchangée ». Le contrat n'est pas modifié ; la géométrie
est corrigée.

## Correction appliquée

`gabarits/common/nexus-manuel.cls` et `gabarits/common/nexus-charte.sty`
(source canonique unique, wrappers Maths/NSI inchangés, `check_charte_sync`
7/7) :

- impaire : rectangle `xshift=-12mm → +1mm` (12 mm visibles + 1 mm d'arête
  de coupe hors page), filet accent à `-12mm`, texte centré à `-6mm` ;
- paire : miroir `-1mm → +12mm`, filet à `+12mm`, texte à `+6mm`.

## Mesure APRÈS correction (300 dpi)

| grandeur | impaire | paire |
| --- | --- | --- |
| outer_thickness_measured_mm | **12,02** | **12,02** |
| visible_inside_page_mm | 12,02 | 12,02 |
| bleed_outside_page_mm | 1,0 | 1,0 |
| total_rectangle_mm | 13,0 | 13,0 |

(12,11 mesuré sur la page 11 impaire = +1 colonne d'anti-aliasing, dans la
tolérance.)

## Contrat complet onglet (SHORT = COURS, LONG = AUTO-ÉVALUATION)

| contrôle | COURS impaire (p.3) | COURS paire (p.4) | AUTO-ÉVAL impaire (p.11) | AUTO-ÉVAL paire (p.12) |
| --- | --- | --- | --- | --- |
| longueur onglet (mm) | 16,00 | 16,00 | 24,64 | 24,64 |
| min 16 mm | ✔ (= min) | ✔ | ✔ (> 16) | ✔ |
| texte (mm) | 6,86 | 6,94 | 18,46 | 18,46 |
| formule texte+6 | branche min | branche min | 24,46 ≈ 24,64 (±2 px) | 24,46 ≈ 24,64 |
| padding début (mm) | 4,49 | 4,57 | 2,96 | 3,05 |
| padding fin (mm) | 4,66 | 4,49 | 3,22 | 3,13 |
| ≥ 3 mm (branche auto) | n/a (surplus min réparti) | n/a | ✔ (±1 px) | ✔ |
| asymétrie ≤ 0,5 mm | 0,17 ✔ | 0,08 ✔ | 0,25 ✔ | 0,08 ✔ |
| même longueur impaire/paire | ✔ 16,00 == 16,00 | | ✔ 24,64 == 24,64 | |
| texte entièrement contenu | ✔ | ✔ | ✔ | ✔ |
| une seule ligne (no wrap) | ✔ (épaisseur ligne 1,44 mm) | ✔ | ✔ (1,78 mm) | ✔ |
| police 6/6 pt (no shrink) | ✔ statique + formule | ✔ | ✔ | ✔ |

Contre-preuve `pdftotext -bbox-layout` : COURS p.3 x 574,01→582,04 pt
(centre à 6,09 mm du bord = centre de bande) ; AUTO-ÉVALUATION p.11
y 79,37→131,97 pt = 18,56 mm de longueur de texte — concordant avec le raster.

## Effet sur la maquette et les oracles visuels

- Compilation : 3 passes LuaLaTeX propres, 15 pages, renvois 2/2.
- Diff pixel 300 dpi vs état précédent : les changements sont STRICTEMENT
  confinés à la zone onglet (lignes 295-585, bande extérieure) sur les pages
  1-5, 7-12, 15 ; pages 6, 13, 14 byte-identiques.
- Les oracles visuels (`NON_DIAGNOSTICS_PAGE_SHA256`,
  `validations/v5/page-*.png`) n'ont PAS été mis à jour :
  `check_maquette_v5.py` échoue désormais volontairement sur « page 1
  altérée » en attendant la revue humaine des 12 pages modifiées
  (copies 150 dpi produites hors dépôt pour comparaison).
- Sources QCM : intactes (aucun fichier QCM modifié par la correction).
- Provenance runtime `.fls` : la compilation consomme
  `gabarits/common/nexus-charte.sty` et `gabarits/common/nexus-manuel.cls`
  canoniques (preuve runtime : 9 builds analysés, PASS).
- **MAQUETTE V5 : non prononcée validée. D7 : BLOCKED** jusqu'à revue humaine
  des rasters.
