---
title: "T09 - bareme - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "bases relationnelles, clés et contraintes"
notion: "bases relationnelles, clés et contraintes"
private_data: false
official_program:
  capacities:
    - "T-BDD-01A"
    - "T-BDD-01B"
    - "T-BDD-01C"
    - "T-BDD-02"
---

# T09 - Barème - bases relationnelles, clés et contraintes

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- 3 points tâche `identifier schéma et instance`.
- 3 points résultat `Livre.id_livre identifie chaque livre`.
- 2 points cas limite `clé primaire nulle`.

## Évaluation question par question
- Question 1 : 4 points sur T-BDD-01A avec résultat `Livre.id_livre identifie chaque livre`.
- Question 2 : 4 points sur T-BDD-01B avec résultat `Emprunt.id_livre référence Livre.id_livre`.
- Question 3 : 4 points sur T-BDD-01C avec résultat `Emprunt(11,9,Sam) viole la référence`.
- Question 4 : 4 points sur T-BDD-02 avec résultat `suppression d un livre emprunté refusée`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
