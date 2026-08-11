---
title: "Guide professeur - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "guide_prof"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "pilotage de séquence"
duration: "5 séances"
difficulty: "standard"
private_data: false
official_program: {level: "premiere", rubrique: "Représentation des données", content: "Guide professeur", capacities: []}
prerequisites: ["Bases Python très simples"]
learning_objectives: ["Piloter une séquence progressive et auditable."]
assessment: {formative: true, summative: true}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Guide professeur - S01

## Objectifs

- Stabiliser le concept de représentation.
- Installer bases 2, 10, 16.
- Introduire le complément à deux sans formalisme excessif.
- Faire construire des tables de vérité.
- Relier texte et encodage.
- Justifier liste, tuple et dictionnaire.
- Installer l'habitude des tests.

## Durée

Séquence prévue sur 5 séances de 1 h à 1 h 30.
Une séance supplémentaire est possible si les conversions sont fragiles.

## Scénario séance par séance

Séance 1 : situation badge, bit, bases 2/10/16, exercices courts.
Séance 2 : entiers positifs, bornes, complément à deux.
Séance 3 : booléens, table de vérité, texte et Unicode.
Séance 4 : listes, tuples, dictionnaires, choix de représentation.
Séance 5 : TP Python et tests.
Évaluation courte après consolidation.

## Difficultés prévisibles

- Les élèves lisent une écriture sans préciser la base.
- Le complément à deux est confondu avec un simple bit de signe.
- Les tables de vérité sont incomplètes.
- Le mot "caractère" est confondu avec "octet".
- La liste est utilisée par défaut pour tout.
- Les tests sont perçus comme facultatifs.

## Remédiation

- Revenir à la phrase : "quelle convention de lecture ?"
- Utiliser des cartes de bits pour manipuler les conversions.
- Faire décoder la même suite avec deux conventions différentes.
- Faire comparer `len("é")` et `len("é".encode("utf-8"))`.
- Faire verbaliser l'opération principale avant le choix de structure.

## Différenciation

- Fragile : conversions inférieures à 32, tables à deux variables.
- Standard : conversions sur octet et choix de structure justifié.
- Expert : tests de bornes, comparaison liste/dictionnaire, UTF-8 multi-octets.

## Questions orales

- Que faut-il connaître pour interpréter `1010` ?
- Pourquoi `11111111` peut-il représenter `255` ou `-1` ?
- Que signifie "encodage" pour un texte ?
- Pourquoi les index commencent-ils à zéro en Python ?
- Quelle opération rend le dictionnaire pertinent ?

## Critères d'évaluation

- Méthode de conversion explicite.
- Convention de signe précisée.
- Table de vérité exhaustive.
- Justification du choix de structure.
- Tests ordinaires et limites présents.

## Barème

- Conversions : 4 points.
- Complément à deux : 4 points.
- Booléens et texte : 3 points.
- Structures Python : 5 points.
- Tests et justification : 4 points.

## Erreurs fréquentes

- Réponse numérique sans base.
- Code non testé sur zéro.
- Utilisation de noms propres d'élèves dans les exemples.
- Mélange entre corrigé professeur et version élève.

## Prolongements

- Traitement de données en tables.
- Flottants et limites de représentation.
- Encodage d'images simples.
- Algorithmique sur tableaux.

## Ajustements possibles

Si la classe bloque sur le complément à deux, réduire d'abord à 4 bits.

Si la classe maîtrise déjà les conversions, avancer plus vite vers Unicode.

Si les dictionnaires sont fragiles, limiter l'exemple à deux clés.

Si le temps manque, déplacer l'extension experte en devoir facultatif.

Prévoir une correction orale de cinq minutes sur les erreurs de vocabulaire.

Conserver une trace des questions récurrentes pour la séance suivante.
