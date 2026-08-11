---
title: "T11 - tp_papier - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "tp_papier"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "SoC, processus, ordonnancement et interblocage"
notion: "SoC, processus, ordonnancement et interblocage"
private_data: false
official_program:
  capacities:
    - "T-ARCH-01"
    - "T-ARCH-02A"
    - "T-ARCH-02B"
    - "T-ARCH-02C"
---

# T11 - TP - SoC, processus, ordonnancement et interblocage

## Statut du TP
TP papier : ce support n attend aucune ressource Python ; le livrable est une trace écrite vérifiable.

## Donnée fournie
`P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : identifier CPU mémoire interfaces.
3. Réaliser : décrire création de processus.
4. Tester le cas limite `un seul processus prêt`.
5. Produire le livrable : P1 20 ms, P2 20 ms, P1 20 ms.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `P1 20 ms, P2 20 ms, P1 20 ms`.
- 2 points : cas limite `un seul processus prêt`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
### Corrigé question 2
Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
### Corrigé question 3
Résultat attendu : trace `P1 attend journal`, `P2 attend camera` ; cycle d attente `P1 -> P2 -> P1`, interblocage.
### Corrigé question 4
Résultat attendu : `un seul processus prêt` traité sans ambiguïté.

## Liens
- TD lié : `T11_TD_processus_ordonnancement_interblocage.md`.
- Évaluation liée : `T11_evaluation_processus_ordonnancement_interblocage.md`.

## Cas limites travaillés
- un seul processus prêt.
- ressource libérée avant attente.
- processus bloqué.

## Erreurs fréquentes
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `P1 20 ms, P2 20 ms, P1 20 ms`.
- Au moins un cas limite de la section précédente est décidé.

