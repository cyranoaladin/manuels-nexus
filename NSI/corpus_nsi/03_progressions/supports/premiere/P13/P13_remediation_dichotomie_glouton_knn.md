---
title: "P13 - remediation - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "remediation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "dichotomie, glouton et k-NN"
notion: "dichotomie, glouton et k-NN"
private_data: false
official_program:
  capacities:
    - "P-ALGO-03"
    - "P-ALGO-04"
    - "P-ALGO-05"
---

# P13 - Remédiation - dichotomie, glouton et k-NN

## Diagnostic
- dichotomie sur liste non triée.
- glouton supposé toujours optimal.
- égalité k-NN non décidée.

## Activités correctives
1. Annoter `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
2. Refaire la tâche `calculer milieu puis réduire intervalle` et comparer avec `milieux 18 puis 37 -> trouvé indice 4`.
3. Traiter le cas limite `cible absente`.
4. Relier la réponse à P-ALGO-04 (montrer la terminaison de la recherche dichotomique à l'aide d'un variant de boucle).

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
