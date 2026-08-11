---
title: "T06 - evaluation - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01A"
    - "T-ALGO-01B"
    - "T-ALGO-01C"
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - Évaluation - arbres binaires de recherche

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ALGO-01A, T-ALGO-01B, T-ALGO-01C, T-ALGO-01E, T-ALGO-01F.

## Questions
### Question 1
- Capacité officielle : T-ALGO-01E.
- Énoncé : à partir de `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`, comparer à la racine.
- Réponse attendue : chercher 6 : 8 -> 3 -> 6.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `arbre vide`.
### Question 2
- Capacité officielle : T-ALGO-01F.
- Énoncé : à partir de `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`, descendre gauche ou droite.
- Réponse attendue : insérer 7 : 8 -> 3 -> 6 -> droite.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `doublon 6`.
### Question 3
- Capacité officielle : T-ALGO-01C.
- Énoncé : à partir de `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`, produire le parcours infixe.
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `arbre dégénéré`.
### Question 4
- Capacité officielle : T-ALGO-01F.
- Énoncé : à partir de `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`, parcours infixe pour clés triées.
- Réponse attendue : arbre vide -> nouvelle racine.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `arbre vide`.

### Question 5
- Capacité officielle : T-ALGO-01A, T-ALGO-01B.
- Énoncé : à partir de l'ABR construit avec `[8, 3, 10, 1, 6, 14]`, calculer la taille (nombre de nœuds) et la hauteur de l'arbre.
- Réponse attendue : taille = 6, hauteur = 2.
- Barème : 1 point taille correcte, 1 point hauteur correcte, 1 point méthode récursive visible, 1 point cas limite arbre vide (taille 0, hauteur -1).

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : chercher 6 : 8 -> 3 -> 6.
- Critère spécifique : comparer à la racine et éviter `gauche et droite inversées`.
### Corrigé question 2
- Résultat attendu : insérer 7 : 8 -> 3 -> 6 -> droite.
- Critère spécifique : descendre gauche ou droite et éviter `logarithmique sans équilibre`.
### Corrigé question 3
- Résultat attendu : infixe -> 1,3,6,8,10,14.
- Critère spécifique : parcours infixe (gauche, racine, droite) et éviter `racine vide oubliée`.
### Corrigé question 4
- Résultat attendu : arbre vide -> nouvelle racine.
- Critère spécifique : parcours infixe pour clés triées et éviter `gauche et droite inversées`.

### Corrigé question 5
- Résultat attendu : taille = 6 (compter récursivement 1 + taille gauche + taille droite), hauteur = 2 (1 + max des hauteurs des sous-arbres).
- Critère spécifique : la récursion distingue le cas de base (nœud vide) et le cas récursif.

## Erreurs fréquentes et remédiation
- gauche et droite inversées.
- logarithmique sans équilibre.
- racine vide oubliée.

## Cas limites travaillés
- arbre vide.
- doublon 6.
- arbre dégénéré.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `chercher 6 : 8 -> 3 -> 6`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 5: 1 point taille correcte, 1 point hauteur correcte, 1 point méthode récursive visible, 1 point cas limite arbre vide.

## Fiche liée
- Fiche liée : fiche de cours T06 sur `arbres_binaires_recherche`.

## Aménagement
- Version aménagée : `T06_version_amenagee_arbres_binaires_recherche.md` ; consignes découpées et barème conservé.
