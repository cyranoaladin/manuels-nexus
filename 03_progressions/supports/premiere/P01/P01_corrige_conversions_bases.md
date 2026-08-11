---
title: "P01 - Corrige - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "corrige"
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


# P01 - Corrigé professeur - Conversions entre bases

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

## Méthode générale de correction
- Point 1 : pour décimal vers binaire, exiger la donnée `13` en base dix, la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut » et le contrôle « 0 se code 0 ».
- Point 2 : pour binaire vers décimal, exiger la donnée `101101₂`, la méthode « additionner les poids `32 + 8 + 4 + 1` » et le contrôle « un seul bit à 1 ».
- Point 3 : pour binaire vers hexadécimal, exiger la donnée `11110000₂`, la méthode « séparer `1111` et `0000`, puis traduire chaque paquet » et le contrôle « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
- Point 4 : pour décimal vers hexadécimal, exiger la donnée `255`, la méthode « diviser par 16 et lire les restes avec les symboles A à F » et le contrôle « chiffre hexadécimal maximal F ».
## Exercices numérotés
- Exercice 1 : résoudre décimal vers binaire avec `13` en base dix ; attendu : `1101₂`.
- Exercice 2 : expliquer binaire vers décimal à partir de `101101₂` ; attendu : `45`.
- Exercice 3 : comparer binaire vers hexadécimal avec `11110000₂` ; attendu : `F0₁₆`.
- Exercice 4 : corriger décimal vers hexadécimal pour `255` ; attendu : `FF₁₆`.
- Exercice 5 : tester un cas limite lié à 0 se code 0 ; attendu : le comportement de décimal vers binaire est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour binaire vers décimal ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise binaire vers hexadécimal avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur décimal vers hexadécimal ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut », puis écrire `1101₂`.
- Résultat : `1101₂`.
- Contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Erreur traitée : EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de additionner les poids `32 + 8 + 4 + 1` avant de conclure par `45`.
- Résultat : `45`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Additionner les chiffres binaires sans poids de position.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » et valider `F0₁₆`.
- Résultat : `F0₁₆`.
- Contrôle : comparer avec le cas « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
- Erreur traitée : EF3 - Former des paquets hexadécimaux sans compléter à gauche.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Accepter un chiffre interdit dans la base utilisée. » puis reprendre la procédure correcte.
- Résultat : `FF₁₆`.
- Contrôle : corriger l’erreur « Accepter un chiffre interdit dans la base utilisée. ».
- Erreur traitée : EF4 - Accepter un chiffre interdit dans la base utilisée.
### Corrigé exercice 5
- Méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut », puis écrire `1101₂`.
- Résultat : le comportement de décimal vers binaire est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de additionner les poids `32 + 8 + 4 + 1` avant de conclure par `45`.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Additionner les chiffres binaires sans poids de position. » est une erreur.
- Erreur traitée : EF2 - Additionner les chiffres binaires sans poids de position.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » et valider `F0₁₆`.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Former des paquets hexadécimaux sans compléter à gauche.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Accepter un chiffre interdit dans la base utilisée. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base. ».
- Erreur traitée : EF4 - Accepter un chiffre interdit dans la base utilisée.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « 0 se code 0 » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « complément à gauche si le nombre de bits n’est pas multiple de 4 » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Accepter un chiffre interdit dans la base utilisée. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Additionner les chiffres binaires sans poids de position. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base. » ».
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
