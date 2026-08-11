---
title: "P06 - trace - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "trace"
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

# P06 - Trace - recherche, tri et fusion de tables

## Trace courte
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Vocabulaire : recherche dans une table, clé id, doublon id=17, tri stable, tri par clé composée.
- Étape 1 : chercher la première ligne id=17.
- Étape 2 : détecter le doublon id=17.
- Résultat de référence : première ligne id=17 -> Ada/robot.

## Cas limites à mémoriser
- table vide.
- clé id=9 absente.
- conflit de clé id=17.

## Erreurs fréquentes
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Critères de réussite observables
- Capacité : P-TABLE-03.
- Résultat final : doublon id=17 -> Ada/python signalé.
- Cas limite : table vide.
