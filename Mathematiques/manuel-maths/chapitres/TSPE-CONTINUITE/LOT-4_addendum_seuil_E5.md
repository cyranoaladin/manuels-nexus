# LOT-4 — Addendum : passage du squelette au seuil E5

Date : 2026-08-11. Branche : `production/collection-v2`.

## État avant

Le chapitre comptait **8 exercices** pour 2 capacités, sans aucun coup de
pouce. Il figurait dans l'audit du 11 août parmi les 37 chapitres « squelettes
de programme » de la collection.

## État après

| | Parcours ◆ | Parcours ◆◆ | Parcours ◆◆◆ | Total |
|---|---:|---:|---:|---:|
| **C1** — TVI, existence, unicité, encadrement | 12 | 12 | 6 | 30 |
| **C2** — suites récurrentes `u(n+1) = f(u(n))` | 8 | 8 | 4 | 20 |
| **Total** | 20 | 20 | 10 | **50** |

Ratio 40/40/20 exactement conforme à E5/F01. Toutes les cases capacité ×
parcours comptent au moins 2 exercices. 50 corrigés copie-modèle, 20 coups de
pouce (un par exercice de parcours ◆).

SymPy : **108 objets OK, 0 FAIL**.

## Progression pédagogique retenue

**C1 ◆** — application directe, en variant délibérément les supports pour que
l'élève ne rattache pas le TVI au seul polynôme de degré 3 : degrés 3 et 5,
exponentielle, racine carrée, quotient, produit `x·exp(-x)`, et lecture d'un
tableau de variations à trois branches.

**C1 ◆◆** — format examen. Trois exercices exploitent la différence entre
*existence* et *calcul* : le TVI fournit l'unicité, puis l'équation se résout
exactement (produit en croix, discriminant, factorisation par racine évidente).
Deux portent sur l'algorithmique du programme, dont la comparaison du coût du
balayage et de la dichotomie.

**C1 ◆◆◆** — démonstration : point fixe sur `[0;1]`, discussion paramétrique en
cinq cas, racine réelle des polynômes de degré impair, `exp(x) = 3 - x²` traité
par la dérivée seconde, et la suite `(α_n)` des racines de `x^n + x - 1`.

**C2 ◆** — la méthode complète sur sept fonctions. EX-034 et EX-039 partagent
`sqrt(x+2)` avec deux points de départ opposés : l'une croît vers 2, l'autre
décroît vers 2, ce qui fait émerger la notion de point fixe attractif. EX-038 a
deux points fixes, si bien que l'équation `f(l) = l` ne suffit pas à conclure —
l'exercice l'énonce explicitement : la continuité donne une condition
nécessaire, pas suffisante.

**C2 ◆◆** — contextes (pharmacocinétique, dilution), algorithme de Héron,
convergence lente au point fixe double, suite alternée non monotone, seuil
algorithmique et risque de non-terminaison d'une boucle `while`.

**C2 ◆◆◆** — nombre d'or par les quotients de Fibonacci consécutifs,
convergence quadratique de Héron avec doublement du nombre de décimales
exactes, et théorème du point fixe contractant qui unifie rétrospectivement
tout le chapitre : sa démonstration ne suppose aucune monotonie et couvre donc
aussi bien les suites croissantes que les suites alternées produites plus haut.

## Ce que les gates ont rejeté

Sept défauts, tous détectés par les assertions, aucun laissé passer.

**Défaut P0 antérieur (EX-003 / CO-003).** L'énoncé demandait de montrer
`f'(x) > 0` sur `[-3;-1]` alors que `f'(-1) = 0`. Le bloc VERIFY ne testait
qu'un seul point intérieur, `x = -2`, ce qui rendait le contrôle aveugle au
défaut. Le corrigé masquait l'incohérence en restreignant silencieusement
l'intervalle à `[-3;-1[`. Énoncé recentré sur l'ouvert, corrigé réécrit avec le
théorème reliant signe de la dérivée et stricte croissance sur l'intervalle
fermé, assertions étendues à la borne.

**Cinq valeurs approchées écrites à la main puis rejetées** : racine de
`x^5+x-3` (1,1325963 → 1,1329976), seconde racine du bénéfice
(9,7311895 → 9,7380612), première racine du volume
(1,1401045 → 1,1737862), `P(10)` du modèle logistique
(196,0355 → 196,0373), et la comparaison de vitesse de CO-044 dont l'affirmation
était simplement fausse. Aucune assertion n'a été affaiblie : toutes ont été
recalculées, conformément à la règle VERIFY.

**Erreur d'énoncé EX-045.** L'identité `f(x) - 2 = -2(x-2)/(x+2)` portait un
facteur 2 parasite ; la valeur correcte est `-(x-2)/(x+2)`. Détectée par
l'assertion du corrigé, corrigée dans l'énoncé **et** verrouillée par une
assertion ajoutée à l'énoncé lui-même.

## Deux faux positifs documentés

**CO-026, sous-résolution du flottant.** L'assertion `theta(t) > 20` échouait en
`t = 1000` parce que `60·exp(-100) ≈ 2,2e-42` disparaît devant 20 en double
précision : `float(20 + 2.2e-42)` vaut exactement 20,0. L'énoncé mathématique
est pourtant vrai pour tout `t`. L'assertion n'a pas été supprimée mais
**remplacée par une preuve symbolique** sur un réel positif quelconque
(`(th - 20).is_positive is True`), donc strictement plus forte que la version
échantillonnée en flottants.

**CO-031, indécidabilité de `solveset`.** Sur `x³ - 4x + 1`, `solveset` renvoie
des radicaux dont SymPy ne sait pas décider l'appartenance à ℝ, ce qui fait
échouer toute itération sur le résultat. Remplacé par `Poly.real_roots`, qui
donne les trois mêmes valeurs de façon fiable.

**CO-044, explosion des rationnels.** L'itération exacte de `x²/4 + 1` sur 30
rangs produit des rationnels de taille astronomique et dépassait le délai du
gate. Passage en flottants pour cette comparaison de vitesse uniquement, les
identités algébriques restant vérifiées exactement.

## Reste à faire sur ce chapitre

- LOT 3 : étendre le cours (2 sections aujourd'hui) et porter les fiches
  méthodes de 2 à une par capacité, avec la méthode de contraction issue de
  EX-046 et EX-050.
- LOT 5 : QCM diagnostic à distracteurs reliés aux erreurs documentées, et
  fiches de remédiation par capacité.
- LOT 6 : évaluations A et B avec résolution aveugle.
- LOT 7 : assemblage, compilation PDF, relecture, tag `chap/TSPE-CONTINUITE-v1`.
