---
title: "T08 - td - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "BFS, DFS, cycles et chemins"
notion: "BFS, DFS, cycles et chemins"
private_data: false
official_program:
  capacities:
    - "T-ALGO-02A"
    - "T-ALGO-02B"
    - "T-ALGO-02C"
    - "T-ALGO-02D"
---

# T08 - TD - BFS, DFS, cycles et chemins

## Objectifs
- Travailler BFS avec file, DFS avec pile, marquage, prédécesseurs, chemin reconstruit.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-02A.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=alpha
- Consigne : BFS file A puis B,C puis D,E ; traiter aussi `sommet isolé F` si nécessaire.
- Réponse attendue : BFS -> A,B,C,D,E.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé F`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-ALGO-02B.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=beta
- Consigne : mémoriser prédécesseurs ; traiter aussi `destination absente` si nécessaire.
- Réponse attendue : prédécesseurs E<-C<-A donc chemin A-C-E.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `destination absente`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-ALGO-02C.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=gamma
- Consigne : DFS explore un chemin avant retour ; traiter aussi `cycle D-C-D` si nécessaire.
- Réponse attendue : F isolé -> aucun chemin.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cycle D-C-D`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-ALGO-02D.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=delta
- Consigne : détecter cycle par sommet gris ; traiter aussi `sommet isolé F` si nécessaire.
- Réponse attendue : complexité O(V+E).
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé F`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-ALGO-02A.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=epsilon
- Consigne : BFS file A puis B,C puis D,E ; traiter aussi `destination absente` si nécessaire.
- Réponse attendue : BFS -> A,B,C,D,E.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `destination absente`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-ALGO-02B.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=zeta
- Consigne : mémoriser prédécesseurs ; traiter aussi `cycle D-C-D` si nécessaire.
- Réponse attendue : prédécesseurs E<-C<-A donc chemin A-C-E.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `cycle D-C-D`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-ALGO-02C.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=eta
- Consigne : DFS explore un chemin avant retour ; traiter aussi `sommet isolé F` si nécessaire.
- Réponse attendue : F isolé -> aucun chemin.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `sommet isolé F`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-ALGO-02D.
- Données : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`. ; jeu_exercice=theta
- Consigne : détecter cycle par sommet gris ; traiter aussi `destination absente` si nécessaire.
- Réponse attendue : complexité O(V+E).
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `destination absente`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-ALGO-02A.
- Résultat attendu : BFS -> A,B,C,D,E.
- Justification : la tâche `BFS file A puis B,C puis D,E` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : marquage trop tardif.
- Donnée utilisée alpha dans T08 TD bfs dfs cycles chemins : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-ALGO-02B.
- Résultat attendu : prédécesseurs E<-C<-A donc chemin A-C-E.
- Justification : la tâche `mémoriser prédécesseurs` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : BFS confondu avec DFS.
- Donnée utilisée beta dans T08 TD bfs dfs cycles chemins : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-ALGO-02C.
- Résultat attendu : F isolé -> aucun chemin.
- Justification : la tâche `DFS explore un chemin avant retour` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : prédécesseurs oubliés.
- Donnée utilisée gamma dans T08 TD bfs dfs cycles chemins : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-ALGO-02D.
- Résultat attendu : complexité O(V+E).
- Justification : la tâche `détecter cycle par sommet gris` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : marquage trop tardif.
- Donnée utilisée delta dans T08 TD bfs dfs cycles chemins : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-ALGO-02A.
- Résultat attendu : BFS -> A,B,C,D,E.
- Justification : la tâche `BFS file A puis B,C puis D,E` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : BFS confondu avec DFS.
- Donnée utilisée epsilon dans T08 TD bfs dfs cycles chemins : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-ALGO-02B.
- Résultat attendu : prédécesseurs E<-C<-A donc chemin A-C-E.
- Justification : la tâche `mémoriser prédécesseurs` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : prédécesseurs oubliés.
- Donnée utilisée zeta dans T08 TD bfs dfs cycles chemins : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-ALGO-02C.
- Résultat attendu : F isolé -> aucun chemin.
- Justification : la tâche `DFS explore un chemin avant retour` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : marquage trop tardif.
- Donnée utilisée eta dans T08 TD bfs dfs cycles chemins : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-ALGO-02D.
- Résultat attendu : complexité O(V+E).
- Justification : la tâche `détecter cycle par sommet gris` s applique à `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` ; erreur évitée : BFS confondu avec DFS.
- Donnée utilisée theta dans T08 TD bfs dfs cycles chemins : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T08 TD bfs dfs cycles chemins : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T08 TD bfs dfs cycles chemins : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T08 TD bfs dfs cycles chemins : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `destination absente`.

## Cas limites travaillés
- sommet isolé F.
- destination absente.
- cycle D-C-D.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `BFS -> A,B,C,D,E`.
- Au moins un cas limite de la section précédente est décidé.

