---
title: "T15 - tp_papier - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "tp_papier"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - TP - calculabilité, programme comme donnée et arrêt

## Statut du TP
TP papier : ce support n attend aucune ressource Python ; le livrable est une trace écrite vérifiable.

## Donnée fournie
`arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : encoder un programme comme texte.
3. Réaliser : raisonner indépendamment de Python.
4. Tester le cas limite `programme très long mais fini`.
5. Produire le livrable : source="print(1)" est une donnée.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `source="print(1)" est une donnée`.
- 2 points : cas limite `programme très long mais fini`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
### Corrigé question 2
Résultat attendu : source="print(1)" est une donnée.
### Corrigé question 3
Résultat attendu : arrete(P,x) renvoie True ou False.
### Corrigé question 4
Résultat attendu : `programme très long mais fini` traité sans ambiguïté.

## Liens
- TD lié : `T15_TD_calculabilite_arret.md`.
- Évaluation liée : `T15_evaluation_calculabilite_arret.md`.

## Cas limites travaillés
- programme très long mais fini.
- langage différent.
- entrée absente.

## Erreurs fréquentes
- non connu confondu avec impossible.
- tests finis comme preuve.
- contradiction oubliée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `source="print(1)" est une donnée`.
- Au moins un cas limite de la section précédente est décidé.

