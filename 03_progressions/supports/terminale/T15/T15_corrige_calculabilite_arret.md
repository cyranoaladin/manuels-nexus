---
title: "T15 - corrige - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - Corrigé - calculabilité, programme comme donnée et arrêt

## Corrigé du TD
### Exercice 1
- Réponse attendue : source="print(1)" est une donnée.
- Méthode : encoder un programme comme texte.
- Cas limite : programme très long mais fini.
### Exercice 2
- Réponse attendue : arrete(P,x) renvoie True ou False.
- Méthode : raisonner indépendamment de Python.
- Cas limite : langage différent.
### Exercice 3
- Réponse attendue : Q boucle si arrete(Q,Q) dit True.
- Méthode : poser un oracle hypothétique.
- Cas limite : entrée absente.
### Exercice 4
- Réponse attendue : contradiction donc oracle impossible.
- Méthode : construire un programme contradictoire.
- Cas limite : programme très long mais fini.
### Exercice 5
- Réponse attendue : source="print(1)" est une donnée.
- Méthode : encoder un programme comme texte.
- Cas limite : langage différent.
### Exercice 6
- Réponse attendue : arrete(P,x) renvoie True ou False.
- Méthode : raisonner indépendamment de Python.
- Cas limite : entrée absente.
### Exercice 7
- Réponse attendue : Q boucle si arrete(Q,Q) dit True.
- Méthode : poser un oracle hypothétique.
- Cas limite : programme très long mais fini.
### Exercice 8
- Réponse attendue : contradiction donc oracle impossible.
- Méthode : construire un programme contradictoire.
- Cas limite : langage différent.

## Corrigé du TP
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Résultat principal : source="print(1)" est une donnée.
- Résultat secondaire : arrete(P,x) renvoie True ou False.

## Corrigé de l évaluation
- Question 1 : source="print(1)" est une donnée.
- Question 2 : arrete(P,x) renvoie True ou False.
- Question 3 : Q boucle si arrete(Q,Q) dit True.
- Question 4 : contradiction donc oracle impossible.
