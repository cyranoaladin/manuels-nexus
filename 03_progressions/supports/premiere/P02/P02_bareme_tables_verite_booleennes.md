---
title: "P02 - barème - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "bareme"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation machine"
notion: "expression booléenne, table de vérité, opérateurs logiques"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-04"
---

# P02 - Barème - Tables de vérité booléennes

## Objectifs

- Vérifier la capacité à construire une table de vérité pour une expression booléenne à 2 ou 3 variables.
- Évaluer la maîtrise des opérateurs logiques (ET, OU, NON, XOR).
- Contrôler la compréhension des notions de tautologie et contradiction.

## Capacités officielles

- P-DATA-BASE-04 : Écrire la table de vérité associée à une expression booléenne.

## Prérequis

- Connaître les opérateurs logiques de base : ET (AND), OU (OR), NON (NOT).
- Savoir lister toutes les combinaisons de valeurs pour n variables booléennes.
- Comprendre la notion de simplification d'expression booléenne.

## Situation-problème

Un concepteur de circuits logiques doit vérifier qu'une porte combinatoire produit les sorties attendues. Il construit la table de vérité de l'expression booléenne associée, identifie les lignes pertinentes et simplifie l'expression si possible. Le barème guide l'évaluation de cette compétence.

## Activité d’entrée

Écrire la table de vérité de l'expression A ET (NON B) pour deux variables A et B, puis vérifier le résultat en testant chaque combinaison à la main.

## Exemple

Expression : (A OU B) ET (NON A OU B). Table à 4 lignes, résultat : la sortie vaut 1 uniquement quand B = 1. Simplification : l'expression est équivalente à B.

## Barème question par question

### Barème question 1 — Table de vérité à 2 variables (P-DATA-BASE-04) — 5 points
- 1.a) Variables et lignes : 1 point (2 variables identifiées, 4 lignes listées dans l'ordre canonique 00, 01, 10, 11).
- 1.b) Calcul de la table : 3 points (1 pt par colonne intermédiaire correcte, 1 pt colonne résultat sans erreur, 1 pt présentation claire avec en-têtes).
- 1.c) Simplification : 1 point (expression simplifiée correcte avec justification par lecture de la table).

### Barème question 2 — Table de vérité à 3 variables (P-DATA-BASE-04) — 6 points
- 2.a) Nombre de lignes : 1 point (8 lignes identifiées pour 3 variables, toutes combinaisons présentes).
- 2.b) Calcul de la table : 4 points (1 pt colonnes intermédiaires correctes, 1 pt par sous-expression évaluée sans erreur, 1 pt colonne finale correcte, 1 pt aucune ligne manquante).
- 2.c) Contrôle par substitution : 1 point (au moins une ligne vérifiée en substituant les valeurs dans l'expression originale).

### Barème question 3 — XOR et propriétés (P-DATA-BASE-04) — 4 points
- 3.a) Table du XOR : 2 points (1 pt définition correcte A XOR B = (A ET NON B) OU (NON A ET B), 1 pt table à 4 lignes sans erreur).
- 3.b) Comparaison XOR / OU exclusif : 1 point (explication que XOR vaut 1 si et seulement si les entrées diffèrent).
- 3.c) Tautologie ou contradiction : 1 point (identification correcte : A XOR NON A est une tautologie, A XOR A est une contradiction, avec justification par la table).

### Barème question 4 — Synthèse et lois de De Morgan (P-DATA-BASE-04) — 5 points
- 4.a) Application de De Morgan : 2 points (1 pt formule NON(A ET B) = NON A OU NON B correcte, 1 pt vérification par la table de vérité).
- 4.b) Simplification d'une expression : 2 points (1 pt expression simplifiée correcte, 1 pt justification par équivalence des tables).
- 4.c) Cas limite expression constante : 1 point (table d'une expression sans variable — toujours vraie ou toujours fausse — identifiée comme tautologie ou contradiction).

## Total : 20 points

## Critères de réussite observables
- Toutes les combinaisons de variables sont listées sans omission.
- Les colonnes intermédiaires sont présentes et permettent de suivre le raisonnement.
- Au moins une vérification par substitution est effectuée.

## Erreurs fréquentes
- Oublier une ou plusieurs lignes dans la table (notamment pour 3 variables).
- Confondre OU inclusif et OU exclusif (XOR).
- Ne pas évaluer les sous-expressions dans le bon ordre de priorité.
- Écrire une simplification sans la justifier par la table.

## Exercices

Les exercices évalués sont les questions 1 à 3 de l'évaluation tables de vérité booléennes P02.

## Corrigé

Les réponses détaillées se trouvent dans P02_corrige_tables_verite_booleennes.md.

## Remédiation

En cas de score inférieur à 8/15, reprendre la construction d'une table à 2 variables avec un seul opérateur avant de passer aux expressions composées.

## Différenciation

- Socle : question 1 (table à 2 variables avec opérateurs simples).
- Standard : question 2 (table à 3 variables avec sous-expressions).
- Expert : question 3c (identification de tautologie et contradiction).

## Séance(s) correspondante(s)

Séance dédiée aux expressions booléennes et tables de vérité.
