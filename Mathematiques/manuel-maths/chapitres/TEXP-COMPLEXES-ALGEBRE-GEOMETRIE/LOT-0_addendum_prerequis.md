# Addendum LOT 0 — Correction P0 des prérequis attribués à la Première

Date : 2026-08-11. Branche : `production/collection-v2`.

## Défaut

Quatre contrats de Terminale déclaraient comme acquis de Première des contenus
qui ne figurent dans aucun programme de Première (2019 ni 2026) :

| Chapitre | Prérequis fautif | Origine déclarée |
|---|---|---|
| `TEXP-COMPLEXES-ALGEBRE-GEOMETRIE` | « Nombres complexes : forme algébrique, opérations de base » | `1SPE` |
| `TEXP-ARITHMETIQUE` | « Récursivité, algorithmique » | `1SPE` |
| `TEXP-GRAPHES` | « Structures de données de base » | `1SPE` |
| `TCOMPL-CALCULS-AIRES` | « Dérivation, primitives usuelles » | `1SPE-DERIVATION-GLOBAL` |

Le contrat des complexes aggravait le défaut en annonçant à l'élève, dans sa
`situation_accroche`, un chapitre qui « reprend et approfondit l'étude
algébrique des nombres complexes vue en première ». Un élève de maths expertes
aurait cherché en vain, dans son manuel de première, un chapitre inexistant.

Le cas de `TCOMPL-CALCULS-AIRES` était doublement faux : les primitives ne sont
pas au programme de Première **et** sont introduites par ce chapitre lui-même
(capacités C4 et C5).

## Preuve

Recherche textuelle dans les BO de Première déposés et empreintés
(`sources/txt/BO2019_1SPE_specialite.txt`, `sources/txt/BO2026_1SPE_specialite.txt`) :

- « nombres complexes » : 0 occurrence dans les deux textes ;
- « récursivité » / « récursif » : 0 occurrence ;
- « structures de données » : 0 occurrence ;
- « primitive » : 0 occurrence.

La seule occurrence du mot « complexe » dans le BO 2026 est
« découper une tâche complexe en tâches plus simples », dans la section
Algorithmique et programmation — sans rapport avec les nombres complexes.

Ces notions relèvent respectivement du programme optionnel de mathématiques
expertes (nombres complexes, matrices et graphes), de la spécialité NSI
(récursivité, structures de données) et de la Terminale (primitives).

## Correction

Prérequis remplacés par des acquis réellement disponibles, chacun rattaché à un
chapitre existant de la collection :

- complexes ← second degré (discriminant négatif), calcul algébrique, géométrie
  repérée, trigonométrie ;
- arithmétique ← algorithmique et programmation Python (thème transversal
  effectivement présent au programme de Première, BO 2019 l.19 et l.695),
  raisonnement par récurrence (TSPE-SUITES-LIMITES) ;
- graphes ← calcul matriciel (TEXP-MATRICES-MARKOV, chapitre du même manuel),
  algorithmique Python ;
- calculs d'aires ← dérivation seule.

L'accroche des complexes est réécrite : elle part du discriminant négatif vu en
première, constat que l'élève possède réellement, et annonce l'ensemble des
nombres complexes comme entièrement nouveau.

## Test de régression

`tests/test_prerequis_conformite.py` — 50 cas, 2 assertions par contrat de
Terminale. Le verdict n'est pas codé en dur : le test recherche chaque notion
surveillée dans les textes officiels de Première déposés. Un prérequis attribué
à la Première dont la notion est absente des deux BO échoue.

C'est ce test qui a révélé le quatrième défaut (`TCOMPL-CALCULS-AIRES`), non
détecté lors de l'audit manuel.

## Point laissé ouvert

`referentiel/capacites_1SPE_SUITES.json` et
`referentiel/capacites_1SPE_SECOND_DEGRE.json` portent encore une
`bo_reference` vers le BO spécial n°1 du 22 janvier 2019, alors que les huit
autres référentiels de Première citent le programme 2026 et que
`referentiel/CONFORMITE_BO2026.md` déclare ces deux chapitres conformes au BO
2026. Non corrigé ici : `CLAUDE.md` §7 interdit de modifier `referentiel/*.json`
sans instruction explicite.
