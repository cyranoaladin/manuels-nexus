---
title: "Aides progressives - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "aides"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "aides différenciées"
duration: "variable"
difficulty: "socle"
private_data: false
official_program: {level: "premiere", rubrique: "Représentation des données", content: "Aides", capacities: []}
prerequisites: ["Cours et TD S01"]
learning_objectives: ["Permettre une entrée graduée dans les tâches."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Aides progressives - S01

## Situation-problème

Un blocage en représentation vient souvent d'une convention oubliée.
Les aides ci-dessous guident sans donner directement toute la réponse.

## Aides progressives

### Niveau 1 - Comprendre la question

- Entourer la base demandée.
- Souligner le nombre de bits.
- Repérer si la valeur peut être négative.
- Repérer si la donnée est une collection.
- Nommer l'opération principale : lire, modifier, chercher, compter, convertir.

### Niveau 2 - Mettre en route

- Ecrire les puissances de 2 ou de 16.
- Pour la conversion vers base 10, multiplier chaque chiffre par son poids.
- Pour la conversion depuis base 10, faire les divisions successives.
- Pour le complément à deux, calculer l'intervalle représentable.
- Pour une table de vérité, lister tous les couples `False/True`.
- Pour une structure Python, essayer une phrase : "j'ai besoin de chercher par...".

### Niveau 3 - Vérifier

- Refaire la conversion dans l'autre sens.
- Vérifier que le résultat tient dans le nombre de bits.
- Tester une valeur limite.
- Vérifier qu'une clé de dictionnaire existe avant de l'utiliser.
- Lire le résultat avec une phrase humaine.

## Erreurs fréquentes

- Lire trop vite la base.
- Oublier la ligne `False, False` d'une table de vérité.
- Croire que `11111111` a une seule signification.
- Ecrire un test qui reproduit seulement l'exemple du cours.

## Extension

Créer une mini-fiche personnelle : une erreur que je fais souvent, un exemple, un test qui la détecte.

## Auto-évaluation

- Je sais choisir une aide adaptée.
- Je sais expliquer ce que l'aide m'a permis de débloquer.
- Je sais refaire sans aide après correction.

## Différenciation

- Fragile : utiliser les aides niveau 1 et 2 avec nombres inférieurs à 32.
- Standard : utiliser les aides niveau 2 et 3 sur 8 bits.
- Expert : rédiger une aide supplémentaire pour un camarade.

## Renforcement après correction

Reprendre une erreur en indiquant la représentation utilisée.

Dire si l'erreur porte sur la valeur, le codage ou le type Python.

Refaire un exemple analogue avec des nombres plus petits.

Comparer la réponse obtenue avec un calcul mental simple.

Expliquer à un camarade la première étape seulement.

Noter la question à poser au professeur si le blocage persiste.
