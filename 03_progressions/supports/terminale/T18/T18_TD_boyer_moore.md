---
title: "T18 - td - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - TD - Boyer-Moore

## Objectifs
- Travailler motif, texte, table du mauvais caractère, comparaison droite à gauche, décalage.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=alpha
- Consigne : prétraiter dernière position de chaque caractère ; traiter aussi `motif absent` si nécessaire.
- Réponse attendue : table : A->2, N->1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif absent`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=beta
- Consigne : comparer depuis la droite ; traiter aussi `motif plus long que texte` si nécessaire.
- Réponse attendue : alignement 0 : N comparé à A -> décalage 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif plus long que texte`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=gamma
- Consigne : calculer max(1, j - dernière_position) ; traiter aussi `caractère absent du motif` si nécessaire.
- Réponse attendue : alignement 1 : ANA trouvé à l'indice 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `caractère absent du motif`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=delta
- Consigne : comparer avec recherche naïve ; traiter aussi `motif absent` si nécessaire.
- Réponse attendue : motif XYZ absent.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif absent`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=epsilon
- Consigne : prétraiter dernière position de chaque caractère ; traiter aussi `motif plus long que texte` si nécessaire.
- Réponse attendue : table : A->2, N->1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif plus long que texte`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=zeta
- Consigne : comparer depuis la droite ; traiter aussi `caractère absent du motif` si nécessaire.
- Réponse attendue : alignement 0 : N comparé à A -> décalage 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `caractère absent du motif`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=eta
- Consigne : calculer max(1, j - dernière_position) ; traiter aussi `motif absent` si nécessaire.
- Réponse attendue : alignement 1 : ANA trouvé à l'indice 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif absent`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ALGO-05.
- Données : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`. ; jeu_exercice=theta
- Consigne : comparer avec recherche naïve ; traiter aussi `motif plus long que texte` si nécessaire.
- Réponse attendue : motif XYZ absent.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `motif plus long que texte`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : table : A->2, N->1.
- Justification : la tâche `prétraiter dernière position de chaque caractère` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : comparaison gauche à droite.
- Donnée utilisée alpha dans T18 TD boyer moore : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T18 TD boyer moore : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : alignement 0 : N comparé à A -> décalage 1.
- Justification : la tâche `comparer depuis la droite` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : décalage nul.
- Donnée utilisée beta dans T18 TD boyer moore : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T18 TD boyer moore : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : alignement 1 : ANA trouvé à l'indice 1.
- Justification : la tâche `calculer max(1, j - dernière_position)` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : caractère absent oublié.
- Donnée utilisée gamma dans T18 TD boyer moore : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T18 TD boyer moore : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : motif XYZ absent.
- Justification : la tâche `comparer avec recherche naïve` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : comparaison gauche à droite.
- Donnée utilisée delta dans T18 TD boyer moore : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T18 TD boyer moore : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : table : A->2, N->1.
- Justification : la tâche `prétraiter dernière position de chaque caractère` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : décalage nul.
- Donnée utilisée epsilon dans T18 TD boyer moore : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T18 TD boyer moore : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : alignement 0 : N comparé à A -> décalage 1.
- Justification : la tâche `comparer depuis la droite` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : caractère absent oublié.
- Donnée utilisée zeta dans T18 TD boyer moore : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T18 TD boyer moore : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : alignement 1 : ANA trouvé à l'indice 1.
- Justification : la tâche `calculer max(1, j - dernière_position)` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : comparaison gauche à droite.
- Donnée utilisée eta dans T18 TD boyer moore : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T18 TD boyer moore : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ALGO-05.
- Résultat attendu : motif XYZ absent.
- Justification : la tâche `comparer avec recherche naïve` s applique à `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1` ; erreur évitée : décalage nul.
- Donnée utilisée theta dans T18 TD boyer moore : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T18 TD boyer moore : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T18 TD boyer moore : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T18 TD boyer moore : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- comparaison gauche à droite.
- décalage nul.
- caractère absent oublié.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `motif plus long que texte`.

## Cas limites travaillés
- motif absent.
- motif plus long que texte.
- caractère absent du motif.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `table : A->2, N->1`.
- Au moins un cas limite de la section précédente est décidé.

