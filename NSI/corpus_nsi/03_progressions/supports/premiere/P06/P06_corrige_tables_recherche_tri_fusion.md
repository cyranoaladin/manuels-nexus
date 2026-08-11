---
title: "P06 - corrige - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "recherche, tri et fusion de tables"
notion: "recherche, tri et fusion de tables"
private_data: false
official_program:
  capacities:
    - "P-TABLE-03"
    - "P-TABLE-04"
---

# P06 - Corrigé - recherche, tri et fusion de tables

## Corrigé du TD
### Exercice 1
- Réponse attendue : première ligne id=17 -> Ada/robot.
- Méthode : chercher la première ligne id=17.
- Cas limite : table vide.
### Exercice 2
- Réponse attendue : doublon id=17 -> Ada/python signalé.
- Méthode : détecter le doublon id=17.
- Cas limite : clé id=9 absente.
### Exercice 3
- Réponse attendue : tri -> Ada/python, Ada/robot, Linus/web.
- Méthode : trier par (nom, atelier).
- Cas limite : conflit de clé id=17.
### Exercice 4
- Réponse attendue : fusion -> erreur id_absent=9.
- Méthode : fusionner inscriptions et présences.
- Cas limite : table vide.
### Exercice 5
- Réponse attendue : première ligne id=17 -> Ada/robot.
- Méthode : chercher la première ligne id=17.
- Cas limite : clé id=9 absente.
### Exercice 6
- Réponse attendue : doublon id=17 -> Ada/python signalé.
- Méthode : détecter le doublon id=17.
- Cas limite : conflit de clé id=17.
### Exercice 7
- Réponse attendue : tri -> Ada/python, Ada/robot, Linus/web.
- Méthode : trier par (nom, atelier).
- Cas limite : table vide.
### Exercice 8
- Réponse attendue : fusion -> erreur id_absent=9.
- Méthode : fusionner inscriptions et présences.
- Cas limite : clé id=9 absente.

## Corrigé du TP
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Résultat principal : première ligne id=17 -> Ada/robot.
- Résultat secondaire : doublon id=17 -> Ada/python signalé.

## Corrigé de l évaluation
- Question 1 : première ligne id=17 -> Ada/robot.
- Question 2 : doublon id=17 -> Ada/python signalé.
- Question 3 : tri -> Ada/python, Ada/robot, Linus/web.
- Question 4 : fusion -> erreur id_absent=9.
