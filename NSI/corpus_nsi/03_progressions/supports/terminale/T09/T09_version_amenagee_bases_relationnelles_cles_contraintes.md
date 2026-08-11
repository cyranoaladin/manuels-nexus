---
title: "T09 - version_amenagee - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "version_amenagee"
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

# T09 - Version aménagée - bases relationnelles, clés et contraintes

## Aides intégrées
- Donnée fournie : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Mots utiles : relation, attribut, tuple, clé primaire, clé étrangère.
- Méthode guidée : identifier schéma et instance puis vérifier unicité id_livre.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-BDD-01A ou T-BDD-01B.
3. Compléter le résultat : Livre.id_livre identifie chaque livre.
4. Cocher le cas limite : clé primaire nulle.

## Réponses rapides
- Réponse 1 : Livre.id_livre identifie chaque livre.
- Réponse 2 : Emprunt.id_livre référence Livre.id_livre.
- Réponse 3 : Emprunt(11,9,Sam) viole la référence.
