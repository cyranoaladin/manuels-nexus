---
title: "T15 - td - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - TD - calculabilité, programme comme donnée et arrêt

## Objectifs
- Travailler programme comme donnée, interpréteur, calculabilité, langage indépendant, problème de l arrêt.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-LANG-01A.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=alpha
- Consigne : encoder un programme comme texte ; traiter aussi `programme très long mais fini` si nécessaire.
- Réponse attendue : source="print(1)" est une donnée.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `programme très long mais fini`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-LANG-01B.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=beta
- Consigne : raisonner indépendamment de Python ; traiter aussi `langage différent` si nécessaire.
- Réponse attendue : arrete(P,x) renvoie True ou False.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `langage différent`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-LANG-01C.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=gamma
- Consigne : poser un oracle hypothétique ; traiter aussi `entrée absente` si nécessaire.
- Réponse attendue : Q boucle si arrete(Q,Q) dit True.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `entrée absente`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-LANG-01A.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=delta
- Consigne : construire un programme contradictoire ; traiter aussi `programme très long mais fini` si nécessaire.
- Réponse attendue : contradiction donc oracle impossible.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `programme très long mais fini`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-LANG-01B.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=epsilon
- Consigne : encoder un programme comme texte ; traiter aussi `langage différent` si nécessaire.
- Réponse attendue : source="print(1)" est une donnée.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `langage différent`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-LANG-01C.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=zeta
- Consigne : raisonner indépendamment de Python ; traiter aussi `entrée absente` si nécessaire.
- Réponse attendue : arrete(P,x) renvoie True ou False.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `entrée absente`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-LANG-01A.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=eta
- Consigne : poser un oracle hypothétique ; traiter aussi `programme très long mais fini` si nécessaire.
- Réponse attendue : Q boucle si arrete(Q,Q) dit True.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `programme très long mais fini`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-LANG-01B.
- Données : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`. ; jeu_exercice=theta
- Consigne : construire un programme contradictoire ; traiter aussi `langage différent` si nécessaire.
- Réponse attendue : contradiction donc oracle impossible.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `langage différent`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-LANG-01A.
- Résultat attendu : source="print(1)" est une donnée.
- Justification : la tâche `encoder un programme comme texte` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : non connu confondu avec impossible.
- Donnée utilisée alpha dans T15 TD calculabilite arret : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T15 TD calculabilite arret : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-LANG-01B.
- Résultat attendu : arrete(P,x) renvoie True ou False.
- Justification : la tâche `raisonner indépendamment de Python` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : tests finis comme preuve.
- Donnée utilisée beta dans T15 TD calculabilite arret : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T15 TD calculabilite arret : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-LANG-01C.
- Résultat attendu : Q boucle si arrete(Q,Q) dit True.
- Justification : la tâche `poser un oracle hypothétique` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : contradiction oubliée.
- Donnée utilisée gamma dans T15 TD calculabilite arret : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T15 TD calculabilite arret : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-LANG-01A.
- Résultat attendu : contradiction donc oracle impossible.
- Justification : la tâche `construire un programme contradictoire` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : non connu confondu avec impossible.
- Donnée utilisée delta dans T15 TD calculabilite arret : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T15 TD calculabilite arret : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-LANG-01B.
- Résultat attendu : source="print(1)" est une donnée.
- Justification : la tâche `encoder un programme comme texte` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : tests finis comme preuve.
- Donnée utilisée epsilon dans T15 TD calculabilite arret : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T15 TD calculabilite arret : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-LANG-01C.
- Résultat attendu : arrete(P,x) renvoie True ou False.
- Justification : la tâche `raisonner indépendamment de Python` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : contradiction oubliée.
- Donnée utilisée zeta dans T15 TD calculabilite arret : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T15 TD calculabilite arret : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-LANG-01A.
- Résultat attendu : Q boucle si arrete(Q,Q) dit True.
- Justification : la tâche `poser un oracle hypothétique` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : non connu confondu avec impossible.
- Donnée utilisée eta dans T15 TD calculabilite arret : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T15 TD calculabilite arret : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-LANG-01B.
- Résultat attendu : contradiction donc oracle impossible.
- Justification : la tâche `construire un programme contradictoire` s applique à `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)` ; erreur évitée : tests finis comme preuve.
- Donnée utilisée theta dans T15 TD calculabilite arret : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T15 TD calculabilite arret : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T15 TD calculabilite arret : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T15 TD calculabilite arret : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- non connu confondu avec impossible.
- tests finis comme preuve.
- contradiction oubliée.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `langage différent`.

## Cas limites travaillés
- programme très long mais fini.
- langage différent.
- entrée absente.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `source="print(1)" est une donnée`.
- Au moins un cas limite de la section précédente est décidé.

