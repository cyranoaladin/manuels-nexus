---
title: "T09 - td - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "bases relationnelles, clés et contraintes"
notion: "bases relationnelles, clés et contraintes"
private_data: false
official_program:
  capacities:
    - "T-BDD-01A"
    - "T-BDD-01B"
    - "T-BDD-01C"
    - "T-BDD-02"
---

# T09 - TD - bases relationnelles, clés et contraintes

## Objectifs
- Travailler relation, attribut, tuple, clé primaire, clé étrangère.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-BDD-01A.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=alpha
- Consigne : identifier schéma et instance ; traiter aussi `clé primaire nulle` si nécessaire.
- Réponse attendue : Livre.id_livre identifie chaque livre.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé primaire nulle`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-BDD-01B.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=beta
- Consigne : vérifier unicité id_livre ; traiter aussi `doublon id_livre=1` si nécessaire.
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon id_livre=1`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-BDD-01C.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=gamma
- Consigne : contrôler Emprunt.id_livre ; traiter aussi `suppression référencée` si nécessaire.
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `suppression référencée`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-BDD-02.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=delta
- Consigne : repérer id_livre=9 absent ; traiter aussi `clé primaire nulle` si nécessaire.
- Réponse attendue : suppression d un livre emprunté refusée.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé primaire nulle`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-BDD-01A.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=epsilon
- Consigne : identifier schéma et instance ; traiter aussi `doublon id_livre=1` si nécessaire.
- Réponse attendue : Livre.id_livre identifie chaque livre.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon id_livre=1`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-BDD-01B.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=zeta
- Consigne : vérifier unicité id_livre ; traiter aussi `suppression référencée` si nécessaire.
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `suppression référencée`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-BDD-01C.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=eta
- Consigne : contrôler Emprunt.id_livre ; traiter aussi `clé primaire nulle` si nécessaire.
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé primaire nulle`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-BDD-02.
- Données : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`. ; jeu_exercice=theta
- Consigne : repérer id_livre=9 absent ; traiter aussi `doublon id_livre=1` si nécessaire.
- Réponse attendue : suppression d un livre emprunté refusée.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon id_livre=1`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-BDD-01A.
- Résultat attendu : Livre.id_livre identifie chaque livre.
- Justification : la tâche `identifier schéma et instance` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : attribut confondu avec valeur.
- Donnée utilisée alpha dans T09 TD bases relationnelles cles contraintes : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-BDD-01B.
- Résultat attendu : Emprunt.id_livre référence Livre.id_livre.
- Justification : la tâche `vérifier unicité id_livre` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : clé étrangère supposée unique.
- Donnée utilisée beta dans T09 TD bases relationnelles cles contraintes : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-BDD-01C.
- Résultat attendu : Emprunt(11,9,Sam) viole la référence.
- Justification : la tâche `contrôler Emprunt.id_livre` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : domaine ignoré.
- Donnée utilisée gamma dans T09 TD bases relationnelles cles contraintes : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-BDD-02.
- Résultat attendu : suppression d un livre emprunté refusée.
- Justification : la tâche `repérer id_livre=9 absent` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : attribut confondu avec valeur.
- Donnée utilisée delta dans T09 TD bases relationnelles cles contraintes : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-BDD-01A.
- Résultat attendu : Livre.id_livre identifie chaque livre.
- Justification : la tâche `identifier schéma et instance` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : clé étrangère supposée unique.
- Donnée utilisée epsilon dans T09 TD bases relationnelles cles contraintes : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-BDD-01B.
- Résultat attendu : Emprunt.id_livre référence Livre.id_livre.
- Justification : la tâche `vérifier unicité id_livre` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : domaine ignoré.
- Donnée utilisée zeta dans T09 TD bases relationnelles cles contraintes : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-BDD-01C.
- Résultat attendu : Emprunt(11,9,Sam) viole la référence.
- Justification : la tâche `contrôler Emprunt.id_livre` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : attribut confondu avec valeur.
- Donnée utilisée eta dans T09 TD bases relationnelles cles contraintes : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-BDD-02.
- Résultat attendu : suppression d un livre emprunté refusée.
- Justification : la tâche `repérer id_livre=9 absent` s applique à `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide` ; erreur évitée : clé étrangère supposée unique.
- Donnée utilisée theta dans T09 TD bases relationnelles cles contraintes : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T09 TD bases relationnelles cles contraintes : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T09 TD bases relationnelles cles contraintes : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T09 TD bases relationnelles cles contraintes : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `doublon id_livre=1`.

## Cas limites travaillés
- clé primaire nulle.
- doublon id_livre=1.
- suppression référencée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `Livre.id_livre identifie chaque livre`.
- Au moins un cas limite de la section précédente est décidé.

