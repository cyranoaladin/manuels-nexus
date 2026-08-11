---
title: "T12 - tp - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - TP - routage RIP et OSPF

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (T12_starter_routage_rip_ospf.py, T12_tests_attendus_routage_rip_ospf.py, T12_corrige_professeur_routage_rip_ospf.py).

## Donnée fournie
`RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : compter sauts RIP.
3. Réaliser : additionner coûts OSPF.
4. Tester le cas limite `égalité exacte`.
5. Produire le livrable : RIP : A-B-D et A-C-D ont 2 sauts.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `RIP : A-B-D et A-C-D ont 2 sauts`.
- 2 points : cas limite `égalité exacte`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
### Corrigé question 2
Résultat attendu : RIP : A-B-D et A-C-D ont 2 sauts.
### Corrigé question 3
Résultat attendu : OSPF : A-B-D coût 10, A-C-D coût 11.
### Corrigé question 4
Résultat attendu : `égalité exacte` traité sans ambiguïté.

## Liens
- TD lié : `T12_TD_routage_rip_ospf.md`.
- Évaluation liée : `T12_evaluation_routage_rip_ospf.md`.

## Cas limites travaillés
- égalité exacte.
- lien indisponible.
- route inconnue.

## Erreurs fréquentes
- sauts et coûts mélangés.
- choix visuel.
- panne non recalculée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `RIP : A-B-D et A-C-D ont 2 sauts`.
- Au moins un cas limite de la section précédente est décidé.



## Assets Python
- Starter élève : `code/T12_starter_routage_rip_ospf.py`.
- Tests attendus : `code/T12_tests_attendus_routage_rip_ospf.py`.
- Corrigé professeur : `code/T12_corrige_professeur_routage_rip_ospf.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
