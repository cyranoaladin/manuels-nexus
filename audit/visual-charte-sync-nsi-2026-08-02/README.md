# Revue visuelle — synchronisation de la charte NSI

Statut : **PREUVES PRODUITES — VALIDATION HUMAINE EN ATTENTE**.

Cette revue compare le rendu NSI au commit `e20adcd05105832504041fb2f9aa0e116e5bbdee`
avec le rendu obtenu après synchronisation exacte de :

- `NSI/gabarits/nexus-manuel.cls` ;
- `NSI/gabarits/nexus-signatures.tex`.

Les fichiers synchronisés ont respectivement les mêmes SHA-256 que leurs
sources Mathématiques :

- `nexus-manuel.cls` :
  `4f1d30e460f48ee94414000ac543465430c2b042728f1c7c4624ae23cec23097` ;
- `nexus-signatures.tex` :
  `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74`.

## Planches avant/après

- [Specimen, pages 1 et 3](specimen-avant-apres.png) : ouverture, grille,
  titre, marge et onglet ;
- [Chapitre complet, pages 1, 29 et 36](chapitre-avant-apres.png) : page
  dense, reflow avancé et fin de chapitre.

Chaque ligne présente l'ancien rendu à gauche et le nouveau à droite.

## Résultats techniques

| Contrôle | Avant | Après | Verdict technique |
|---|---:|---:|---|
| Specimen | 9 pages A4 | 9 pages A4 | stable |
| Chapitre `1NSI-TYPES-CONSTRUITS` | 36 pages A4 | 36 pages A4 | stable |
| Erreurs TeX / overfull | 0 | 0 | stable |
| Polices incorporées | toutes | toutes | stable |
| Glyphes `◆` manquants, chapitre | 3 | 3 | dette antérieure, non aggravée |
| Gate de synchronisation | rouge, 2 fichiers | vert, 7/7 | corrigé |

Le raster change sur les 9 pages du specimen et les 36 pages du chapitre.
Le changement n'est donc pas une variation d'environnement ni une simple
correction d'onglet : le profil partagé modifie aussi les marges, la densité,
les titres et le reflow. Le nombre de pages et l'intégrité PDF restent stables.

L'inspection des pages représentatives n'a trouvé ni chevauchement, ni texte
coupé, ni débordement. Elle montre toutefois une ouverture plus compacte et une
redistribution matérielle du contenu, notamment entre les pages 29 et 36. Cette
évolution ne peut pas être auto-approuvée par l'agent.

## Portée de la décision

Aucune image de baseline existante n'a été modifiée. Le manifeste porte
`baseline_updated=false`, `human_visual_decision=pending` et
`release_acceptance=false`.

Une approbation humaine future pourrait valider ce rendu comme changement
attendu pour NSI. Elle ne vaudrait ni validation scientifique, ni validation
éditoriale globale, ni autorisation de publication.

## Outils

- LuaHBTeX 1.17.0, TeX Live 2023/Debian ;
- Poppler 24.02.0 ;
- ImageMagick 6.9.12-98 Q16 ;
- specimen rasterisé à 150 ppp ;
- chapitre rasterisé à 100 ppp.

La consultation indépendante Chutes n'a pas pu être exécutée : HTTP 402,
quota du compte dépassé. Aucun avis externe n'a été utilisé.
