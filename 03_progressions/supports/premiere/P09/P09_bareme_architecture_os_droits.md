---
title: "P09 - bareme - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "bareme"
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

# P09 - Barème - architecture, système et droits Unix

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`.
- 3 points tâche `distinguer mémoire vive et stockage`.
- 3 points résultat `-rw-r----- -> propriétaire rw, groupe r, autres aucun droit`.
- 2 points cas limite `fichier absent`.

## Évaluation question par question
- Question 1 : 4 points sur P-ARCH-01A avec résultat `-rw-r----- -> propriétaire rw, groupe r, autres aucun droit`.
- Question 2 : 4 points sur P-ARCH-01B avec résultat `chmod 640 mesures.csv donne rw-r-----`.
- Question 3 : 4 points sur P-ARCH-03A avec résultat `PID 2314 python collecte.py est un processus`.
- Question 4 : 4 points sur P-ARCH-03B avec résultat `sans x sur dossier, lecture du fichier impossible`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
