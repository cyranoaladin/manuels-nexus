---
title: "P13 - version_amenagee - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "version_amenagee"
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

# P13 - Version aménagée - dichotomie, glouton et k-NN

## Aides intégrées
- Donnée fournie : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
- Mots utiles : dichotomie, variant V = droite − gauche + 1, glouton, choix local, k-NN.
- Méthode guidée : calculer milieu puis réduire intervalle puis montrer que V = droite − gauche + 1 décroît strictement.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-ALGO-03 ou P-ALGO-04.
3. Compléter le résultat : milieux 18 puis 37 -> trouvé indice 4.
4. Cocher le cas limite : cible absente.

## Réponses rapides
- Réponse 1 : milieux 18 puis 37 -> trouvé indice 4.
- Réponse 2 : 28 -> 10+10+5+2+1.
- Réponse 3 : rouge, bleu, rouge -> classe rouge.
