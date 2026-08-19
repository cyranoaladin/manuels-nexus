# STATUT CANONIQUE — 1NSI-ALGO-DICHO-GLOUTON-KNN (ADGK)

Correction formelle de la classification du rapport A4 précédent, qui
qualifiait ADGK de « chapitre legacy coexistant avec une réécriture
divergente ». **Cette interprétation était FAUSSE** ; l'arbitrage humain est
confirmé par l'autorité canonique du dépôt.

```
DO_NOT_ARCHIVE_ADGK = TRUE
DO_NOT_DELETE_ADGK  = TRUE
DO_NOT_MERGE_ADGK_INTO_APT = TRUE
```

## Comparaison canonique

| élément | 1NSI-ALGO-PARCOURS-TRIS (APT) | 1NSI-ALGO-DICHO-GLOUTON-KNN (ADGK) |
| --- | --- | --- |
| titre contractuel | « Algorithmique 1 : parcours et tris » | « Algorithmique 2 : dichotomie, algorithmes gloutons, k plus proches voisins » |
| capacités (refs programme NSI 2019) | C1..C6 → P-ALGO-01A/01B/02A/02C/02B/02D | C1..C3 → P-ALGO-04 / P-ALGO-05 / P-ALGO-03 |
| relation de prérequis | — | `prerequis R1 = « Parcours séquentiel, tableaux triés », chapitre_origine: 1NSI-ALGO-PARCOURS-TRIS` |
| assemblage actuel | MANUEL_1NSI (élève+professeur) | MANUEL_1NSI (élève+professeur) |
| reviews | receipts scellés (runs 2026-08-10-algorithms.yaml, par source_sha256) | idem (mêmes runs, scope: object, chapters ADGK+APT) |

Les deux jeux de capacités sont DISJOINTS (P-ALGO-01/02 vs P-ALGO-03/04/05) ;
ADGK référence APT comme origine de son prérequis : ce sont **deux chapitres
canoniques actifs successifs** (Algorithmique 1 puis 2). La ressemblance des
squelettes d'exercices (constatée sur EX-006) est une parenté de gabarit de
génération, pas une duplication de chapitre. La migration documentée
`ID_MIGRATION_1NSI_ADGK_TO_APT` concernait le renommage des objets du
chapitre APT (préfixés ADGK par erreur à l'origine), pas une absorption
d'ADGK.

## Re-clusterisation des 41 références cassées du chapitre (aucun UNKNOWN)

| cluster | count | cas | classification | action |
| --- | --- | --- | --- | --- |
| capacites `1NSI-ADGK-C{1..3}` | 19 | objets EX-006..EX-024 | **object metadata issue (old internal IDs)** : IDs de capacité scopés par le SLUG d'objet (`1NSI-ADGK-`) au lieu du code contrat / de l'ID scopé chapitre ; les codes (C1..C3) existent tous au contrat et les champs `capacites_codes` jumeaux portent déjà la forme canonique | réécriture META mécanique vers la forme scopée chapitre canonique (dry-run, garde anti-corruption ; les receipts d'objet touchés deviennent légitimement stale) |
| `capacites_codes` R2 | 1 | 1NSI-ADGK-RE-C02 | **contract issue** : fiche de remise à niveau R2 réelle, prérequis non déclaré au contrat (schéma: chapitre_origine FACULTATIF) | flux §3 : ajouter `prerequis R2 {code, libelle exact de la fiche}` ; origine seulement si démontrée |
| methodes M2 | 10 | EX-010..EX-019 | **real missing metadata target** : M2 ↔ C2 (P-ALGO-05, gloutons) à produire | production de fiche (lot méthodes, autorité NSI 2019) |
| methodes M3 | 5 | EX-020..EX-024 | **real missing metadata target** : M3 ↔ C3 (P-ALGO-03, k-NN)… voir note mapping | production de fiche |
| methodes M5 | 6 | EX-009/014/015/016/018/019 | **wrong reference (old internal IDs)** : l'architecture C↔M du chapitre (3 capacités) rend M5 impossible ; M5 apparaît en 2ᵉ méthode sur des exercices de capacités différentes (débris de gabarit) | correction META : retrait des entrées M5 (documenté par fichier dans le dry-run) |

## Défaut de contenu supplémentaire découvert (à traiter au lot méthodes)

`1NSI-ADGK-ME-001` (statut `approved`, alias M1) s'intitule **« Dériver une
fonction composée »** : contenu MATHÉMATIQUES contaminé (gabarit) dans un
chapitre NSI d'algorithmique. La fiche M1 devra être RÉÉCRITE pour la
capacité C1 (P-ALGO-04) sous l'autorité NSI 2019, avec invalidation de
review ; les fiches M2 et M3 sont à produire. Un dossier est scellé avant
tout remplacement (contenu actuel préservé dans l'historique Git).

Objectif : ADGK broken_meta = 0 SANS suppression ni archivage du chapitre.
