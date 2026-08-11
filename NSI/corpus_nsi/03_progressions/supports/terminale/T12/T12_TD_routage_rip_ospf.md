---
title: "T12 - td - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - TD - routage RIP et OSPF

## Objectifs
- Travailler route, RIP, nombre de sauts, OSPF, coût.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=alpha
- Consigne : compter sauts RIP ; traiter aussi `égalité exacte` si nécessaire.
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `égalité exacte`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=beta
- Consigne : additionner coûts OSPF ; traiter aussi `lien indisponible` si nécessaire.
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `lien indisponible`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=gamma
- Consigne : choisir route en égalité documentée ; traiter aussi `route inconnue` si nécessaire.
- Réponse attendue : panne B-D -> A-C-D coût 11.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `route inconnue`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=delta
- Consigne : recalculer après panne ; traiter aussi `égalité exacte` si nécessaire.
- Réponse attendue : route inconnue -> rejet ou défaut.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `égalité exacte`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=epsilon
- Consigne : compter sauts RIP ; traiter aussi `lien indisponible` si nécessaire.
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `lien indisponible`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=zeta
- Consigne : additionner coûts OSPF ; traiter aussi `route inconnue` si nécessaire.
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `route inconnue`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=eta
- Consigne : choisir route en égalité documentée ; traiter aussi `égalité exacte` si nécessaire.
- Réponse attendue : panne B-D -> A-C-D coût 11.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `égalité exacte`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ARCH-03.
- Données : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`. ; jeu_exercice=theta
- Consigne : recalculer après panne ; traiter aussi `lien indisponible` si nécessaire.
- Réponse attendue : route inconnue -> rejet ou défaut.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `lien indisponible`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : RIP : A-B-D et A-C-D ont 2 sauts.
- Justification : la tâche `compter sauts RIP` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : sauts et coûts mélangés.
- Donnée utilisée alpha dans T12 TD routage rip ospf : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T12 TD routage rip ospf : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : OSPF : A-B-D coût 10, A-C-D coût 11.
- Justification : la tâche `additionner coûts OSPF` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : choix visuel.
- Donnée utilisée beta dans T12 TD routage rip ospf : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T12 TD routage rip ospf : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : panne B-D -> A-C-D coût 11.
- Justification : la tâche `choisir route en égalité documentée` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : panne non recalculée.
- Donnée utilisée gamma dans T12 TD routage rip ospf : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T12 TD routage rip ospf : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : route inconnue -> rejet ou défaut.
- Justification : la tâche `recalculer après panne` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : sauts et coûts mélangés.
- Donnée utilisée delta dans T12 TD routage rip ospf : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T12 TD routage rip ospf : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : RIP : A-B-D et A-C-D ont 2 sauts.
- Justification : la tâche `compter sauts RIP` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : choix visuel.
- Donnée utilisée epsilon dans T12 TD routage rip ospf : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T12 TD routage rip ospf : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : OSPF : A-B-D coût 10, A-C-D coût 11.
- Justification : la tâche `additionner coûts OSPF` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : panne non recalculée.
- Donnée utilisée zeta dans T12 TD routage rip ospf : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T12 TD routage rip ospf : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : panne B-D -> A-C-D coût 11.
- Justification : la tâche `choisir route en égalité documentée` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : sauts et coûts mélangés.
- Donnée utilisée eta dans T12 TD routage rip ospf : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T12 TD routage rip ospf : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ARCH-03.
- Résultat attendu : route inconnue -> rejet ou défaut.
- Justification : la tâche `recalculer après panne` s applique à `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9` ; erreur évitée : choix visuel.
- Donnée utilisée theta dans T12 TD routage rip ospf : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T12 TD routage rip ospf : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T12 TD routage rip ospf : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T12 TD routage rip ospf : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- sauts et coûts mélangés.
- choix visuel.
- panne non recalculée.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `lien indisponible`.

## Cas limites travaillés
- égalité exacte.
- lien indisponible.
- route inconnue.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `RIP : A-B-D et A-C-D ont 2 sauts`.
- Au moins un cas limite de la section précédente est décidé.

