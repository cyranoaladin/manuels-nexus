---
title: "P13 - corrige - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "corrige"
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

# P13 - Corrigé - dichotomie, glouton et k-NN

## Corrigé du TD
### Exercice 1
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : milieux 18 puis 37 → trouvé indice 4.
- Méthode : dichotomie.
- Cas limite : cible absente.
### Exercice 2
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : V décroît de 6 à 3 → terminaison.
- Méthode : variant.
- Cas limite : cible absente → V=0.
### Exercice 3
- Capacité mobilisée : P-ALGO-05.
- Réponse attendue : 28=10+10+5+2+1 (5 pièces).
- Méthode : glouton.
- Cas limite : pièce 1 absente.
### Exercice 4
- Capacité mobilisée : P-ALGO-03.
- Réponse attendue : rouge 2 vs bleu 1 → classe rouge.
- Méthode : k-NN vote.
- Cas limite : k pair → égalité.
### Exercice 5
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : V décroît 6→3→1 → cible=23 trouvée indice 3.
- Méthode : variant.
- Cas limite : cible absente → V=0.
### Exercice 6
- Capacité mobilisée : P-ALGO-05.
- Réponse attendue : 13=10+2+1 (3 pièces).
- Méthode : glouton.
- Cas limite : pièce 1 absente → blocage.
### Exercice 7
- Capacité mobilisée : P-ALGO-03.
- Réponse attendue : A(3,2) B(5,4) A(2,3) → vote A=2 B=1 → classe A.
- Méthode : distance euclidienne + vote.
- Cas limite : k=2 → égalité.
### Exercice 8
- Capacité mobilisée : P-ALGO-04.
- Réponse attendue : V décroît 6→3→1→0 → cible=38 absente.
- Méthode : variant.
- Cas limite : V atteint 0.

### Exercice 9
- Capacité mobilisée : P-ALGO-03.
- Données : point cible X(4,3), voisins A1(3,2), B1(5,4), A2(2,3), B2(6,1), A3(1,5).
- Distances euclidiennes : d(X,A1) = sqrt((4-3)²+(3-2)²) = sqrt(2) ≈ 1.41 ; d(X,B1) = sqrt((4-5)²+(3-4)²) = sqrt(2) ≈ 1.41 ; d(X,A2) = sqrt((4-2)²+(3-3)²) = 2.00 ; d(X,B2) = sqrt((4-6)²+(3-1)²) = sqrt(8) ≈ 2.83 ; d(X,A3) = sqrt((4-1)²+(3-5)²) = sqrt(13) ≈ 3.61.
- Tri par distance croissante : A1(1.41), B1(1.41), A2(2.00), B2(2.83), A3(3.61).
- Réponse attendue : k=3 → 3 plus proches = A1, B1, A2 → vote A=2, B=1 → classe "A".
- Méthode : distance euclidienne, tri, vote majoritaire.
- Cas limite : k=2 avec A1 et B1 à distance égale → égalité de vote A=1, B=1 → résultat indéterminé, convention nécessaire (ex. classe du plus proche ou tirage).

## Corrigé du TP
- Donnée dichotomie : `tableau=[4,9,18,23,37,41], cible=37` → trouvé indice 4.
- Donnée glouton : `pièces=[10,5,2,1], montant=28` → 10+10+5+2+1 (5 pièces).
- Donnée k-NN : `voisins=[rouge:1.2, bleu:2.0, rouge:2.4], k=3` → classe rouge.

## Corrigé de l'évaluation
- Question 1 (P-ALGO-04 dichotomie) : valeurs lues aux milieux : 18 puis 37 → cible trouvée à l'indice 4. Cas limite : cible absente → la boucle s'arrête quand gauche > droite.
- Question 2 (P-ALGO-04 variant) : V = droite − gauche + 1 décroît de 6 à 3 → terminaison (cible trouvée). Cas limite : cible=38 absente → V décroît 6→3→1→0, arrêt sans trouver.
- Question 3 (P-ALGO-05 glouton) : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces). Cas limite : sans la pièce 1, montant 28 avec [10,5,2] → le glouton se bloque (reste 1) alors que 28 = 10+10+2+2+2+2 est représentable.
- Question 4 (P-ALGO-03 k-NN) : rouge (2 voix) vs bleu (1 voix) → classe rouge. Cas limite : k pair → égalité de vote possible.
