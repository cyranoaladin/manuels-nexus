---
title: "P09 - trace - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "trace"
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

# P09 - Trace - architecture, système et droits Unix

## Trace courte
- Donnée : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`.
- Vocabulaire : processeur, mémoire, stockage, processus, PID.
- Étape 1 : distinguer mémoire vive et stockage.
- Étape 2 : identifier PID et processus.
- Résultat de référence : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.

## Cas limites à mémoriser
- fichier absent.
- droit x manquant sur dossier.
- chmod 777 trop permissif.

## Erreurs fréquentes
- confondre mémoire et disque.
- oublier x sur dossier.
- donner tous les droits.

## Critères de réussite observables
- Capacité : P-ARCH-01A.
- Résultat final : chmod 640 mesures.csv donne rw-r-----.
- Cas limite : fichier absent.
