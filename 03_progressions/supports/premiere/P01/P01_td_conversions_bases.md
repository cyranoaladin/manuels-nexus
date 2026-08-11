---
title: "P01 - Td - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "td"
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

# P01 - TD - Conversions entre bases

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

## Exemples corrigés précis
### Exemple corrigé 1 - décimal vers binaire
- Donnée étudiée : `13` en base dix.
- Méthode : enchaîner divisions par 2 puis lire les restes de bas en haut.
- Résultat obtenu : `1101₂`.
- Contrôle : le cas limite « 0 se code 0 » est vérifié séparément.
### Exemple corrigé 2 - binaire vers décimal
- Donnée étudiée : `101101₂`.
- Méthode : additionner les poids `32 + 8 + 4 + 1`.
- Résultat obtenu : `45`.
- Contrôle : le cas limite « un seul bit à 1 » est vérifié séparément.
### Exemple corrigé 3 - binaire vers hexadécimal
- Donnée étudiée : `11110000₂`.
- Méthode : séparer `1111` et `0000`, puis traduire chaque paquet.
- Résultat obtenu : `F0₁₆`.
- Contrôle : le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » est vérifié séparément.
### Exemple corrigé 4 - décimal vers hexadécimal
- Donnée étudiée : `255`.
- Méthode : diviser par 16 et lire les restes avec les symboles A à F.
- Résultat obtenu : `FF₁₆`.
- Contrôle : le cas limite « chiffre hexadécimal maximal F » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : résoudre décimal vers binaire avec `13` en base dix.
- Production attendue : `1101₂`.
- Contrainte de contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : expliquer binaire vers décimal à partir de `101101₂`.
- Production attendue : `45`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : comparer binaire vers hexadécimal avec `11110000₂`.
- Production attendue : `F0₁₆`.
- Contrainte de contrôle : comparer avec le cas « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : corriger décimal vers hexadécimal pour `255`.
- Production attendue : `FF₁₆`.
- Contrainte de contrôle : corriger l’erreur « Accepter un chiffre interdit dans la base utilisée. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : tester un cas limite lié à 0 se code 0.
- Production attendue : le comportement de décimal vers binaire est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : classer deux méthodes possibles pour binaire vers décimal.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Additionner les chiffres binaires sans poids de position. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : justifier un transfert qui utilise binaire vers hexadécimal avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-01.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur décimal vers hexadécimal.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : `1101₂`.
- Contrôle : faire apparaître le contrôle « 0 se code 0 ».
- Erreur traitée : EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
- Donnée utilisée alpha dans P01 td conversions bases : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P01 td conversions bases : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P01 td conversions bases : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `45`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Additionner les chiffres binaires sans poids de position.
- Donnée utilisée beta dans P01 td conversions bases : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P01 td conversions bases : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P01 td conversions bases : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `F0₁₆`.
- Contrôle : comparer avec le cas « complément à gauche si le nombre de bits n’est pas multiple de 4 ».
- Erreur traitée : EF3 - Former des paquets hexadécimaux sans compléter à gauche.
- Donnée utilisée gamma dans P01 td conversions bases : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P01 td conversions bases : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P01 td conversions bases : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : `FF₁₆`.
- Contrôle : corriger l’erreur « Accepter un chiffre interdit dans la base utilisée. ».
- Erreur traitée : EF4 - Accepter un chiffre interdit dans la base utilisée.
- Donnée utilisée delta dans P01 td conversions bases : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P01 td conversions bases : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P01 td conversions bases : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de décimal vers binaire est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
- Donnée utilisée epsilon dans P01 td conversions bases : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P01 td conversions bases : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P01 td conversions bases : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Additionner les chiffres binaires sans poids de position. » est une erreur.
- Erreur traitée : EF2 - Additionner les chiffres binaires sans poids de position.
- Donnée utilisée zeta dans P01 td conversions bases : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P01 td conversions bases : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P01 td conversions bases : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Former des paquets hexadécimaux sans compléter à gauche.
- Donnée utilisée eta dans P01 td conversions bases : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P01 td conversions bases : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P01 td conversions bases : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base. ».
- Erreur traitée : EF4 - Accepter un chiffre interdit dans la base utilisée.
- Donnée utilisée theta dans P01 td conversions bases : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P01 td conversions bases : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P01 td conversions bases : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P01 td conversions bases : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

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
