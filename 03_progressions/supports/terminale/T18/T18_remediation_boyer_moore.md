---
title: "T18 - remediation - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "remediation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - Remédiation - Boyer-Moore

## Diagnostic
- comparaison gauche à droite.
- décalage nul.
- caractère absent oublié.

## Activités correctives
1. Annoter `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`.
2. Refaire la tâche `prétraiter dernière position de chaque caractère` et comparer avec `table : A->2, N->1`.
3. Reprendre la comparaison depuis la droite : à l’alignement `0`, comparer `N` du texte avec `A` du motif, puis calculer le décalage `1`.
4. Traiter le cas limite `motif absent`.
5. Relier la réponse à T-ALGO-05.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
