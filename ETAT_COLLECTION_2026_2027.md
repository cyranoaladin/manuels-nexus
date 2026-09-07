# ÉTAT DE LA COLLECTION — édition 2026-2027

> **NON AUTORITAIRE — DIAGNOSTIC HISTORIQUE.** Le verdict de release
> appartient exclusivement à `audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`.

Généré de façon déterministe par `scripts/collection_dashboard.py`.
Aucun chiffre de ce document n'est saisi à la main : tout est recalculé
depuis l'arbre par `scripts/chapter_readiness.py`.

## Vue d'ensemble

- Chapitres : **52**, dont **0** satisfont l'ancienne checklist
- Manuels satisfaisant l'ancienne checklist : **0 / 6**
- Capacités rattachées : **319 / 322** (3 non rattachées)
- Objets encore au statut `generated` : **1841 / 4059**

## Par manuel

| Manuel | Programme | Chapitres | READY | EN COURS | SQUELETTE | BLOQUÉ | Capacités | Exercices | `generated` | Prêt |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Mathématiques Première spécialité | 2026 | 10 | 0 | 10 | 0 | 0 | 52/55 | 484/342 | 1413/1446 | 76.7% |
| NSI Première spécialité | 2019 | 10 | 0 | 1 | 9 | 0 | 53/53 | 101/320 | 20/360 | 55.3% |
| Mathématiques Terminale spécialité | 2019 | 11 | 0 | 5 | 6 | 0 | 67/67 | 277/376 | 56/839 | 63.0% |
| NSI Terminale spécialité | 2019 | 7 | 0 | 0 | 7 | 0 | 61/61 | 23/290 | 109/122 | 44.8% |
| Mathématiques complémentaires Terminale | 2019 | 9 | 0 | 9 | 0 | 0 | 53/53 | 306/318 | 150/792 | 62.2% |
| Mathématiques expertes Terminale | 2019 | 5 | 0 | 5 | 0 | 0 | 33/33 | 194/194 | 93/500 | 66.7% |

## Lecture

Le libellé `READY` ci-dessus appartient uniquement à l'ancienne
checklist. Il ne constitue jamais un verdict de publication. Les
quinze critères historiques de
`chapter_readiness.py` sont réunis, dont l'absence totale d'objet au
statut `generated`. Un objet `generated` n'a franchi aucune revue :
le pipeline de statuts interdit qu'il paraisse dans une release.

La colonne Exercices compare l'effectif au seuil capacitaire
`min(50, max(24, 6 × C))`, où C est le nombre de capacités du chapitre.
Ce seuil est un plancher de couverture, pas l'indicateur principal :
les KPI qui décident d'une release sont la couverture des capacités,
la couverture de revue scientifique, la traçabilité programme, la
couverture d'évaluation et de remédiation, et l'état des builds.

Détail par chapitre : `audit/CHAPTER_READINESS.json`.
