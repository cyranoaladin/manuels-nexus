---
title: "T11 - evaluation - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "evaluation"
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

# T11 - Évaluation - SoC, processus, ordonnancement et interblocage

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C.

## Questions
### Question 1
- Capacité officielle : T-ARCH-01.
- Énoncé : à partir de `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`, identifier CPU mémoire interfaces.
- Réponse attendue : P1 20 ms, P2 20 ms, P1 20 ms.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `un seul processus prêt`.
### Question 2
- Capacité officielle : T-ARCH-02A.
- Énoncé : à partir de `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`, décrire création de processus.
- Réponse attendue : P1 attend journal et P2 attend camera.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `ressource libérée avant attente`.
### Question 3
- Capacité officielle : T-ARCH-02B.
- Énoncé : à partir de `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`, simuler round-robin.
- Réponse attendue : CPU + mémoire + contrôleur caméra intégrés.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `processus bloqué`.
### Question 4
- Capacité officielle : T-ARCH-02C.
- Énoncé : à partir de `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`, détecter attente circulaire.
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `un seul processus prêt`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
- Critère spécifique : identifier CPU mémoire interfaces et éviter `programme confondu avec processus`.
### Corrigé question 2
- Résultat attendu : P1 attend journal et P2 attend camera.
- Critère spécifique : décrire création de processus et éviter `bloqué confondu avec terminé`.
### Corrigé question 3
- Résultat attendu : CPU + mémoire + contrôleur caméra intégrés.
- Critère spécifique : simuler round-robin et éviter `ordre des verrous oublié`.
### Corrigé question 4
- Résultat attendu : processus bloqué ne consomme pas CPU.
- Critère spécifique : détecter attente circulaire et éviter `programme confondu avec processus`.

## Erreurs fréquentes et remédiation
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Cas limites travaillés
- un seul processus prêt.
- ressource libérée avant attente.
- processus bloqué.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `P1 20 ms, P2 20 ms, P1 20 ms`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T11 sur `processus_ordonnancement_interblocage`.

## Aménagement
- Version aménagée : `T11_version_amenagee_processus_ordonnancement_interblocage.md` ; consignes découpées et barème conservé.
