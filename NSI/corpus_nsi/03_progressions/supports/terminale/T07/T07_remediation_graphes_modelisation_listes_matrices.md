---
title: "T07 - remediation - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "remediation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "graphes, listes et matrices"
notion: "graphes, listes et matrices"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-05A"
    - "T-STRUCT-05B"
    - "T-STRUCT-05C"
    - "T-STRUCT-05D"
---

# T07 - Remédiation - graphes, listes et matrices

## Diagnostic
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Activités correctives
1. Annoter `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
2. Refaire la tâche `lister voisins sortants` et comparer avec `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
3. Traiter le cas limite `sommet isolé E`.
4. Relier la réponse à T-STRUCT-05A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
