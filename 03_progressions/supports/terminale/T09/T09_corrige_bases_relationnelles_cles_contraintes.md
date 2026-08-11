---
title: "T09 - corrige - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "corrige"
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

# T09 - Corrigé - bases relationnelles, clés et contraintes

## Corrigé du TD
### Exercice 1
- Réponse attendue : Livre.id_livre identifie chaque livre.
- Méthode : identifier schéma et instance.
- Cas limite : clé primaire nulle.
### Exercice 2
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : doublon id_livre=1.
### Exercice 3
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Méthode : contrôler Emprunt.id_livre.
- Cas limite : suppression référencée.
### Exercice 4
- Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent.
- Cas limite : clé primaire nulle.
### Exercice 5
- Réponse attendue : Livre.id_livre identifie chaque livre.
- Méthode : identifier schéma et instance.
- Cas limite : doublon id_livre=1.
### Exercice 6
- Réponse attendue : Emprunt.id_livre référence Livre.id_livre.
- Méthode : vérifier unicité id_livre.
- Cas limite : suppression référencée.
### Exercice 7
- Réponse attendue : Emprunt(11,9,Sam) viole la référence.
- Méthode : contrôler Emprunt.id_livre.
- Cas limite : clé primaire nulle.
### Exercice 8
- Réponse attendue : suppression d un livre emprunté refusée.
- Méthode : repérer id_livre=9 absent.
- Cas limite : doublon id_livre=1.

## Corrigé du TP
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Résultat principal : Livre.id_livre identifie chaque livre.
- Résultat secondaire : Emprunt.id_livre référence Livre.id_livre.

## Corrigé de l évaluation
- Question 1 : Livre.id_livre identifie chaque livre.
- Question 2 : Emprunt.id_livre référence Livre.id_livre.
- Question 3 : Emprunt(11,9,Sam) viole la référence.
- Question 4 : suppression d un livre emprunté refusée.
