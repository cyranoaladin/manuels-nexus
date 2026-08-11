---
title: "T11 - corrige - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "corrige"
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

# T11 - Corrigé - SoC, processus, ordonnancement et interblocage

## Corrigé du TD
### Exercice 1
- Réponse attendue : P1 20 ms, P2 20 ms, P1 20 ms.
- Méthode : identifier CPU mémoire interfaces.
- Cas limite : un seul processus prêt.
### Exercice 2
- Réponse attendue : P1 attend journal et P2 attend camera.
- Méthode : décrire création de processus.
- Cas limite : ressource libérée avant attente.
### Exercice 3
- Réponse attendue : CPU + mémoire + contrôleur caméra intégrés.
- Méthode : simuler round-robin.
- Cas limite : processus bloqué.
### Exercice 4
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Méthode : détecter attente circulaire.
- Cas limite : un seul processus prêt.
### Exercice 5
- Réponse attendue : P1 20 ms, P2 20 ms, P1 20 ms.
- Méthode : identifier CPU mémoire interfaces.
- Cas limite : ressource libérée avant attente.
### Exercice 6
- Réponse attendue : P1 attend journal et P2 attend camera.
- Méthode : décrire création de processus.
- Cas limite : processus bloqué.
### Exercice 7
- Réponse attendue : CPU + mémoire + contrôleur caméra intégrés.
- Méthode : simuler round-robin.
- Cas limite : un seul processus prêt.
### Exercice 8
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Méthode : détecter attente circulaire.
- Cas limite : ressource libérée avant attente.

## Corrigé du TP
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Résultat principal : P1 20 ms, P2 20 ms, P1 20 ms.
- Résultat secondaire : P1 attend journal et P2 attend camera.

## Corrigé de l évaluation
- Question 1 : P1 20 ms, P2 20 ms, P1 20 ms.
- Question 2 : P1 attend journal et P2 attend camera.
- Question 3 : CPU + mémoire + contrôleur caméra intégrés.
- Question 4 : processus bloqué ne consomme pas CPU.
