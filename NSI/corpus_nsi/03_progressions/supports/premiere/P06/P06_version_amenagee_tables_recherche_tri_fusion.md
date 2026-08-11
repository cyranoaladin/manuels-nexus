---
title: "P06 - version_amenagee - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "version_amenagee"
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

# P06 - Version aménagée - recherche, tri et fusion de tables

## Aides intégrées
- Donnée fournie : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Mots utiles : recherche dans une table, clé id, doublon id=17, tri stable, tri par clé composée.
- Méthode guidée : chercher la première ligne id=17 puis détecter le doublon id=17.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-TABLE-03 ou P-TABLE-04.
3. Compléter le résultat : première ligne id=17 -> Ada/robot.
4. Cocher le cas limite : table vide.

## Réponses rapides
- Réponse 1 : première ligne id=17 -> Ada/robot.
- Réponse 2 : doublon id=17 -> Ada/python signalé.
- Réponse 3 : tri -> Ada/python, Ada/robot, Linus/web.
