---
title: "T06 - td - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - TD - arbres binaires de recherche

## Objectifs
- Travailler invariant ABR, recherche, insertion, parcours infixe, arbre vide.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-01E.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=alpha
- Consigne : comparer à la racine ; traiter aussi `arbre vide` si nécessaire.
- Réponse attendue : chercher 6 : 8 -> 3 -> 6.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arbre vide`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ALGO-01F.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=beta
- Consigne : descendre gauche ou droite ; traiter aussi `doublon 6` si nécessaire.
- Réponse attendue : insérer 7 : 8 -> 3 -> 6 -> droite.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon 6`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ALGO-01E.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=gamma
- Consigne : insérer une feuille ; traiter aussi `arbre dégénéré` si nécessaire.
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arbre dégénéré`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ALGO-01F.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=delta
- Consigne : parcours infixe pour clés triées ; traiter aussi `arbre vide` si nécessaire.
- Réponse attendue : arbre vide -> nouvelle racine.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arbre vide`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ALGO-01E.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=epsilon
- Consigne : comparer à la racine ; traiter aussi `doublon 6` si nécessaire.
- Réponse attendue : chercher 6 : 8 -> 3 -> 6.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon 6`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-01F.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=zeta
- Consigne : descendre gauche ou droite ; traiter aussi `arbre dégénéré` si nécessaire.
- Réponse attendue : insérer 7 : 8 -> 3 -> 6 -> droite.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arbre dégénéré`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ALGO-01E.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=eta
- Consigne : insérer une feuille ; traiter aussi `arbre vide` si nécessaire.
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arbre vide`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ALGO-01F.
- Données : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`. ; jeu_exercice=theta
- Consigne : parcours infixe pour clés triées ; traiter aussi `doublon 6` si nécessaire.
- Réponse attendue : arbre vide -> nouvelle racine.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon 6`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ALGO-01E.
- Résultat attendu : chercher 6 : 8 -> 3 -> 6.
- Justification : la tâche `comparer à la racine` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : gauche et droite inversées.
- Donnée utilisée alpha dans T06 TD arbres binaires recherche : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ALGO-01F.
- Résultat attendu : insérer 7 : 8 -> 3 -> 6 -> droite.
- Justification : la tâche `descendre gauche ou droite` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : logarithmique sans équilibre.
- Donnée utilisée beta dans T06 TD arbres binaires recherche : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ALGO-01E.
- Résultat attendu : infixe -> 1,3,6,8,10,14.
- Justification : la tâche `insérer une feuille` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : racine vide oubliée.
- Donnée utilisée gamma dans T06 TD arbres binaires recherche : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ALGO-01F.
- Résultat attendu : arbre vide -> nouvelle racine.
- Justification : la tâche `parcours infixe pour clés triées` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : gauche et droite inversées.
- Donnée utilisée delta dans T06 TD arbres binaires recherche : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ALGO-01E.
- Résultat attendu : chercher 6 : 8 -> 3 -> 6.
- Justification : la tâche `comparer à la racine` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : logarithmique sans équilibre.
- Donnée utilisée epsilon dans T06 TD arbres binaires recherche : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ALGO-01F.
- Résultat attendu : insérer 7 : 8 -> 3 -> 6 -> droite.
- Justification : la tâche `descendre gauche ou droite` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : racine vide oubliée.
- Donnée utilisée zeta dans T06 TD arbres binaires recherche : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ALGO-01E.
- Résultat attendu : infixe -> 1,3,6,8,10,14.
- Justification : la tâche `insérer une feuille` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : gauche et droite inversées.
- Donnée utilisée eta dans T06 TD arbres binaires recherche : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ALGO-01F.
- Résultat attendu : arbre vide -> nouvelle racine.
- Justification : la tâche `parcours infixe pour clés triées` s applique à `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14` ; erreur évitée : logarithmique sans équilibre.
- Donnée utilisée theta dans T06 TD arbres binaires recherche : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T06 TD arbres binaires recherche : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T06 TD arbres binaires recherche : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T06 TD arbres binaires recherche : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- gauche et droite inversées.
- logarithmique sans équilibre.
- racine vide oubliée.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `doublon 6`.

## Cas limites travaillés
- arbre vide.
- doublon 6.
- arbre dégénéré.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `chercher 6 : 8 -> 3 -> 6`.
- Au moins un cas limite de la section précédente est décidé.

