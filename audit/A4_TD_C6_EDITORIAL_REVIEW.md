# A4 — REVUE ÉDITORIALE DES 14 RÉFÉRENCES C6 DES TD (DOSSIER SCELLÉ)

Une ligne par référence dans `audit/A4_TD_C6_EDITORIAL_REVIEW.json`
(14 lignes, UNKNOWN = 0). Synthèse et décision.

## Constat prouvé

Les 7 chapitres concernés (TCOMPL-CORRELATION-CAUSALITE, INEGALITES,
INFERENCE-BAYESIENNE, LOGARITHME-HISTORIQUE, MODELES-EVOLUTION,
TEXP-COMPLEXES-ALGEBRE-GEOMETRIE, TEXP-GRAPHES) portent TOUS les DEUX MÊMES
TD : « Optimisation d'une boîte de conserve » (07_td_contextualise) et
« Étude complète de f(x)=x²e⁻ˣ » (07_td_fil_rouge), déclarant `C6` alors que
leurs contrats s'arrêtent à C5.

Vérification programmatique : les corps des 14 fichiers sont
**byte-identiques (aux IDs d'objets près) aux TD originaux de
`TCOMPL-MODELES-FONCTION`** — le chapitre d'étude de fonctions, où ce contenu
(dérivation, optimisation, convexité, intégrale) est à sa place et où `C6`
existe au contrat. Aucun des 14 clones n'exerce la moindre compétence du
chapitre hôte (rien sur Bayes, Lorenz/Gini, graphes, complexes, suites,
logarithme historique).

## Classification : CONTAMINATED_TEMPLATE_CONTENT — 14/14

- WRONG_TAG_UNAMBIGUOUS : 0 (aucune capacité hôte candidate — le contenu
  entier est hors thème, pas seulement l'étiquette C6)
- CONTRACT_STALE : 0 (ajouter un C6 « étude de fonctions » aux contrats de
  Bayes/graphes/etc. serait une falsification du programme)
- contenu unique perdu : 0 (clones prouvés ; l'original canonique vit dans
  TCOMPL-MODELES-FONCTION ; l'historique Git préserve les octets)

## Décision (cas NON ambigu)

**Archivage de doublon** : suppression des 14 clones. Conséquences assumées
et VISIBLES :

- la case « Temps 7 » (TD) de ces 7 chapitres redevient une dette de contenu
  honnête (à produire par chapitre, conformément au gabarit), au lieu d'être
  masquée par un contenu hors-sujet publié dans les manuels ;
- les manuels TCOMPL et TEXPERTES sont reconstruits (élève + professeur)
  après suppression ;
- aucun `C6` n'est modifié ni « corrigé » ; aucun contrat n'est altéré.

Cas restant réellement éditorial pour arbitrage humain sur C6 : **AUCUN**.
La production des TD conformes par chapitre rejoint la dette de contenu
générale (même famille que les fiches méthodes manquantes).
