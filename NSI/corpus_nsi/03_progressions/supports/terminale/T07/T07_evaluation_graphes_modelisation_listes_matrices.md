---
title: "T07 - evaluation - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "evaluation"
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

# T07 - Évaluation - graphes, listes et matrices

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D.

## Questions
### Question 1
- Capacité officielle : T-STRUCT-05A.
- Énoncé : à partir de `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`, lister voisins sortants.
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `sommet isolé E`.
### Question 2
- Capacité officielle : T-STRUCT-05B.
- Énoncé : à partir de `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`, remplir matrice 0/1.
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `boucle A->A`.
### Question 3
- Capacité officielle : T-STRUCT-05C.
- Énoncé : à partir de `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`, calculer degré sortant.
- Réponse attendue : matrice 4x4 -> 16 cases.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `arête non orientée`.
### Question 4
- Capacité officielle : T-STRUCT-05D.
- Énoncé : à partir de `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`, choisir liste pour graphe peu dense.
- Réponse attendue : sommet E isolé -> liste vide.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `sommet isolé E`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Critère spécifique : lister voisins sortants et éviter `voisin entrant confondu`.
### Corrigé question 2
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Critère spécifique : remplir matrice 0/1 et éviter `sommet isolé oublié`.
### Corrigé question 3
- Résultat attendu : matrice 4x4 -> 16 cases.
- Critère spécifique : calculer degré sortant et éviter `coût mémoire ignoré`.
### Corrigé question 4
- Résultat attendu : sommet E isolé -> liste vide.
- Critère spécifique : choisir liste pour graphe peu dense et éviter `voisin entrant confondu`.

## Erreurs fréquentes et remédiation
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Cas limites travaillés
- sommet isolé E.
- boucle A->A.
- arête non orientée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T07 sur `graphes_modelisation_listes_matrices`.

## Aménagement
- Version aménagée : `T07_version_amenagee_graphes_modelisation_listes_matrices.md` ; consignes découpées et barème conservé.
