# A4 — CLÔTURE (PARTIELLE) ET PAQUET D'ARBITRAGE ÉDITORIAL

Burndown des `broken_meta_references` par cause racine, et périmètre restant
qui NE PEUT PAS être résolu de façon autonome sans violer R2/R7 (contenu
pédagogique vérifié, aucune invention réglementaire) ni le protocole
(« ne jamais supprimer du contenu pour faire disparaître le signal »).

## Burndown par sous-lot

| étape | cluster | Δ | broken_meta après | commit |
| --- | --- | --- | --- | --- |
| départ (PRE-A4, mesuré frais) | — | — | 2730 | 9c832d63 |
| A4.1 resolver namespace CAPACITY_ID scopé chapitre | CAP-SCOPED-ID | −1478 | 1252 | 2a09cabf |
| A4.2 dérivation d'alias METH-0n | MET-LEGACY-SUFFIX | −452 (+2 ambiguïtés révélées) | 802 | 74ea4d53 |
| A4.3 suppression des 7 doublons de méthode prouvés + rebuilds | MET-LEGACY-DUP | −242 | 560 | b0891498 |
| A4.7a complétion du contrat TRIGO depuis le référentiel BO | TRIGO C3-C5 | −18 | 542 | d9cbe5f7 |

Réductions par nature : analyzer 1478 · schema 452 · legacy IDs 242 ·
contrat stale (référentiel) 18. Total résolu : 2188 (80,1 %).
`fail-on-new` = PASS avec 0 nouvelle anomalie après CHAQUE sous-lot.

## RESTE : 542 — arbitrage éditorial requis (aucun UNKNOWN)

### 1. MET-PHANTOM — 476 références `methodes[*]` vers des méthodes jamais créées

Le gabarit pédagogique (docs/01, Temps 5) prescrit « **une fiche méthode par
capacité** (numérotation M1, M2… alignée sur C1, C2…) ». Les chapitres
TCOMPL/TEXP/NSI n'ont qu'UNE méthode alors que leurs contrats déclarent 4 à
16 capacités : les références M2..M6 des exercices sont donc CONFORMES au
gabarit, et ce sont **les fiches méthodes qui manquent**
(CONTENT_TRULY_MISSING, ≈ 90-100 fiches sur ~20 chapitres). Les produire
exige une rédaction pédagogique avec revue humaine (workflow LOT-3) ; les
références ne doivent PAS être supprimées (falsification du système de
renvois). Décision attendue : programme de production des fiches, ou
révision éditoriale du gabarit/du périmètre de références.

### 2. Codes R{n} — 33 références `capacites_codes` de remédiation

Les fiches de remise à niveau R3-R5 existent AVEC contenu réel (ex.
TCOMPL-CALCULS-AIRES-FR-R3 « Fonction exponentielle : propriétés et
dérivée ») mais les contrats ne déclarent que R1-R2 en `prerequis`.
Compléter les contrats exige `chapitre_origine` (non dérivable sans
invention — R7). Décision attendue : compléter les prerequis des contrats
(libellés verbatim des fiches, origines à valider), ou reclasser ces fiches.

### 3. C6 des TD — 14 références `capacites[*]`

Les TD `07_td_contextualise/07_td_fil_rouge` déclarent `C6` dans des
chapitres à 5 capacités, avec des signes de contamination de gabarit (ex.
TEXP-GRAPHES porte un TD « Optimisation d'une boîte de conserve »). Revue
éditoriale du contenu des TD requise avant toute correction de référence.

### 4. Chapitre legacy ADGK — 19 `capacites` + 1 `capacites_codes` (R2)

`1NSI-ALGO-DICHO-GLOUTON-KNN` coexiste avec sa réécriture divergente
`1NSI-ALGO-PARCOURS-TRIS` (durées/capacités différentes) et LES DEUX sont
assemblés dans MANUEL_1NSI ; ses objets portent des reviews scellées par
`source_sha256`. La disposition du chapitre (suppression/archivage/fusion)
est un arbitrage éditorial qui résoudra ces 20 références ; toute
modification préalable invaliderait les receipts.

## Constats connexes scellés

- Rebuilds §11 : TSPE_2026_2027 élève+professeur reconstruits PASS (PDF
  suivis rafraîchis, masters régénérés sans METH-01). **1NSI : rebuild
  tenté et BLOQUÉ par un défaut préexistant de l'assembleur NSI**
  (résolution de `nexus-charte.sty` en staging, échec au chargement de la
  classe avant tout contenu — indépendant d'A4 ; la gouvernance liste déjà
  `1NSI:build_observé_absent`). À traiter comme défaut d'infrastructure
  d'assemblage NSI.
- Les métriques de ce document utilisent la taxonomie de
  `audit/ANOMALY_METRIC_SEMANTICS.md`.
