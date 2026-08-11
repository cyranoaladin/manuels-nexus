---
title: "T11 - cours - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "cours"
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

# T11 - Cours - SoC, processus, ordonnancement et interblocage

## Objectifs spécifiques
- Identifier les données utiles de la situation : P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms.
- Employer le vocabulaire : système sur puce, processus, état prêt, état bloqué, ordonnancement, quantum.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-ARCH-01.
- T-ARCH-02A.
- T-ARCH-02B.
- T-ARCH-02C.

## Situation-problème
P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms

## À savoir
- système sur puce.
- processus.
- état prêt.
- état bloqué.
- ordonnancement.
- quantum.
- ressource critique.
- interblocage.

## Méthodes
- identifier CPU mémoire interfaces.
- décrire création de processus.
- simuler round-robin.
- détecter attente circulaire.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : identifier CPU mémoire interfaces.
- Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
- Contrôle : capacité T-ARCH-01 et cas limite `un seul processus prêt`.
### Exemple corrigé 2
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : décrire création de processus.
- Résultat attendu : P1 attend journal et P2 attend camera.
- Contrôle : capacité T-ARCH-02A et cas limite `ressource libérée avant attente`.
### Exemple corrigé 3
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : simuler round-robin.
- Résultat attendu : CPU + mémoire + contrôleur caméra intégrés.
- Contrôle : capacité T-ARCH-02B et cas limite `processus bloqué`.
### Exemple corrigé 4
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Méthode : détecter attente circulaire.
- Résultat attendu : processus bloqué ne consomme pas CPU.
- Contrôle : capacité T-ARCH-02C et cas limite `un seul processus prêt`.

## Cas limites
- un seul processus prêt.
- ressource libérée avant attente.
- processus bloqué.

## Erreurs fréquentes
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Exercices intégrés
1. Identifier les données utiles dans `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
2. Appliquer : identifier CPU mémoire interfaces.
3. Appliquer : décrire création de processus.
4. Décider le cas limite `un seul processus prêt`.

## Critères de réussite observables
- Une capacité parmi T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C est citée et utilisée.
- Le résultat attendu est explicite : P1 20 ms, P2 20 ms, P1 20 ms.
- Le cas limite `ressource libérée avant attente` est tranché.

## Lien avec la progression
- Séance : T11-S1 à T11-S4.
- TD : `T11_TD_processus_ordonnancement_interblocage.md`.
- TP : `T11_tp_processus_ordonnancement_interblocage.md`.
- Évaluation : `T11_evaluation_processus_ordonnancement_interblocage.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur processus et ordonnancement. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : processus, état prêt, état bloqué, ordonnanceur, interblocage, ressource.
- Capacités reliées : T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- tracer l’état d’un processus après une demande de ressource.
- identifier une attente circulaire.
- distinguer processus prêt et processus bloqué.

### Erreurs fréquentes spécifiques
- Un élève peut confondre programme et processus ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier qu’un processus bloqué ne consomme pas le processeur ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut ignorer une ressource déjà tenue ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de processus et ordonnancement.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
