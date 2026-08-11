---
title: "T09 - trace - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "trace"
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

# T09 - Trace - bases relationnelles, clés et contraintes

## Trace courte
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Vocabulaire : relation, attribut, tuple, clé primaire, clé étrangère.
- Étape 1 : identifier schéma et instance.
- Étape 2 : vérifier unicité id_livre.
- Résultat de référence : Livre.id_livre identifie chaque livre.

## Cas limites à mémoriser
- clé primaire nulle.
- doublon id_livre=1.
- suppression référencée.

## Erreurs fréquentes
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Critères de réussite observables
- Capacité : T-BDD-01A.
- Résultat final : Emprunt.id_livre référence Livre.id_livre.
- Cas limite : clé primaire nulle.
