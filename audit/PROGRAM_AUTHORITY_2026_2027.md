# MATRICE D'AUTORITÉ PROGRAMMES — ÉDITION 2026-2027

Arbitrage humain appliqué (2026-08-19). Version machine :
`audit/PROGRAM_AUTHORITY_2026_2027.json` (16 chapitres concernés par les
méthodes manquantes, avec le jeu de capacités contractuel de chacun).
Aucune méthode n'est rédigée avant la validation mécanique de cette matrice.

## Règles d'autorité par manuel

| manuel | autorité programme | BO / date | note d'application |
| --- | --- | --- | --- |
| 1SPE | Programme de spécialité mathématiques de Première 2026 | BO n°14 du 2 avril 2026 | NOUVEAU programme, applicable à la rentrée 2026-2027 → autorité de l'édition. Référentiel machine local `referentiel/capacites_1SPE_*.json`. |
| TSPE / TCOMPL | Programmes de Terminale ACTUELLEMENT applicables (2019) | BO spécial n°8 du 25 juillet 2019 | NE PAS utiliser prématurément les programmes Terminale 2026 : ils n'entrent en application qu'à la rentrée 2027-2028. |
| TEXPERTES | Programme mathématiques expertes 2019 | BO spécial n°8 du 25 juillet 2019 | Applicable à l'édition 2026-2027, sauf texte officiel ultérieur explicitement applicable. |
| 1NSI / TNSI | Programmes NSI Première/Terminale 2019 | BO spécial n°1 du 22 janvier 2019 | Actuellement en vigueur. |

## Chapitres à méthodes manquantes (16)

| manuel | chapitre | capacités contractuelles | alignement |
| --- | --- | --- | --- |
| 1NSI | 1NSI-ALGO-DICHO-GLOUTON-KNN | C1..C3 (P-ALGO-03/04/05) | contrat validé sous NSI 2019 (chapitre canonique actif — voir A4_ADGK_CANONICAL_STATUS) |
| 1SPE | 1SPE-TRIGONOMETRIE | C1..C5 (référentiel BO 2026) | contrat = référentiel 2026, vérifié par test |
| TCOMPL | CALCULS-AIRES · CORRELATION-CAUSALITE · ECHANTILLONNAGE · INEGALITES · INFERENCE-BAYESIENNE · LOGARITHME-HISTORIQUE · MODELES-EVOLUTION · MODELES-FONCTION · TEMPS-ATTENTE | selon contrat (4-6 capacités) | contrats validés sous programme 2019 ; le contrat est l'autorité de capacités |
| TEXPERTES | ARITHMETIQUE · COMPLEXES-ALGEBRE-GEOMETRIE · COMPLEXES-TRIGO-POLYNOMES · GRAPHES · MATRICES-MARKOV | selon contrat | idem |

Règle de production : chaque fiche M_i traite exactement la capacité C_i du
contrat de SON chapitre, dans les limites du programme d'autorité ci-dessus ;
tout contenu hors programme est interdit (R7).
