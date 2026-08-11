---
title: "P06 - remediation - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "remediation"
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

# P06 - Remédiation - recherche, tri et fusion de tables

## Diagnostic
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Activités correctives
1. Annoter `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
2. Refaire la tâche `chercher la première ligne id=17` et comparer avec `première ligne id=17 -> Ada/robot`.
3. Traiter le cas limite `table vide`.
4. Relier la réponse à P-TABLE-03.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
