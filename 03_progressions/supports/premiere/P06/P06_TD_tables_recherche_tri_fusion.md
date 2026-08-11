---
title: "P06 - td - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "recherche, tri et fusion de tables"
notion: "recherche, tri et fusion de tables"
private_data: false
official_program:
  capacities:
    - "P-TABLE-03"
    - "P-TABLE-04"
---

# P06 - TD - recherche, tri et fusion de tables

## Objectifs
- Travailler recherche dans une table, clé id, doublon id=17, tri stable, tri par clé composée.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : P-TABLE-03.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=alpha
- Consigne : chercher la première ligne id=17 ; traiter aussi `table vide` si nécessaire.
- Réponse attendue : première ligne id=17 -> Ada/robot.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `table vide`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-TABLE-04.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=beta
- Consigne : détecter le doublon id=17 ; traiter aussi `clé id=9 absente` si nécessaire.
- Réponse attendue : doublon id=17 -> Ada/python signalé.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé id=9 absente`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-TABLE-03.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=gamma
- Consigne : trier par (nom, atelier) ; traiter aussi `conflit de clé id=17` si nécessaire.
- Réponse attendue : tri -> Ada/python, Ada/robot, Linus/web.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `conflit de clé id=17`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-TABLE-04.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=delta
- Consigne : fusionner inscriptions et présences ; traiter aussi `table vide` si nécessaire.
- Réponse attendue : fusion -> erreur id_absent=9.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `table vide`.
### Exercice 5
- Type : justification.
- Capacité officielle : P-TABLE-03.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=epsilon
- Consigne : chercher la première ligne id=17 ; traiter aussi `clé id=9 absente` si nécessaire.
- Réponse attendue : première ligne id=17 -> Ada/robot.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé id=9 absente`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : P-TABLE-04.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=zeta
- Consigne : détecter le doublon id=17 ; traiter aussi `conflit de clé id=17` si nécessaire.
- Réponse attendue : doublon id=17 -> Ada/python signalé.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `conflit de clé id=17`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : P-TABLE-03.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=eta
- Consigne : trier par (nom, atelier) ; traiter aussi `table vide` si nécessaire.
- Réponse attendue : tri -> Ada/python, Ada/robot, Linus/web.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `table vide`.
### Exercice 8
- Type : justification.
- Capacité officielle : P-TABLE-04.
- Données : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`. ; jeu_exercice=theta
- Consigne : fusionner inscriptions et présences ; traiter aussi `clé id=9 absente` si nécessaire.
- Réponse attendue : fusion -> erreur id_absent=9.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé id=9 absente`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : P-TABLE-03.
- Résultat attendu : première ligne id=17 -> Ada/robot.
- Justification : la tâche `chercher la première ligne id=17` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : écraser un doublon.
- Donnée utilisée alpha dans P06 TD tables recherche tri fusion : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : P-TABLE-04.
- Résultat attendu : doublon id=17 -> Ada/python signalé.
- Justification : la tâche `détecter le doublon id=17` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : utiliser un indice comme clé.
- Donnée utilisée beta dans P06 TD tables recherche tri fusion : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : P-TABLE-03.
- Résultat attendu : tri -> Ada/python, Ada/robot, Linus/web.
- Justification : la tâche `trier par (nom, atelier)` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : oublier une clé absente.
- Donnée utilisée gamma dans P06 TD tables recherche tri fusion : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : P-TABLE-04.
- Résultat attendu : fusion -> erreur id_absent=9.
- Justification : la tâche `fusionner inscriptions et présences` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : écraser un doublon.
- Donnée utilisée delta dans P06 TD tables recherche tri fusion : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : P-TABLE-03.
- Résultat attendu : première ligne id=17 -> Ada/robot.
- Justification : la tâche `chercher la première ligne id=17` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : utiliser un indice comme clé.
- Donnée utilisée epsilon dans P06 TD tables recherche tri fusion : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : P-TABLE-04.
- Résultat attendu : doublon id=17 -> Ada/python signalé.
- Justification : la tâche `détecter le doublon id=17` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : oublier une clé absente.
- Donnée utilisée zeta dans P06 TD tables recherche tri fusion : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : P-TABLE-03.
- Résultat attendu : tri -> Ada/python, Ada/robot, Linus/web.
- Justification : la tâche `trier par (nom, atelier)` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : écraser un doublon.
- Donnée utilisée eta dans P06 TD tables recherche tri fusion : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : P-TABLE-04.
- Résultat attendu : fusion -> erreur id_absent=9.
- Justification : la tâche `fusionner inscriptions et présences` s applique à `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]` ; erreur évitée : utiliser un indice comme clé.
- Donnée utilisée theta dans P06 TD tables recherche tri fusion : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P06 TD tables recherche tri fusion : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P06 TD tables recherche tri fusion : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P06 TD tables recherche tri fusion : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `clé id=9 absente`.

## Cas limites travaillés
- table vide.
- clé id=9 absente.
- conflit de clé id=17.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première ligne id=17 -> Ada/robot`.
- Au moins un cas limite de la section précédente est décidé.

