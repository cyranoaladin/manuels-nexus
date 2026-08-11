---
title: "Projet associé - Mini encodeur de badge"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "projet"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "mini-projet"
duration: "2 h"
difficulty: "standard"
private_data: false
official_program: {level: "premiere", rubrique: "Représentation des données", content: "Projet", capacities: []}
prerequisites: ["TP S01"]
learning_objectives: ["Réinvestir les représentations dans un petit artefact."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Projet associé - Mini encodeur de badge

## Cahier des charges

Créer un petit module qui encode les informations fictives d'un badge.
Le badge contient un identifiant positif.
Le badge contient une variation de solde relative.
Le badge contient un droit booléen.
Le badge contient une initiale Unicode.
Aucune donnée réelle de personne ne doit être utilisée.

## Jalons

Jalon 1 : définir les fonctions attendues.
Jalon 2 : écrire les conversions.
Jalon 3 : écrire les tests ordinaires.
Jalon 4 : écrire les tests de limites.
Jalon 5 : rédiger les choix de représentation.

## Livrables

- Un fichier Python court.
- Un fichier de tests.
- Une note de justification.
- Une démonstration avec données fictives.

## Critères d'évaluation

- Les conventions sont explicites.
- Les tests couvrent au moins un cas limite.
- Les noms utilisés sont fictifs.
- Les choix liste, tuple ou dictionnaire sont justifiés.

## Grille de soutenance

- Présenter la donnée codée : 2 points.
- Expliquer la convention de lecture : 4 points.
- Montrer un test : 4 points.
- Justifier une structure : 4 points.
- Répondre à une question : 6 points.

## Version minimale

Convertir un identifiant en base 2 et base 16.
Tester `0` et `42`.

## Version standard

Ajouter le complément à deux et l'initiale Unicode.
Tester une valeur négative et un caractère accentué.

## Version experte

Ajouter une fonction qui choisit liste, tuple ou dictionnaire à partir d'un scénario.
Ajouter une explication de cas limite non trivial.

## Erreurs fréquentes

- Utiliser de vrais noms.
- Oublier les bornes du complément à deux.
- Ne pas relier les tests aux fonctions.

## Auto-évaluation

- Mon projet n'utilise aucune donnée personnelle.
- Mon projet contient des tests.
- Mon projet explique ses conventions.
