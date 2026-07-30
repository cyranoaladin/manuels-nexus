# Décision humaine requise — baseline visuelle maquette V5

Statut : **NO-GO mise à jour des hashes sans approbation page par page**.

## Résultat

Les cinq tests rouges ont une cause commune : l'oracle codé correspond au rendu
du commit `60d0460`, antérieur aux onglets adaptatifs introduits par `f071d37`.
Les PNG suivis depuis `63c497e` et une nouvelle rastérisation du PDF courant
concordent octet pour octet. Les changements sont confinés à l'onglet latéral ;
aucun hash n'a été modifié.

Tests concernés :

1. `test_checker_cli_synthetic_exit_codes` ;
2. `test_validation_png_reference_hashes` ;
3. `test_non_diagnostics_page_hashes_reject_a_changed_page` ;
4. `test_page13_diagnostics_layout_pdf` ;
5. `test_maquette_v5_acceptance`.

Le quatrième test ne révèle pas une divergence de la page 13 : il atteint
ensuite le contrôle fail-fast de la page 1. La page 13 courante correspond à son
oracle corrigé.

## Décision page par page

| Page | Ancien hash | Nouveau hash | Pixels | Pourcentage | Bbox `(x0,y0,x1,y1)` | Verdict proposé | Décision humaine |
|---:|---|---|---:|---:|---|---|---|
| 1 | `1e065c44…24d` | `a3a5ea8b…fd2` | 1 711 | 0,078605 % | `(1169,157,1240,257)` | `expected_change` | à décider |
| 7 | `b3499d26…233` | `0f091b2b…280` | 1 078 | 0,049524 % | `(1169,161,1240,249)` | `expected_change` | à décider |
| 8 | `7dc9d309…64ac` | `13ff6daa…70f` | 1 141 | 0,052418 % | `(0,161,71,249)` | `expected_change` | à décider |
| 9 | `fbe900ad…726e` | `ccda0af7…35c3` | 1 229 | 0,056461 % | `(1169,160,1240,251)` | `expected_change` | à décider |
| 10 | `50aec577…7be` | `4466330d…52d1` | 1 268 | 0,058253 % | `(0,161,71,251)` | `expected_change` | à décider |
| 11 | `91f971e7…984d` | `7f114a2b…f130` | 4 334 | 0,199107 % | `(1169,148,1240,293)` | `expected_change` | à décider |
| 12 | `eeb87208…093` | `3517dc00…f44f` | 4 367 | 0,200624 % | `(0,148,71,293)` | `expected_change` | à décider |
| 15 | `988b636d…91b4` | `11de1dad…191` | 740 | 0,033996 % | `(1169,163,1240,245)` | `expected_change` | à décider |

Les hashes complets et les images sont dans
`audit/visual-baseline-review/manifest.json`.

## Contrôles complémentaires

| Contrôle | Observation |
|---|---|
| Chevauchement | aucun changement hors bande de l'onglet ; aucun chevauchement nouveau observé |
| Texte coupé | aucune zone de texte métier dans les bbox de diff |
| Notes marginales | aucune modification détectée hors onglet |
| Onglets | longueur/position adaptées au libellé ; cause de toutes les différences |
| En-têtes et pieds de page | identiques pixel à pixel hors bande latérale |
| Couche texte | présente sur les huit pages, de 139 à 851 mots extraits par page |
| Recto-verso | alternance gauche/droite cohérente avec les pages paires et impaires |
| Polices | toutes incorporées selon `pdffonts` |
| PDF courant | A4, 15 pages, non chiffré ; `Tagged: no` reste une dette d'accessibilité |

Outils : ImageMagick `6.9.12-98 Q16`, Poppler `24.02.0`, LuaHBTeX
`1.17.0`, Pillow `12.3.0`, rastérisation 150 dpi en `1241 × 1754`.

## Décision demandée

Pour chaque page, choisir :

- `expected_change` : autoriser ensuite une commande explicite de mise à jour ;
- `regression` : corriger la source et conserver l'ancien hash ;
- `environment_drift` : reproduire dans l'environnement de référence ;
- `undetermined` : demander une revue visuelle complémentaire.

Cette décision ne vaut ni validation mathématique, ni validation de release.
