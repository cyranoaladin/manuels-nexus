---
title: "P02 - Evaluation - Complément à deux et booléens"
level: "premiere"
sequence_id: "P02"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation machine"
notion: "entier signé, complément à deux, débordement, expression booléenne"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-02A"
    - "P-DATA-BASE-02B"
---


# P02 - Évaluation courte - Complément à deux et booléens

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-02A
- P-DATA-BASE-02B

## Prérequis
- Reconnaître une consigne liée à entier signé.
- Distinguer donnée, méthode et conclusion dans le thème Représentation machine.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P02-S1 à P02-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un capteur transmet un octet qui peut représenter une température signée ou un ensemble d’indicateurs logiques.

## Activité d’entrée
1. Décoder `11110110` sur 8 bits signés.
2. Comparer l’intervalle représentable sur 4 bits et sur 8 bits.
3. Simplifier `(a and b) or (a and not b)` avec une table.
4. Repérer un débordement lors de l’encodage de 140 sur 8 bits signés.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé : résoudre décodage signé avec `11110110` sur 8 bits.
- Réponse attendue : `-10`.
- Critère de réussite : méthode visible, résultat correct et contrôle « bit de poids fort à 1 ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé : expliquer bornes sur n bits à partir de `n = 4` bits signés.
- Réponse attendue : `[-8 ; 7]`.
- Critère de réussite : méthode visible, résultat correct et contrôle « asymétrie entre minimum et maximum ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : P-DATA-BASE-02A, P-DATA-BASE-02B.
- Énoncé : comparer encodage négatif avec `-6` sur 8 bits.
- Réponse attendue : `11111010`.
- Critère de réussite : méthode visible, résultat correct et contrôle « retenue finale ignorée sur la largeur fixée ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé : corriger simplification booléenne pour `(a and b) or (a and not b)`.
- Réponse attendue : `a`.
- Critère de réussite : méthode visible, résultat correct et contrôle « un exemple ne prouve pas une identité ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à bit de poids fort à 1.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à asymétrie entre minimum et maximum.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à retenue finale ignorée sur la largeur fixée.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à un exemple ne prouve pas une identité.
## Erreurs fréquentes
- Erreur fréquente EF1 - Lire un mot binaire signé comme un entier naturel.
- Erreur fréquente EF2 - Oublier de tester les bornes avant l’encodage.
- Erreur fréquente EF3 - Inverser les bits sans ajouter 1.
- Erreur fréquente EF4 - Simplifier une expression booléenne avec un seul exemple.

## Remédiation ciblée
- Activité corrective EF1 : Regarder d’abord le bit de poids fort puis choisir naturel ou signé.
- Activité corrective EF2 : Écrire explicitement l’intervalle avant chaque conversion.
- Activité corrective EF3 : Séparer inversion et ajout de 1 dans deux lignes distinctes.
- Activité corrective EF4 : Remplir les quatre lignes de la table avant de conclure.

## Différenciation
- Socle : traiter `11110110` sur 8 bits avec une fiche méthode fournie.
- Standard : traiter `n = 4` bits signés en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « retenue finale ignorée sur la largeur fixée » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour P02.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour P02.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour P02.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour P02.

## Corrigé
### Corrigé question 1
- Résultat attendu : `-10`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « bit de poids fort à 1 ».
### Corrigé question 2
- Résultat attendu : `[-8 ; 7]`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « asymétrie entre minimum et maximum ».
### Corrigé question 3
- Résultat attendu : `11111010`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « retenue finale ignorée sur la largeur fixée ».
### Corrigé question 4
- Résultat attendu : `a`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « un exemple ne prouve pas une identité ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche complément à deux et booléens, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- P-DATA-BASE-02A
- P-DATA-BASE-02B

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence P02, statut `needs_review`.
- Séance liée : `P02-S1`, avec question centrée sur encodage signé et table de vérité.
- Version aménagée : données encodage signé et table de vérité surlignées et tableau réponse en trois zones.
- Remédiation : recalculer un codage sur 4 bits puis vérifier les bornes, puis verbaliser la méthode en binôme.

