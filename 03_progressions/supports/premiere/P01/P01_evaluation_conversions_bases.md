---
title: "P01 - Evaluation - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation des entiers"
notion: "base dix, base deux, base seize, écriture positionnelle"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-01"
---


# P01 - Évaluation courte - Conversions entre bases

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-01

## Prérequis
- Reconnaître une consigne liée à base dix.
- Distinguer donnée, méthode et conclusion dans le thème Représentation des entiers.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P01-S1 à P01-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un protocole réseau fournit des octets en hexadécimal tandis qu’un relevé de laboratoire donne les mêmes valeurs en décimal.

## Activité d’entrée
1. Convertir 13 par divisions successives.
2. Reconstruire 45 à partir de `101101₂`.
3. Regrouper `11110000₂` par paquets de quatre bits.
4. Refuser une écriture binaire contenant le symbole 2.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé : résoudre décimal vers binaire avec `13` en base dix.
- Réponse attendue : `1101₂`.
- Critère de réussite : méthode visible, résultat correct et contrôle « 0 se code 0 ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé : expliquer binaire vers décimal à partir de `101101₂`.
- Réponse attendue : `45`.
- Critère de réussite : méthode visible, résultat correct et contrôle « un seul bit à 1 ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé : comparer binaire vers hexadécimal avec `11110000₂`.
- Réponse attendue : `F0₁₆`.
- Critère de réussite : méthode visible, résultat correct et contrôle « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé : corriger décimal vers hexadécimal pour `255`.
- Réponse attendue : `FF₁₆`.
- Critère de réussite : méthode visible, résultat correct et contrôle « chiffre hexadécimal maximal F ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à 0 se code 0.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à un seul bit à 1.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à complément à gauche si le nombre de bits n’est pas multiple de 4.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à chiffre hexadécimal maximal F.
## Erreurs fréquentes
- Erreur fréquente EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
- Erreur fréquente EF2 - Additionner les chiffres binaires sans poids de position.
- Erreur fréquente EF3 - Former des paquets hexadécimaux sans compléter à gauche.
- Erreur fréquente EF4 - Accepter un chiffre interdit dans la base utilisée.

## Remédiation ciblée
- Activité corrective EF1 : Rejouer la division de 45 en deux colonnes : quotient et reste.
- Activité corrective EF2 : Annoter chaque bit par son poids avant toute addition.
- Activité corrective EF3 : Compléter `101101₂` en `0010 1101₂` puis lire les deux paquets.
- Activité corrective EF4 : Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base.

## Différenciation
- Socle : traiter `13` en base dix avec une fiche méthode fournie.
- Standard : traiter `101101₂` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « complément à gauche si le nombre de bits n’est pas multiple de 4 » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour P01.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour P01.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour P01.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour P01.

## Corrigé
### Corrigé question 1
- Résultat attendu : `1101₂`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « 0 se code 0 ».
### Corrigé question 2
- Résultat attendu : `45`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « un seul bit à 1 ».
### Corrigé question 3
- Résultat attendu : `F0₁₆`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
### Corrigé question 4
- Résultat attendu : `FF₁₆`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « chiffre hexadécimal maximal F ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche conversions personnelle, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- P-DATA-BASE-01
- P-DATA-BASE-01

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence P01, statut `needs_review`.
- Séance liée : `P01-S1`, avec question centrée sur bases 2, 10 et 16.
- Version aménagée : données bases 2, 10 et 16 surlignées et tableau réponse en trois zones.
- Remédiation : refaire une conversion courte en écrivant chaque division, puis verbaliser la méthode en binôme.

