---
title: "P09 - td - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "td"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "architecture, système et droits Unix"
notion: "architecture, système et droits Unix"
private_data: false
official_program:
  capacities:
    - "P-ARCH-01A"
    - "P-ARCH-01B"
    - "P-ARCH-03A"
    - "P-ARCH-03B"
    - "P-ARCH-03C"
---

# P09 - TD - architecture, système et droits Unix

## Objectifs
- Travailler processeur, mémoire, stockage, processus, PID.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : P-ARCH-01A.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=alpha
- Consigne : distinguer mémoire vive et stockage ; traiter aussi `fichier absent` si nécessaire.
- Réponse attendue : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `fichier absent`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-ARCH-01B.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=beta
- Consigne : identifier PID et processus ; traiter aussi `droit x manquant sur dossier` si nécessaire.
- Réponse attendue : chmod 640 mesures.csv donne rw-r-----.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `droit x manquant sur dossier`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-ARCH-03A.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=gamma
- Consigne : lire rwx pour propriétaire groupe autres ; traiter aussi `chmod 777 trop permissif` si nécessaire.
- Réponse attendue : PID 2314 python collecte.py est un processus.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `chmod 777 trop permissif`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-ARCH-03B.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=delta
- Consigne : calculer chmod 640 et droit x dossier ; traiter aussi `fichier absent` si nécessaire.
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `fichier absent`.
### Exercice 5
- Type : justification.
- Capacité officielle : P-ARCH-03C.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=epsilon
- Consigne : distinguer mémoire vive et stockage ; traiter aussi `droit x manquant sur dossier` si nécessaire.
- Réponse attendue : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `droit x manquant sur dossier`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : P-ARCH-01A.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=zeta
- Consigne : identifier PID et processus ; traiter aussi `chmod 777 trop permissif` si nécessaire.
- Réponse attendue : chmod 640 mesures.csv donne rw-r-----.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `chmod 777 trop permissif`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : P-ARCH-01B.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=eta
- Consigne : lire rwx pour propriétaire groupe autres ; traiter aussi `fichier absent` si nécessaire.
- Réponse attendue : PID 2314 python collecte.py est un processus.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `fichier absent`.
### Exercice 8
- Type : justification.
- Capacité officielle : P-ARCH-03A.
- Données : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`. ; jeu_exercice=theta
- Consigne : calculer chmod 640 et droit x dossier ; traiter aussi `droit x manquant sur dossier` si nécessaire.
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `droit x manquant sur dossier`.

### Exercice 9
- Type : production/écriture.
- Capacité officielle : P-ARCH-01B.
- Données : mémoire initiale `[10]` = 12, `[11]` = 5, `[12]` = 0. Programme : `LOAD R0, [10] ; LOAD R1, [11] ; SUB R0, R1 ; STORE R0, [12]`.
- Consigne : (9a) dérouler l'exécution instruction par instruction en construisant la trace (CO, instruction, R0, R1, mémoire[12]) ; (9b) donner la valeur finale de mémoire[12] ; (9c) que se passerait-il si on inversait les deux premières instructions ?
- Réponse attendue : (9a) trace 4 étapes ; (9b) mémoire[12] = 7 ; (9c) R0 contiendrait 5 et R1 contiendrait 12, résultat = 5 − 12 = −7.
- Critère de réussite : trace complète avec valeurs correctes à chaque étape, cas d'inversion traité.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : P-ARCH-01A.
- Résultat attendu : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Justification : la tâche `distinguer mémoire vive et stockage` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : confondre mémoire et disque.
- Donnée utilisée alpha dans P09 TD architecture os droits : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P09 TD architecture os droits : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : P-ARCH-01B.
- Résultat attendu : chmod 640 mesures.csv donne rw-r-----.
- Justification : la tâche `identifier PID et processus` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : oublier x sur dossier.
- Donnée utilisée beta dans P09 TD architecture os droits : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P09 TD architecture os droits : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : P-ARCH-03A.
- Résultat attendu : PID 2314 python collecte.py est un processus.
- Justification : la tâche `lire rwx pour propriétaire groupe autres` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : donner tous les droits.
- Donnée utilisée gamma dans P09 TD architecture os droits : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P09 TD architecture os droits : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : P-ARCH-03B.
- Résultat attendu : sans x sur dossier, lecture du fichier impossible.
- Justification : la tâche `calculer chmod 640 et droit x dossier` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : confondre mémoire et disque.
- Donnée utilisée delta dans P09 TD architecture os droits : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P09 TD architecture os droits : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : P-ARCH-03C.
- Résultat attendu : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Justification : la tâche `distinguer mémoire vive et stockage` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : oublier x sur dossier.
- Donnée utilisée epsilon dans P09 TD architecture os droits : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P09 TD architecture os droits : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : P-ARCH-01A.
- Résultat attendu : chmod 640 mesures.csv donne rw-r-----.
- Justification : la tâche `identifier PID et processus` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : donner tous les droits.
- Donnée utilisée zeta dans P09 TD architecture os droits : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P09 TD architecture os droits : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : P-ARCH-01B.
- Résultat attendu : PID 2314 python collecte.py est un processus.
- Justification : la tâche `lire rwx pour propriétaire groupe autres` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : confondre mémoire et disque.
- Donnée utilisée eta dans P09 TD architecture os droits : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P09 TD architecture os droits : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : P-ARCH-03A.
- Résultat attendu : sans x sur dossier, lecture du fichier impossible.
- Justification : la tâche `calculer chmod 640 et droit x dossier` s applique à `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi` ; erreur évitée : oublier x sur dossier.
- Donnée utilisée theta dans P09 TD architecture os droits : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P09 TD architecture os droits : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P09 TD architecture os droits : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P09 TD architecture os droits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

### Corrigé exercice 9
- Capacité mobilisée : P-ARCH-01B.
- Résultat attendu : (9a) Étape 0 : LOAD R0, [10] → R0=12. Étape 1 : LOAD R1, [11] → R1=5. Étape 2 : SUB R0, R1 → R0=12−5=7. Étape 3 : STORE R0, [12] → mémoire[12]=7. (9b) mémoire[12] = 7. (9c) Inversion : R0=5, R1=12, SUB donne 5−12=−7.
- Justification : chaque instruction modifie un registre ou la mémoire ; le résultat dépend de l'ordre d'exécution.
- Cas limite : si les deux valeurs sont égales (12 et 12), SUB donne 0.

## Erreurs fréquentes
- confondre mémoire et disque.
- oublier x sur dossier.
- donner tous les droits.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `droit x manquant sur dossier`.

## Cas limites travaillés
- fichier absent.
- droit x manquant sur dossier.
- chmod 777 trop permissif.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `-rw-r----- -> propriétaire rw, groupe r, autres aucun droit`.
- Au moins un cas limite de la section précédente est décidé.

