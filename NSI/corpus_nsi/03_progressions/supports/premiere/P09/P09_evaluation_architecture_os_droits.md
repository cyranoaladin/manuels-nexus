---
title: "P09 - evaluation - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "evaluation"
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

# P09 - Évaluation - architecture, système et droits Unix

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-ARCH-01A, P-ARCH-01B, P-ARCH-03A, P-ARCH-03B, P-ARCH-03C.

## Questions
### Question 1
- Capacité officielle : P-ARCH-01A.
- Énoncé : à partir de `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`, distinguer mémoire vive et stockage.
- Réponse attendue : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `fichier absent`.
### Question 2
- Capacité officielle : P-ARCH-01B.
- Énoncé : à partir de `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`, identifier PID et processus.
- Réponse attendue : chmod 640 mesures.csv donne rw-r-----.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `droit x manquant sur dossier`.
### Question 3
- Capacité officielle : P-ARCH-03A.
- Énoncé : à partir de `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`, lire rwx pour propriétaire groupe autres.
- Réponse attendue : PID 2314 python collecte.py est un processus.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `chmod 777 trop permissif`.
### Question 4
- Capacité officielle : P-ARCH-03B.
- Énoncé : à partir de `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`, calculer chmod 640 et droit x dossier.
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `fichier absent`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Critère spécifique : distinguer mémoire vive et stockage et éviter `confondre mémoire et disque`.
### Corrigé question 2
- Résultat attendu : chmod 640 mesures.csv donne rw-r-----.
- Critère spécifique : identifier PID et processus et éviter `oublier x sur dossier`.
### Corrigé question 3
- Résultat attendu : PID 2314 python collecte.py est un processus.
- Critère spécifique : lire rwx pour propriétaire groupe autres et éviter `donner tous les droits`.
### Corrigé question 4
- Résultat attendu : sans x sur dossier, lecture du fichier impossible.
- Critère spécifique : calculer chmod 640 et droit x dossier et éviter `confondre mémoire et disque`.

## Erreurs fréquentes et remédiation
- confondre mémoire et disque.
- oublier x sur dossier.
- donner tous les droits.

## Cas limites travaillés
- fichier absent.
- droit x manquant sur dossier.
- chmod 777 trop permissif.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `-rw-r----- -> propriétaire rw, groupe r, autres aucun droit`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P09 sur `architecture_os_droits`.

## Aménagement
- Version aménagée : `P09_version_amenagee_architecture_os_droits.md` ; consignes découpées et barème conservé.
