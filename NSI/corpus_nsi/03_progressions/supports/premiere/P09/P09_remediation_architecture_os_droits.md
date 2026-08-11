---
title: "P09 - remediation - architecture, système et droits Unix"
level: "premiere"
sequence_id: "P09"
document_type: "remediation"
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

# P09 - Remédiation - architecture, système et droits Unix

## Diagnostic
- confondre mémoire et disque.
- oublier x sur dossier.
- donner tous les droits.

## Activités correctives
1. Annoter `ls -l mesures.csv -> -rw-r----- 1 prof nsi 1240 mesures.csv ; utilisateur eleve hors groupe nsi`.
2. Refaire la tâche `distinguer mémoire vive et stockage` et comparer avec `-rw-r----- -> propriétaire rw, groupe r, autres aucun droit`.
3. Traiter le cas limite `fichier absent`.
4. Relier la réponse à P-ARCH-01A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
