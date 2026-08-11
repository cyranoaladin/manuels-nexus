---
title: "T16 - td - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "diviser pour régner et tri fusion"
notion: "diviser pour régner et tri fusion"
private_data: false
official_program:
  capacities:
    - "T-ALGO-03"
---

# T16 - TD - diviser pour régner et tri fusion

## Objectifs
- Travailler diviser pour régner, cas de base, division, récursion, fusion.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=alpha
- Consigne : couper en deux sous-listes ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : division -> [38,12,27] et [12,5,44].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=beta
- Consigne : trier récursivement ; traiter aussi `liste taille 1` si nécessaire.
- Réponse attendue : fusion -> [5,12,12,27,38,44].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste taille 1`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=gamma
- Consigne : fusionner deux listes triées ; traiter aussi `doublons 12` si nécessaire.
- Réponse attendue : cas taille 1 renvoie la liste.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublons 12`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=delta
- Consigne : compter niveaux et comparaisons ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : coût environ n log n.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=epsilon
- Consigne : couper en deux sous-listes ; traiter aussi `liste taille 1` si nécessaire.
- Réponse attendue : division -> [38,12,27] et [12,5,44].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste taille 1`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=zeta
- Consigne : trier récursivement ; traiter aussi `doublons 12` si nécessaire.
- Réponse attendue : fusion -> [5,12,12,27,38,44].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublons 12`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=eta
- Consigne : fusionner deux listes triées ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : cas taille 1 renvoie la liste.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ALGO-03.
- Données : `valeurs=[38,12,27,12,5,44]`. ; jeu_exercice=theta
- Consigne : compter niveaux et comparaisons ; traiter aussi `liste taille 1` si nécessaire.
- Réponse attendue : coût environ n log n.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste taille 1`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : division -> [38,12,27] et [12,5,44].
- Justification : la tâche `couper en deux sous-listes` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : cas de base oublié.
- Donnée utilisée alpha dans T16 TD diviser pour regner tri fusion : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : fusion -> [5,12,12,27,38,44].
- Justification : la tâche `trier récursivement` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : concaténation sans fusion.
- Donnée utilisée beta dans T16 TD diviser pour regner tri fusion : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : cas taille 1 renvoie la liste.
- Justification : la tâche `fusionner deux listes triées` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : coût quadratique annoncé.
- Donnée utilisée gamma dans T16 TD diviser pour regner tri fusion : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : coût environ n log n.
- Justification : la tâche `compter niveaux et comparaisons` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : cas de base oublié.
- Donnée utilisée delta dans T16 TD diviser pour regner tri fusion : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : division -> [38,12,27] et [12,5,44].
- Justification : la tâche `couper en deux sous-listes` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : concaténation sans fusion.
- Donnée utilisée epsilon dans T16 TD diviser pour regner tri fusion : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : fusion -> [5,12,12,27,38,44].
- Justification : la tâche `trier récursivement` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : coût quadratique annoncé.
- Donnée utilisée zeta dans T16 TD diviser pour regner tri fusion : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : cas taille 1 renvoie la liste.
- Justification : la tâche `fusionner deux listes triées` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : cas de base oublié.
- Donnée utilisée eta dans T16 TD diviser pour regner tri fusion : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ALGO-03.
- Résultat attendu : coût environ n log n.
- Justification : la tâche `compter niveaux et comparaisons` s applique à `valeurs=[38,12,27,12,5,44]` ; erreur évitée : concaténation sans fusion.
- Donnée utilisée theta dans T16 TD diviser pour regner tri fusion : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T16 TD diviser pour regner tri fusion : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T16 TD diviser pour regner tri fusion : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T16 TD diviser pour regner tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- cas de base oublié.
- concaténation sans fusion.
- coût quadratique annoncé.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `liste taille 1`.

## Cas limites travaillés
- liste vide.
- liste taille 1.
- doublons 12.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `division -> [38,12,27] et [12,5,44]`.
- Au moins un cas limite de la section précédente est décidé.

