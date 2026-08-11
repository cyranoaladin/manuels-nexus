---
title: "T09 - remediation - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "remediation"
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

# T09 - Remédiation - bases relationnelles, clés et contraintes

## Diagnostic
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Activités correctives
1. Annoter `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
2. Refaire la tâche `identifier schéma et instance` et comparer avec `Livre.id_livre identifie chaque livre`.
3. Traiter le cas limite `clé primaire nulle`.
4. Relier la réponse à T-BDD-01A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
