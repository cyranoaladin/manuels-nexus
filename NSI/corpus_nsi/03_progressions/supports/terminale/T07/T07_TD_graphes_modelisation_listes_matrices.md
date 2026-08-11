---
title: "T07 - td - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "graphes, listes et matrices"
notion: "graphes, listes et matrices"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-05A"
    - "T-STRUCT-05B"
    - "T-STRUCT-05C"
    - "T-STRUCT-05D"
---

# T07 - TD - graphes, listes et matrices

## Objectifs
- Travailler graphe orienté, graphe non orienté, liste d adjacence, matrice d adjacence, degré.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-STRUCT-05A.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=alpha
- Consigne : lister voisins sortants ; traiter aussi `sommet isolé E` si nécessaire.
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé E`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05B.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=beta
- Consigne : remplir matrice 0/1 ; traiter aussi `boucle A->A` si nécessaire.
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `boucle A->A`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05C.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=gamma
- Consigne : calculer degré sortant ; traiter aussi `arête non orientée` si nécessaire.
- Réponse attendue : matrice 4x4 -> 16 cases.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arête non orientée`.
### Exercice 3bis
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05C.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Consigne : écrire l'implémentation du graphe par liste de successeurs (dictionnaire Python) ; afficher les successeurs de chaque sommet.
- Réponse attendue : `{A: [B, C], B: [D], C: [D], D: [B]}`.
- Critère de réussite : dictionnaire correct, chaque sommet présent, liste de successeurs vérifiable.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-STRUCT-05D.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=delta
- Consigne : choisir liste pour graphe peu dense ; traiter aussi `sommet isolé E` si nécessaire.
- Réponse attendue : sommet E isolé -> liste vide.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé E`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-STRUCT-05A.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=epsilon
- Consigne : lister voisins sortants ; traiter aussi `boucle A->A` si nécessaire.
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `boucle A->A`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-STRUCT-05B.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=zeta
- Consigne : remplir matrice 0/1 ; traiter aussi `arête non orientée` si nécessaire.
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `arête non orientée`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-STRUCT-05C.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=eta
- Consigne : calculer degré sortant ; traiter aussi `sommet isolé E` si nécessaire.
- Réponse attendue : matrice 4x4 -> 16 cases.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé E`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-STRUCT-05D.
- Données : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`. ; jeu_exercice=theta
- Consigne : choisir liste pour graphe peu dense ; traiter aussi `boucle A->A` si nécessaire.
- Réponse attendue : sommet E isolé -> liste vide.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `boucle A->A`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-STRUCT-05A.
- Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Justification : la tâche `lister voisins sortants` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : voisin entrant confondu.
- Donnée utilisée alpha dans T07 TD graphes modelisation listes matrices : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-STRUCT-05B.
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Justification : la tâche `remplir matrice 0/1` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : sommet isolé oublié.
- Donnée utilisée beta dans T07 TD graphes modelisation listes matrices : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-STRUCT-05C.
- Résultat attendu : matrice 4x4 -> 16 cases.
- Justification : la tâche `calculer degré sortant` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : coût mémoire ignoré.
- Donnée utilisée gamma dans T07 TD graphes modelisation listes matrices : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3bis
- Capacité mobilisée : T-STRUCT-05C.
- Résultat attendu : `{A: [B, C], B: [D], C: [D], D: [B]}`.
- Méthode : pour chaque arc (u,v), ajouter v à la liste des successeurs de u.
- Cas limite : sommet sans successeur → liste vide (ici tous les sommets ont au moins un arc sortant).
### Corrigé exercice 4
- Capacité mobilisée : T-STRUCT-05D.
- Résultat attendu : sommet E isolé -> liste vide.
- Justification : la tâche `choisir liste pour graphe peu dense` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : voisin entrant confondu.
- Donnée utilisée delta dans T07 TD graphes modelisation listes matrices : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-STRUCT-05A.
- Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Justification : la tâche `lister voisins sortants` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : sommet isolé oublié.
- Donnée utilisée epsilon dans T07 TD graphes modelisation listes matrices : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-STRUCT-05B.
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Justification : la tâche `remplir matrice 0/1` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : coût mémoire ignoré.
- Donnée utilisée zeta dans T07 TD graphes modelisation listes matrices : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-STRUCT-05C.
- Résultat attendu : matrice 4x4 -> 16 cases.
- Justification : la tâche `calculer degré sortant` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : voisin entrant confondu.
- Donnée utilisée eta dans T07 TD graphes modelisation listes matrices : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-STRUCT-05D.
- Résultat attendu : sommet E isolé -> liste vide.
- Justification : la tâche `choisir liste pour graphe peu dense` s applique à `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]` ; erreur évitée : sommet isolé oublié.
- Donnée utilisée theta dans T07 TD graphes modelisation listes matrices : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T07 TD graphes modelisation listes matrices : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T07 TD graphes modelisation listes matrices : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T07 TD graphes modelisation listes matrices : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `boucle A->A`.

## Cas limites travaillés
- sommet isolé E.
- boucle A->A.
- arête non orientée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- Au moins un cas limite de la section précédente est décidé.

