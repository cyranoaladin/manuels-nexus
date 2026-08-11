---
title: "P01 - Cours - Conversions entre bases"
level: "premiere"
sequence_id: "P01"
document_type: "cours"
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

# P01 - Cours - Conversions entre bases

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

## Définitions et formalisation
- Définition D1 : base dix est utilisé dans Représentation des entiers avec une donnée, une règle et un contrôle.
- Définition D2 : base deux est utilisé dans Représentation des entiers avec une donnée, une règle et un contrôle.
- Définition D3 : base seize est utilisé dans Représentation des entiers avec une donnée, une règle et un contrôle.
- Définition D4 : écriture positionnelle est utilisé dans Représentation des entiers avec une donnée, une règle et un contrôle.
- Cas limite principal : 0 se code 0.

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
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-DATA-BASE-01.
- Point de départ : `13` en base dix.
- Angle disciplinaire : repérage initial autour de décimal vers binaire.
- Démarche attendue : enchaîner divisions par 2 puis lire les restes de bas en haut.
- Exemple associé : `1101₂`.
- Point de vigilance : Écrire les restes dans l’ordre de calcul au lieu de les lire de bas en haut.
- Activité de reprise associée : Rejouer la division de 45 en deux colonnes : quotient et reste.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-DATA-BASE-01.
- Point de départ : `101101₂`.
- Angle disciplinaire : méthode guidée autour de binaire vers décimal.
- Démarche attendue : additionner les poids `32 + 8 + 4 + 1`.
- Exemple associé : `45`.
- Point de vigilance : Additionner les chiffres binaires sans poids de position.
- Activité de reprise associée : Annoter chaque bit par son poids avant toute addition.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-DATA-BASE-01.
- Point de départ : `11110000₂`.
- Angle disciplinaire : transfert argumenté autour de binaire vers hexadécimal.
- Démarche attendue : séparer `1111` et `0000`, puis traduire chaque paquet.
- Exemple associé : `F0₁₆`.
- Point de vigilance : Former des paquets hexadécimaux sans compléter à gauche.
- Activité de reprise associée : Compléter `101101₂` en `0010 1101₂` puis lire les deux paquets.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-DATA-BASE-01.
- Point de départ : `255`.
- Angle disciplinaire : vérification critique autour de décimal vers hexadécimal.
- Démarche attendue : diviser par 16 et lire les restes avec les symboles A à F.
- Exemple associé : `FF₁₆`.
- Point de vigilance : Accepter un chiffre interdit dans la base utilisée.
- Activité de reprise associée : Entourer chaque symbole et vérifier qu’il appartient à l’alphabet de la base.
- Mini-production : produire une correction d’erreur avec un nouveau test.
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre décimal vers binaire avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « 0 se code 0 » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre binaire vers décimal avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « un seul bit à 1 » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre binaire vers hexadécimal avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « complément à gauche si le nombre de bits n’est pas multiple de 4 » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre décimal vers hexadécimal avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « chiffre hexadécimal maximal F » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier décimal vers binaire à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier binaire vers décimal à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier binaire vers hexadécimal à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier décimal vers hexadécimal à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- base dix : terme à employer dans une justification écrite de la séquence.
- base deux : terme à employer dans une justification écrite de la séquence.
- base seize : terme à employer dans une justification écrite de la séquence.
- écriture positionnelle : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P01-A : modifier la donnée du premier exemple de P01 - Cours - Conversions entre bases et conserver exactement la même méthode.
- Variante P01-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P01-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P01-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P01-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P01-F : construire une donnée minimale qui force une décision de méthode.
- Variante P01-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P01-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P01-I : relier une erreur fréquente à une activité corrective précise.
- Variante P01-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P01-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P01-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P01-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P01-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P01-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P01-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
