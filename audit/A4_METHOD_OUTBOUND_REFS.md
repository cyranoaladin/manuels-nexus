# A4 — Renvois sortants des fiches méthodes (§9 clôture)

Contrôle : chaque fiche produite porte `\sEntrainer{\refExos{M#}}` (Math) ou
« S'entraîner : exercices C# » (NSI). La validité est SÉMANTIQUE : il doit
exister au moins un exercice du chapitre étiqueté `methodes: [M#]`
(le rendu v5 imprime le libellé littéral — `nxv@training@` n'est peuplé par
aucun producteur — donc aucune erreur LaTeX n'est possible ; le lien est porté
par les META, utilisées par l'inventaire et la couverture).

## Résultat

| Population | Valide | Invalide |
|---|---|---|
| 85 fiches de campagne (après retags) | 85 | 0 |
| 4 fiches de clôture | 2 (AIR M6, ECH M6) | 2 (TRIGO M3, M5) — voir ci-dessous |

Contrôles par fiche : cible = exercice existant, même manuel, même chapitre,
même capacité primaire, aucune cible archive/prototype (les retags ne visent
que des `exercices/*.tex` actifs du chapitre courant).

## Retags effectués (13, journal complet dans le commit de clôture)

Deux classes, discipline §4-TD-C6 :
- **Non ambigus (7)** : exercice à capacité primaire C_k et `methodes: []` →
  `methodes: [M_k]` (MF EX-004, ATT EX-004, ARI EX-004, CTP EX-004,
  MAT EX-006, ECH EX-004 ; + AIR — voir append).
- **Compléments par règle de capacité primaire (6)** : `M_k` AJOUTÉ (jamais
  retiré) sur un exercice parcours-1 de capacité primaire C_k
  (MF EX-007, ARI EX-006/007/009, CTP EX-007, MAT EX-007, AIR EX-006).

## Résiduel explicite (2) — pas d'UNKNOWN

`1SPE-TRIGONOMETRIE` M3 et M5 : le chapitre ne possède AUCUN exercice couvrant
C3 ou C5 (mesuré : exercices primaires C1=12, C2=11, C4=1, C3=0, C5=0).
Le renvoi est donc sémantiquement vide tant que la couverture
capacités×parcours du chapitre n'est pas produite — dette ÉDITORIALE
préexistante du chapitre (1SPE est NO-GO publication par ailleurs), à traiter
dans le lot exercices, PAS par la clôture (production d'exercices hors
mandat). Rendu imprimé inchangé (libellé littéral).

## Dette éditoriale documentée (non touchée)

66 exercices à capacité primaire C6+ portent des tags méthodes hérités M1-M5
(artefact de génération, même famille que le mis-tag TRIGO). Ces tags
RÉSOLVENT (les fiches M1-M5 existent) mais leur pertinence éditoriale est
suspecte ; ils relèvent d'une revue éditoriale par cas, hors mandat de
clôture. Aucun tag existant n'a été supprimé.
