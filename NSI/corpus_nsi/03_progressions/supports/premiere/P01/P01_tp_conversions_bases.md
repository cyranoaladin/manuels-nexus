---
title: "P01 - Tp - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "tp"
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


# P01 - TP - Conversions entre bases

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

## Consigne technique détaillée
- Problème à programmer : Écrire des fonctions de conversion sans utiliser `bin`, `hex` ou `int(x, base)` pour la méthode principale.
- Starter code : `code/P01_starter_conversions_bases.py`.
- Tests attendus : `code/P01_tests_attendus_conversions_bases.py`.
- Corrigé professeur séparé : `code/P01_corrige_professeur_conversions_bases.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : 0 se code 0.
## Étapes de réalisation
- Étape 1 : coder ou tester décimal vers binaire à partir de `13` en base dix, puis contrôler 0 se code 0.
- Étape 2 : coder ou tester binaire vers décimal à partir de `101101₂`, puis contrôler un seul bit à 1.
- Étape 3 : coder ou tester binaire vers hexadécimal à partir de `11110000₂`, puis contrôler complément à gauche si le nombre de bits n’est pas multiple de 4.
- Étape 4 : coder ou tester décimal vers hexadécimal à partir de `255`, puis contrôler chiffre hexadécimal maximal F.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
## Exercices numérotés
- Exercice 1 : résoudre décimal vers binaire avec `13` en base dix ; attendu : `1101₂`.
- Exercice 2 : expliquer binaire vers décimal à partir de `101101₂` ; attendu : `45`.
- Exercice 3 : comparer binaire vers hexadécimal avec `11110000₂` ; attendu : `F0₁₆`.
- Exercice 4 : corriger décimal vers hexadécimal pour `255` ; attendu : `FF₁₆`.
- Exercice 5 : tester un cas limite lié à 0 se code 0 ; attendu : le comportement de décimal vers binaire est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour binaire vers décimal ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise binaire vers hexadécimal avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur décimal vers hexadécimal ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut », puis écrire `1101₂` ; résultat : `1101₂` ; contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de additionner les poids `32 + 8 + 4 + 1` avant de conclure par `45` ; résultat : `45` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » et valider `F0₁₆` ; résultat : `F0₁₆` ; contrôle : comparer avec le cas « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Accepter un chiffre interdit dans la base utilisée. » puis reprendre la procédure correcte ; résultat : `FF₁₆` ; contrôle : corriger l’erreur « Accepter un chiffre interdit dans la base utilisée. ».
- Corrigé exercice 5 : méthode : identifier `13` en base dix, appliquer la méthode « enchaîner divisions par 2 puis lire les restes de bas en haut », puis écrire `1101₂` ; résultat : le comportement de décimal vers binaire est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de additionner les poids `32 + 8 + 4 + 1` avant de conclure par `45` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Additionner les chiffres binaires sans poids de position. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » et valider `F0₁₆` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Accepter un chiffre interdit dans la base utilisée. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base. ».

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

## Validation opérationnelle du TP
- Vérification P01-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification P01-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification P01-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification P01-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification P01-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification P01-6 : comparer l’algorithme écrit avec la capacité officielle citée.
