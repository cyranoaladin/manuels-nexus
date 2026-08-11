---
title: "T08 - remediation - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "remediation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "BFS, DFS, cycles et chemins"
notion: "BFS, DFS, cycles et chemins"
private_data: false
official_program:
  capacities:
    - "T-ALGO-02A"
    - "T-ALGO-02B"
    - "T-ALGO-02C"
    - "T-ALGO-02D"
---

# T08 - Remédiation - BFS, DFS, cycles et chemins

## Diagnostic
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Activités correctives
1. Annoter `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
2. Refaire la tâche `BFS file A puis B,C puis D,E` et comparer avec `BFS -> A,B,C,D,E`.
3. Traiter le cas limite `sommet isolé F`.
4. Relier la réponse à T-ALGO-02A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
