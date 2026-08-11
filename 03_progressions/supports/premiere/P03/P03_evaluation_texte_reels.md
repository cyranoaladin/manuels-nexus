---
title: "P03 - Evaluation - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Données textuelles et approximation"
notion: "Unicode, UTF-8, octet, flottant"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-05A"
    - "P-DATA-BASE-03"
---


# P03 - Évaluation courte - Texte Unicode et nombres réels

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05A
- P-DATA-BASE-03

## Prérequis
- Reconnaître une consigne liée à Unicode.
- Distinguer donnée, méthode et conclusion dans le thème Données textuelles et approximation.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P03-S1 à P03-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un formulaire international mélange accents, symboles monétaires et mesures décimales calculées par programme.

## Activité d’entrée
1. Comparer `A`, `é` et `€` selon caractères et octets.
2. Encoder `Aé` en UTF-8.
3. Observer `0.1 + 0.2` dans Python.
4. Décider quand utiliser une tolérance.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé : résoudre ASCII simple avec `A`.
- Réponse attendue : `41` en hexadécimal.
- Critère de réussite : méthode visible, résultat correct et contrôle « caractère dans l’ASCII ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé : expliquer accent UTF-8 à partir de `é`.
- Réponse attendue : `c3 a9`.
- Critère de réussite : méthode visible, résultat correct et contrôle « longueur en octets différente de la longueur en caractères ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé : comparer chaîne mixte avec `Aé`.
- Réponse attendue : 2 caractères et 3 octets.
- Critère de réussite : méthode visible, résultat correct et contrôle « chaîne vide ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : P-DATA-BASE-05A, P-DATA-BASE-03.
- Énoncé : corriger flottant pour `0.1 + 0.2`.
- Réponse attendue : valeur proche de `0.3`.
- Critère de réussite : méthode visible, résultat correct et contrôle « arrondi binaire ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à caractère dans l’ASCII.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à longueur en octets différente de la longueur en caractères.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à chaîne vide.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à arrondi binaire.
## Erreurs fréquentes
- Erreur fréquente EF1 - Compter les caractères au lieu des octets en UTF-8.
- Erreur fréquente EF2 - Croire que tout caractère occupe un octet.
- Erreur fréquente EF3 - Comparer deux flottants avec égalité stricte après calcul.
- Erreur fréquente EF4 - Confondre point de code et représentation binaire.

## Remédiation ciblée
- Activité corrective EF1 : Afficher la liste des octets avec `encode("utf-8")`.
- Activité corrective EF2 : Construire un tableau caractère, point de code, octets.
- Activité corrective EF3 : Utiliser une tolérance absolue et justifier son ordre de grandeur.
- Activité corrective EF4 : Séparer nom du caractère et encodage effectif.

## Différenciation
- Socle : traiter `A` avec une fiche méthode fournie.
- Standard : traiter `é` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « chaîne vide » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour P03.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour P03.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour P03.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour P03.

## Corrigé
### Corrigé question 1
- Résultat attendu : `41` en hexadécimal.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « caractère dans l’ASCII ».
### Corrigé question 2
- Résultat attendu : `c3 a9`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « longueur en octets différente de la longueur en caractères ».
### Corrigé question 3
- Résultat attendu : 2 caractères et 3 octets.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « chaîne vide ».
### Corrigé question 4
- Résultat attendu : valeur proche de `0.3`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « arrondi binaire ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche texte Unicode et flottants, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- P-DATA-BASE-05A
- P-DATA-BASE-03

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence P03, statut `needs_review`.
- Séance liée : `P03-S1`, avec question centrée sur code points, octets et approximations.
- Version aménagée : données code points, octets et approximations surlignées et tableau réponse en trois zones.
- Remédiation : reprendre un caractère accentué puis un flottant simple, puis verbaliser la méthode en binôme.

