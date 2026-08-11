---
title: "Fiche méthode - Choisir une représentation"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "fiche_methode"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "méthode de choix de représentation"
duration: "20 min"
difficulty: "standard"
private_data: false
official_program: {level: "premiere", rubrique: "Représentation des données", content: "Choisir une représentation", capacities: []}
prerequisites: ["Cours S01"]
learning_objectives: ["Appliquer une méthode de choix de représentation."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Fiche méthode - Choisir une représentation

## Situation-problème

On doit stocker une information mais plusieurs représentations sont possibles.
Le risque est de choisir la première représentation venue.
La méthode impose de partir du traitement attendu.

## Méthode

Étape 1 : nommer la donnée.
Étape 2 : identifier les valeurs possibles.
Étape 3 : repérer si la donnée peut être négative.
Étape 4 : repérer si la donnée est logique, numérique, textuelle ou composée.
Étape 5 : identifier l'opération la plus fréquente.
Étape 6 : choisir une représentation candidate.
Étape 7 : vérifier un cas ordinaire.
Étape 8 : vérifier un cas limite.
Étape 9 : rédiger la justification.

## Exemple

Donnée : code de badge.
Valeurs possibles : entiers positifs.
Opération fréquente : comparaison d'identifiants.
Représentation candidate : entier positif en base 10 côté humain, binaire côté machine.
Cas limite : identifiant `0`.
Justification : l'identifiant ne porte pas de signe et doit être comparé rapidement.

## Erreurs fréquentes

- Choisir une liste alors que l'accès se fait par clé.
- Oublier que le nombre de bits limite l'intervalle.
- Ecrire une conversion sans préciser la base.
- Tester seulement une valeur ordinaire.

## Auto-évaluation

- Je sais identifier l'opération principale.
- Je sais citer un cas limite.
- Je sais justifier liste, tuple ou dictionnaire.
- Je sais expliquer le rôle de la convention de lecture.

## Vérification finale

Je vérifie l'unité de représentation : bit, octet, caractère ou collection.

Je vérifie le domaine de valeurs accepté.

Je vérifie un cas limite avant de généraliser.

Je relie toujours la méthode au TD ou au TP.
