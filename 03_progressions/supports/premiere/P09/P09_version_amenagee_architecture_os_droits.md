---
title: "P09 - version_amenagee - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "version_amenagee"
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

# P09 - Version aménagée - architecture, système et droits Unix

## Aides intégrées
- Donnée fournie : `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`.
- Mots utiles : processeur, mémoire, stockage, processus, PID.
- Méthode guidée : distinguer mémoire vive et stockage puis identifier PID et processus.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-ARCH-01A ou P-ARCH-01B.
3. Compléter le résultat : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
4. Cocher le cas limite : fichier absent.

## Réponses rapides
- Réponse 1 : -rw-r----- -> propriétaire rw, groupe r, autres aucun droit.
- Réponse 2 : chmod 640 mesures.csv donne rw-r-----.
- Réponse 3 : PID 2314 python collecte.py est un processus.
