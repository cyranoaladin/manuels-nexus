---
title: "P11 - td - parcours, recherche, extremum et moyenne"
level: "premiere"
sequence_id: "P11"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "parcours, recherche, extremum et moyenne"
notion: "parcours, recherche, extremum et moyenne"
private_data: false
official_program:
  capacities:
    - "P-ALGO-01A"
    - "P-ALGO-01B"
---

# P11 - TD - parcours, recherche, extremum et moyenne

## Objectifs
- Travailler parcours linéaire, recherche occurrence, premier indice, maximum, minimum.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-01A.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=alpha
- Consigne : parcourir avec indice ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : première occurrence de 21 -> indice 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ALGO-01B.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=beta
- Consigne : mémoriser le premier indice de 21 ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : maximum -> 24.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cible absente`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-ALGO-01A.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=gamma
- Consigne : initialiser maximum à la première valeur ; traiter aussi `doublon de 21` si nécessaire.
- Réponse attendue : somme=101, len=5, moyenne=20.2.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon de 21`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-ALGO-01B.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=delta
- Consigne : tester liste vide avant moyenne ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : liste vide -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 5
- Type : justification.
- Capacité officielle : P-ALGO-01A.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=epsilon
- Consigne : parcourir avec indice ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : première occurrence de 21 -> indice 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cible absente`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-01B.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=zeta
- Consigne : mémoriser le premier indice de 21 ; traiter aussi `doublon de 21` si nécessaire.
- Réponse attendue : maximum -> 24.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `doublon de 21`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : P-ALGO-01A.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=eta
- Consigne : initialiser maximum à la première valeur ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : somme=101, len=5, moyenne=20.2.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 8
- Type : justification.
- Capacité officielle : P-ALGO-01B.
- Données : `mesures=[18,21,17,24,21], cible=21, seuil=22`. ; jeu_exercice=theta
- Consigne : tester liste vide avant moyenne ; traiter aussi `cible absente` si nécessaire.
- Réponse attendue : liste vide -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cible absente`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : P-ALGO-01A.
- Résultat attendu : première occurrence de 21 -> indice 1.
- Justification : la tâche `parcourir avec indice` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : maximum initialisé à 0.
- Donnée utilisée alpha dans P11 TD parcours recherche extremum moyenne : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : P-ALGO-01B.
- Résultat attendu : maximum -> 24.
- Justification : la tâche `mémoriser le premier indice de 21` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : division par len sans test.
- Donnée utilisée beta dans P11 TD parcours recherche extremum moyenne : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : P-ALGO-01A.
- Résultat attendu : somme=101, len=5, moyenne=20.2.
- Justification : la tâche `initialiser maximum à la première valeur` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : indice changé après première occurrence.
- Donnée utilisée gamma dans P11 TD parcours recherche extremum moyenne : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : P-ALGO-01B.
- Résultat attendu : liste vide -> ValueError.
- Justification : la tâche `tester liste vide avant moyenne` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : maximum initialisé à 0.
- Donnée utilisée delta dans P11 TD parcours recherche extremum moyenne : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : P-ALGO-01A.
- Résultat attendu : première occurrence de 21 -> indice 1.
- Justification : la tâche `parcourir avec indice` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : division par len sans test.
- Donnée utilisée epsilon dans P11 TD parcours recherche extremum moyenne : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : P-ALGO-01B.
- Résultat attendu : maximum -> 24.
- Justification : la tâche `mémoriser le premier indice de 21` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : indice changé après première occurrence.
- Donnée utilisée zeta dans P11 TD parcours recherche extremum moyenne : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : P-ALGO-01A.
- Résultat attendu : somme=101, len=5, moyenne=20.2.
- Justification : la tâche `initialiser maximum à la première valeur` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : maximum initialisé à 0.
- Donnée utilisée eta dans P11 TD parcours recherche extremum moyenne : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : P-ALGO-01B.
- Résultat attendu : liste vide -> ValueError.
- Justification : la tâche `tester liste vide avant moyenne` s applique à `mesures=[18,21,17,24,21], cible=21, seuil=22` ; erreur évitée : division par len sans test.
- Donnée utilisée theta dans P11 TD parcours recherche extremum moyenne : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P11 TD parcours recherche extremum moyenne : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P11 TD parcours recherche extremum moyenne : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P11 TD parcours recherche extremum moyenne : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- maximum initialisé à 0.
- division par len sans test.
- indice changé après première occurrence.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `cible absente`.

## Cas limites travaillés
- liste vide.
- cible absente.
- doublon de 21.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première occurrence de 21 -> indice 1`.
- Au moins un cas limite de la section précédente est décidé.

