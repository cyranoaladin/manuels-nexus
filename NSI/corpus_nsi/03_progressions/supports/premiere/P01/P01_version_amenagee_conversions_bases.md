---
title: "P01 - Version amenagee - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "version_amenagee"
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


# P01 - Version aménagée - Conversions entre bases

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

## Version aménagée - Énoncé élève
### Question aménagée 1
- Énoncé élève : traiter décimal vers binaire avec la donnée `13` en base dix.
- Aide intégrée : commencer par enchaîner divisions par 2 puis lire les restes de bas en haut.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
### Question aménagée 2
- Énoncé élève : traiter binaire vers décimal avec la donnée `101101₂`.
- Aide intégrée : commencer par additionner les poids `32 + 8 + 4 + 1`.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Additionner les chiffres binaires sans poids de position.
### Question aménagée 3
- Énoncé élève : traiter binaire vers hexadécimal avec la donnée `11110000₂`.
- Aide intégrée : commencer par séparer `1111` et `0000`, puis traduire chaque paquet.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Former des paquets hexadécimaux sans compléter à gauche.
### Question aménagée 4
- Énoncé élève : traiter décimal vers hexadécimal avec la donnée `255`.
- Aide intégrée : commencer par diviser par 16 et lire les restes avec les symboles A à F.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Accepter un chiffre interdit dans la base utilisée.
## Exercices numérotés
- Exercice 1 : résoudre décimal vers binaire avec `13` en base dix avec aide possible sur la méthode.
- Exercice 2 : expliquer binaire vers décimal à partir de `101101₂` avec aide possible sur la méthode.
- Exercice 3 : comparer binaire vers hexadécimal avec `11110000₂` avec aide possible sur la méthode.
- Exercice 4 : corriger décimal vers hexadécimal pour `255` avec aide possible sur la méthode.
- Exercice 5 : tester un cas limite lié à 0 se code 0 avec aide possible sur la méthode.
- Exercice 6 : classer deux méthodes possibles pour binaire vers décimal avec aide possible sur la méthode.
- Exercice 7 : justifier un transfert qui utilise binaire vers hexadécimal avec une donnée nouvelle avec aide possible sur la méthode.
- Exercice 8 : étendre un énoncé volontairement erroné sur décimal vers hexadécimal avec aide possible sur la méthode.
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
