---
title: "P09 - corrige - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "corrige"
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

# P09 - Corrigé - architecture, système et droits Unix

## Corrigé du TD
### Exercice 1
- Réponse attendue : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Méthode : distinguer mémoire vive et stockage.
- Cas limite : fichier absent.
### Exercice 2
- Réponse attendue : chmod 640 mesures.csv donne rw-r-----.
- Méthode : identifier PID et processus.
- Cas limite : droit x manquant sur dossier.
### Exercice 3
- Réponse attendue : PID 2314 python collecte.py est un processus.
- Méthode : lire rwx pour propriétaire groupe autres.
- Cas limite : chmod 777 trop permissif.
### Exercice 4
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Méthode : calculer chmod 640 et droit x dossier.
- Cas limite : fichier absent.
### Exercice 5
- Réponse attendue : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Méthode : distinguer mémoire vive et stockage.
- Cas limite : droit x manquant sur dossier.
### Exercice 6
- Réponse attendue : chmod 640 mesures.csv donne rw-r-----.
- Méthode : identifier PID et processus.
- Cas limite : chmod 777 trop permissif.
### Exercice 7
- Réponse attendue : PID 2314 python collecte.py est un processus.
- Méthode : lire rwx pour propriétaire groupe autres.
- Cas limite : fichier absent.
### Exercice 8
- Réponse attendue : sans x sur dossier, lecture du fichier impossible.
- Méthode : calculer chmod 640 et droit x dossier.
- Cas limite : droit x manquant sur dossier.

### Exercice 9
- Capacité mobilisée : P-ARCH-01B.
- Réponse attendue : trace 4 étapes (LOAD R0=12, LOAD R1=5, SUB R0=7, STORE mémoire[12]=7). Inversion → R0=5, R1=12, résultat −7.
- Méthode : dérouler instruction par instruction en mettant à jour registres et mémoire.
- Cas limite : valeurs égales → SUB donne 0.

## Corrigé du TP
- Donnée : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`.
- Résultat principal : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Résultat secondaire : chmod 640 mesures.csv donne rw-r-----.

## Corrigé de l évaluation
- Question 1 : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Question 2 : chmod 640 mesures.csv donne rw-r-----.
- Question 3 : PID 2314 python collecte.py est un processus.
- Question 4 : sans x sur dossier, lecture du fichier impossible.
