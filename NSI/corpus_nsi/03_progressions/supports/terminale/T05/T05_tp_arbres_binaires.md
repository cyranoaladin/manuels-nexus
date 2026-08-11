---
title: "T05 - Tp - Arbres binaires"
level: "terminale"
sequence_id: "T05"
document_type: "tp"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Arbres et algorithmes"
notion: "arbre binaire, racine, feuille, parcours"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-04A"
---


# T05 - TP - Arbres binaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-04A

## Prérequis
- Reconnaître une consigne liée à arbre binaire.
- Distinguer donnée, méthode et conclusion dans le thème Arbres et algorithmes.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T05-S1 à T05-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une expression arithmétique est représentée par un arbre dont les feuilles sont des valeurs et les nœuds internes des opérateurs.

## Activité d’entrée
1. Repérer racine, fils gauche et fils droit.
2. Calculer la hauteur d’un arbre réduit à une feuille.
3. Lister un parcours préfixe.
4. Évaluer une expression simple.

## Consigne technique détaillée
- Problème à programmer : Implémenter hauteur, parcours et évaluation sur un arbre binaire représenté par tuples imbriqués.
- Starter code : `code/T05_starter_arbres_binaires.py`.
- Tests attendus : `code/T05_tests_attendus_arbres_binaires.py`.
- Corrigé professeur séparé : `code/T05_corrige_professeur_arbres_binaires.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : arbre vide.
## Étapes de réalisation
- Étape 1 : coder ou tester arbre feuille à partir de `7`, puis contrôler arbre vide.
- Étape 2 : coder ou tester hauteur à partir de racine avec deux feuilles, puis contrôler un seul fils.
- Étape 3 : coder ou tester parcours préfixe à partir de `+ 2 3`, puis contrôler nœud feuille.
- Étape 4 : coder ou tester évaluation à partir de `(2 + 3) * 4`, puis contrôler division par zéro si opérateur `/`.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
## Exercices numérotés
- Exercice 1 : résoudre arbre feuille avec `7` ; attendu : hauteur 0.
- Exercice 2 : expliquer hauteur à partir de racine avec deux feuilles ; attendu : hauteur 1.
- Exercice 3 : comparer parcours préfixe avec `+ 2 3` ; attendu : `+, 2, 3`.
- Exercice 4 : corriger évaluation pour `(2 + 3) * 4` ; attendu : `20`.
- Exercice 5 : tester un cas limite lié à arbre vide ; attendu : le comportement de arbre feuille est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour hauteur ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise parcours préfixe avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur évaluation ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0 ; résultat : hauteur 0 ; contrôle : faire apparaître le contrôle « arbre vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1 ; résultat : hauteur 1 ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3` ; résultat : `+, 2, 3` ; contrôle : comparer avec le cas « nœud feuille ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte ; résultat : `20` ; contrôle : corriger l’erreur « Évaluer un opérateur avant ses opérandes. ».
- Corrigé exercice 5 : méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0 ; résultat : le comportement de arbre feuille est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1 ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Oublier le cas arbre vide. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Remonter les valeurs depuis les feuilles vers la racine. ».

## Erreurs fréquentes
- Erreur fréquente EF1 - Confondre hauteur et nombre de nœuds.
- Erreur fréquente EF2 - Oublier le cas arbre vide.
- Erreur fréquente EF3 - Mélanger parcours préfixe et infixe.
- Erreur fréquente EF4 - Évaluer un opérateur avant ses opérandes.

## Remédiation ciblée
- Activité corrective EF1 : Calculer séparément hauteur gauche et droite.
- Activité corrective EF2 : Décider une convention pour l’arbre vide puis l’appliquer partout.
- Activité corrective EF3 : Écrire l’ordre de visite au-dessus de chaque nœud.
- Activité corrective EF4 : Remonter les valeurs depuis les feuilles vers la racine.

## Différenciation
- Socle : traiter `7` avec une fiche méthode fournie.
- Standard : traiter racine avec deux feuilles en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « nœud feuille » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Validation opérationnelle du TP
- Vérification T05-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification T05-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification T05-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification T05-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification T05-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification T05-6 : comparer l’algorithme écrit avec la capacité officielle citée.
