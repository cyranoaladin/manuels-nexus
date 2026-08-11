---
title: "P13 - tp_papier - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "tp_papier"
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

# P13 - TP - dichotomie, glouton et k-NN

## Statut du TP
TP papier : ce support n attend aucune ressource Python ; le livrable est une trace écrite vérifiable.

## Donnée fournie
`tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : calculer milieu puis réduire intervalle.
3. Réaliser : montrer que V = droite − gauche + 1 décroît strictement.
4. Tester le cas limite `cible absente`.
5. Produire le livrable : milieux 18 puis 37 -> trouvé indice 4.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `milieux 18 puis 37 -> trouvé indice 4`.
- 2 points : cas limite `cible absente`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
### Corrigé question 2
Résultat attendu : milieux 18 puis 37 -> trouvé indice 4.
### Corrigé question 3
Résultat attendu : V = droite − gauche + 1 décroît strictement à chaque itération : V passe de 6 à 3 (milieu=18, cible>18, on réduit à droite) puis de 3 à 1 (milieu=37, cible trouvée). La décroissance stricte de V garantit la terminaison.
### Corrigé question 4
Résultat attendu : `cible absente` traité sans ambiguïté.

## Liens
- TD lié : `P13_TD_dichotomie_glouton_knn.md`.
- Évaluation liée : `P13_evaluation_dichotomie_glouton_knn.md`.

## Cas limites travaillés
- cible absente.
- pièce 1 absente.
- égalité de vote.

## Erreurs fréquentes
- dichotomie sur liste non triée.
- glouton supposé toujours optimal.
- égalité k-NN non décidée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `milieux 18 puis 37 -> trouvé indice 4`.
- Au moins un cas limite de la section précédente est décidé.

