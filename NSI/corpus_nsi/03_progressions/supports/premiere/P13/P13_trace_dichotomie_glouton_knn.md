---
title: "P13 - trace - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "trace"
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

# P13 - Trace - dichotomie, glouton et k-NN

## Trace courte
- Donnée : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
- Vocabulaire : dichotomie, variant V = droite − gauche + 1, glouton, choix local, k-NN.
- Étape 1 : calculer milieu puis réduire intervalle.
- Étape 2 : montrer que V = droite − gauche + 1 décroît strictement.
- Résultat de référence : milieux 18 puis 37 -> trouvé indice 4.

## Cas limites à mémoriser
- cible absente.
- pièce 1 absente.
- égalité de vote.

## Erreurs fréquentes
- dichotomie sur liste non triée.
- glouton supposé toujours optimal.
- égalité k-NN non décidée.

## Critères de réussite observables
- Capacité : P-ALGO-03.
- Résultat final : 28 -> 10+10+5+2+1.
- Cas limite : cible absente.
