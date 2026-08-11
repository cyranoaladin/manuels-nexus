---
title: "T11 - td - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "td"
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

# T11 - TD - SoC, processus, ordonnancement et interblocage

## Objectifs
- Travailler système sur puce, processus, état prêt, état bloqué, ordonnancement.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-01.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=alpha
- Consigne : identifier CPU mémoire interfaces ; traiter aussi `un seul processus prêt` si nécessaire.
- Réponse attendue : P1 20 ms, P2 20 ms, P1 20 ms.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `un seul processus prêt`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ARCH-02A.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=beta
- Consigne : décrire création de processus ; traiter aussi `ressource libérée avant attente` si nécessaire.
- Réponse attendue : P1 attend journal et P2 attend camera.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `ressource libérée avant attente`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ARCH-02B.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=gamma
- Consigne : simuler round-robin ; traiter aussi `processus bloqué` si nécessaire.
- Réponse attendue : CPU + mémoire + contrôleur caméra intégrés.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `processus bloqué`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ARCH-02C.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=delta
- Consigne : détecter attente circulaire ; traiter aussi `un seul processus prêt` si nécessaire.
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `un seul processus prêt`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ARCH-01.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=epsilon
- Consigne : identifier CPU mémoire interfaces ; traiter aussi `ressource libérée avant attente` si nécessaire.
- Réponse attendue : P1 20 ms, P2 20 ms, P1 20 ms.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `ressource libérée avant attente`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-02A.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=zeta
- Consigne : décrire création de processus ; traiter aussi `processus bloqué` si nécessaire.
- Réponse attendue : P1 attend journal et P2 attend camera.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `processus bloqué`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ARCH-02B.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=eta
- Consigne : simuler round-robin ; traiter aussi `un seul processus prêt` si nécessaire.
- Réponse attendue : CPU + mémoire + contrôleur caméra intégrés.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `un seul processus prêt`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ARCH-02C.
- Données : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`. ; jeu_exercice=theta
- Consigne : détecter attente circulaire ; traiter aussi `ressource libérée avant attente` si nécessaire.
- Réponse attendue : processus bloqué ne consomme pas CPU.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `ressource libérée avant attente`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ARCH-01.
- Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
- Justification : la tâche `identifier CPU mémoire interfaces` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : programme confondu avec processus.
- Donnée utilisée alpha dans T11 TD processus ordonnancement interblocage : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ARCH-02A.
- Résultat attendu : P1 attend journal et P2 attend camera.
- Justification : la tâche `décrire création de processus` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : bloqué confondu avec terminé.
- Donnée utilisée beta dans T11 TD processus ordonnancement interblocage : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ARCH-02B.
- Résultat attendu : CPU + mémoire + contrôleur caméra intégrés.
- Justification : la tâche `simuler round-robin` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : ordre des verrous oublié.
- Donnée utilisée gamma dans T11 TD processus ordonnancement interblocage : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ARCH-02C.
- Résultat attendu : processus bloqué ne consomme pas CPU.
- Justification : la tâche `détecter attente circulaire` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : programme confondu avec processus.
- Donnée utilisée delta dans T11 TD processus ordonnancement interblocage : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ARCH-01.
- Résultat attendu : P1 20 ms, P2 20 ms, P1 20 ms.
- Justification : la tâche `identifier CPU mémoire interfaces` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : bloqué confondu avec terminé.
- Donnée utilisée epsilon dans T11 TD processus ordonnancement interblocage : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ARCH-02A.
- Résultat attendu : P1 attend journal et P2 attend camera.
- Justification : la tâche `décrire création de processus` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : ordre des verrous oublié.
- Donnée utilisée zeta dans T11 TD processus ordonnancement interblocage : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ARCH-02B.
- Résultat attendu : CPU + mémoire + contrôleur caméra intégrés.
- Justification : la tâche `simuler round-robin` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : programme confondu avec processus.
- Donnée utilisée eta dans T11 TD processus ordonnancement interblocage : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ARCH-02C.
- Résultat attendu : processus bloqué ne consomme pas CPU.
- Justification : la tâche `détecter attente circulaire` s applique à `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms` ; erreur évitée : bloqué confondu avec terminé.
- Donnée utilisée theta dans T11 TD processus ordonnancement interblocage : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T11 TD processus ordonnancement interblocage : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T11 TD processus ordonnancement interblocage : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T11 TD processus ordonnancement interblocage : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `ressource libérée avant attente`.

## Cas limites travaillés
- un seul processus prêt.
- ressource libérée avant attente.
- processus bloqué.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `P1 20 ms, P2 20 ms, P1 20 ms`.
- Au moins un cas limite de la section précédente est décidé.

