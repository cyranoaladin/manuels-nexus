# Mapping sequences du corpus ↔ chapitres du manuel

Document de reference, construit depuis les contrats reels (`contracts/*.yml`) et les
progressions (`03_progressions/progression_*.md`). Toute decision divergente est documentee.

## Premiere (10 chapitres ← 15 sequences P00-P14)

| Chapitre | Sequences sources | Justification |
|---|---|---|
| 1NSI-TYPES-BASE | P01, P02, P03 | P01=entiers, P02=representation machine/booleens, P03=texte/approximation |
| 1NSI-TYPES-CONSTRUITS | P04 | P04=tuples/listes/dictionnaires (P-DATA-CONSTR-02A) |
| 1NSI-TABLES | P05, P06 | P05=traitement tables CSV, P06=recherche/tri/fusion tables |
| 1NSI-LANGAGE | P00, P07 | P00=methode/rentree (P-LANG-01), P07=fonctions/tests/specifications (P-LANG-01..05) |
| 1NSI-WEB-IHM | P08 | P08=HTML/CSS/DOM/HTTP/formulaires (P-IHM-01..04) |
| 1NSI-ARCHITECTURE-OS | P09 | P09=architecture/systeme/droits Unix (P-ARCH-01/03) |
| 1NSI-RESEAUX | P10 | P10=reseaux/protocoles/paquets (P-ARCH-02/04) |
| 1NSI-ALGO-PARCOURS-TRIS | P11, P12 | P11=parcours/recherche/extremum (P-ALGO-01), P12=tris/invariants/complexite (P-ALGO-02) |
| 1NSI-ALGO-DICHO-GLOUTON-KNN | P13 | P13=dichotomie/glouton/k-NN (P-ALGO-03/04/05) |
| 1NSI-PROJET-METHODES | P14 | P14=synthese/projet/oral (P-HIST-01) |

## Terminale (12 chapitres + blocs transversaux ← 20 sequences T00-T19)

| Chapitre | Sequences sources | Justification |
|---|---|---|
| TNSI-STRUCTURES-LINEAIRES | T01, T03 | T01=structures abstraites (T-STRUCT-01A), T03=listes/piles/files/tables (T-STRUCT-03A) |
| TNSI-POO | T02, T14 | T02=POO (T-STRUCT-02A), T14=modularite/API/paradigmes (T-LANG-03..05) |
| TNSI-RECURSIVITE | T04 | T04=langage/preuve de terminaison (T-LANG-02A). Note : inclut la recursivite au sens large |
| TNSI-ARBRES | T05, T06 | T05=arbres binaires (T-STRUCT-04A), T06=ABR (T-ALGO-01E/F) |
| TNSI-GRAPHES | T07, T08 | T07=graphes representations (T-STRUCT-05), T08=BFS/DFS/cycles/chemins (T-ALGO-02) |
| TNSI-BDD-SQL | T09, T10 | T09=modele relationnel/cles/contraintes (T-BDD-01/02), T10=SQL (T-BDD-03) |
| TNSI-PROCESSUS-SOC | T11 | T11=SoC/processus/ordonnancement/interblocage (T-ARCH-01/02) |
| TNSI-RESEAUX-SECURITE | T12, T13 | T12=routage RIP/OSPF (T-ARCH-03), T13=chiffrement/HTTPS (T-ARCH-04) |
| TNSI-CALCULABILITE-PARADIGMES | T15, T14 | T15=calculabilite/arret (T-LANG-01), T14 pour les paradigmes (T-LANG-04/05) |
| TNSI-DIVISER-REGNER | T16 | T16=diviser pour regner/tri fusion (T-ALGO-03) |
| TNSI-PROG-DYNAMIQUE-TEXTE | T17, T18 | T17=programmation dynamique (T-ALGO-04), T18=Boyer-Moore (T-ALGO-05) |
| TNSI-PREPA-ECE-ECRIT-GO | T19, T00 | T19=bac pratique/ecrit/Grand Oral (T-HIST-01), T00=reprise Python (T-LANG-03A, diagnostic entree) |

## Decisions et notes

- **T14 partage entre POO et CALCULABILITE** : T14 couvre modularite (paradigmes → CALCULABILITE) ET API (→ POO).
  Les capacites T-LANG-03 vont avec POO, T-LANG-04/05 avec CALCULABILITE. La repartition se fait a
  la curation (LOT 2), pas a la recolte.
- **T00 dans PREPA** : T00 est un diagnostic d'entree annuel ; il alimente le bilan d'entree du manuel Terminale.
- **P00 dans LANGAGE** : P00 (methode NSI) est transversal mais partage P-LANG-01 avec P07 ; il est traite
  comme complement d'introduction au chapitre LANGAGE.
