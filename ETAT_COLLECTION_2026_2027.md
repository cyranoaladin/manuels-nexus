# ÉTAT DE LA COLLECTION — édition 2026-2027

Généré le 2026-08-11 par `scripts/collection_dashboard.py`.
Aucun chiffre de ce document n'est saisi à la main : tout est recalculé
depuis l'arbre par `scripts/chapter_readiness.py`.

## Vue d'ensemble

- Chapitres : **51**, dont **0** prêts pour release
- Manuels prêts pour release : **0 / 6**
- Capacités rattachées : **312 / 312** (0 non rattachées)
- Objets encore au statut `generated` : **2472 / 2782**

## Par manuel

| Manuel | Programme | Chapitres | READY | EN COURS | SQUELETTE | BLOQUÉ | Capacités | Exercices | `generated` | Prêt |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Mathématiques Première spécialité | 2026 | 10 | 0 | 10 | 0 | 0 | 50/50 | 473/312 | 1383/1391 | 92.0% |
| NSI Première spécialité | 2019 | 10 | 0 | 1 | 9 | 0 | 53/53 | 100/320 | 0/302 | 51.3% |
| Mathématiques Terminale spécialité | 2019 | 11 | 0 | 4 | 7 | 0 | 67/67 | 255/376 | 757/757 | 58.8% |
| NSI Terminale spécialité | 2019 | 6 | 0 | 0 | 6 | 0 | 59/59 | 23/266 | 103/103 | 27.8% |
| Mathématiques complémentaires Terminale | 2019 | 9 | 0 | 0 | 9 | 0 | 50/50 | 36/300 | 141/141 | 46.7% |
| Mathématiques expertes Terminale | 2019 | 5 | 0 | 0 | 5 | 0 | 33/33 | 24/194 | 88/88 | 46.7% |

## Lecture

Un chapitre n'est `READY` que si les quinze critères de
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
