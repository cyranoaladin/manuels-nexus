---
title: "P12 - evaluation - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - Évaluation - tris, invariants et complexité

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D.

## Questions
### Question 1
- Capacité officielle : P-ALGO-02A.
- Énoncé : à partir de `temps=[42,17,23,17,9]`, insérer la clé dans la partie gauche triée.
- Production attendue : une trace qui indique la clé, les décalages et l'état après le premier passage.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.
### Question 2
- Capacité officielle : P-ALGO-02B.
- Énoncé : à partir de `temps=[42,17,23,17,9]`, chercher le minimum du suffixe.
- Production attendue : un tableau qui localise le minimum du suffixe et l'échange éventuel.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste déjà triée`.
### Question 3
- Capacité officielle : P-ALGO-02C.
- Énoncé : à partir de `temps=[42,17,23,17,9]`, écrire invariant gauche triée.
- Production attendue : une phrase d'invariant avec son initialisation et sa conservation.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `doublons 17`.
### Question 4
- Capacité officielle : P-ALGO-02D.
- Énoncé : à partir de `temps=[42,17,23,17,9]`, compter comparaisons intuitives.
- Production attendue : une comparaison qualitative des cas déjà trié, moyen et inverse.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : insertion après i=1 -> [17,42,23,17,9].
- Critère spécifique : insérer la clé dans la partie gauche triée et éviter `invariant confondu avec résultat`.
### Corrigé question 2
- Résultat attendu : sélection place 9 en tête.
- Critère spécifique : chercher le minimum du suffixe et éviter `décalage oublié`.
### Corrigé question 3
- Résultat attendu : invariant : indices < i triés.
- Critère spécifique : écrire invariant gauche triée et éviter `coût linéaire annoncé`.
### Corrigé question 4
- Résultat attendu : pire cas quadratique.
- Critère spécifique : compter comparaisons intuitives et éviter `invariant confondu avec résultat`.

## Erreurs fréquentes et remédiation
- invariant confondu avec résultat.
- décalage oublié.
- coût linéaire annoncé.

## Cas limites travaillés
- liste vide.
- liste déjà triée.
- doublons 17.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code rend vérifiable le placement de la première clé.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P12 sur `tris_invariants_complexite`.

## Aménagement
- Version aménagée : `P12_version_amenagee_tris_invariants_complexite.md` ; consignes découpées et barème conservé.
