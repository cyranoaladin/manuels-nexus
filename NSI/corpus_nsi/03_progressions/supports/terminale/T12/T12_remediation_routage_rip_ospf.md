---
title: "T12 - remediation - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "remediation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - Remédiation - routage RIP et OSPF

## Diagnostic
- sauts et coûts mélangés.
- choix visuel.
- panne non recalculée.

## Activités correctives
1. Annoter `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
2. Refaire la tâche `compter sauts RIP` et comparer avec `RIP : A-B-D et A-C-D ont 2 sauts`.
3. Traiter le cas limite `égalité exacte`.
4. Relier la réponse à T-ARCH-03.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
