---
title: "T18 - version_amenagee - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - Version aménagée - Boyer-Moore

## Aides intégrées
- Donnée fournie : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`.
- Mots utiles : motif, texte, table du mauvais caractère, comparaison droite à gauche, décalage.
- Méthode guidée : prétraiter dernière position de chaque caractère puis comparer depuis la droite.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-ALGO-05 ou T-ALGO-05.
3. Compléter le résultat : table : A->2, N->1.
4. Cocher le cas limite : motif absent.

## Réponses rapides
- Réponse 1 : table : A->2, N->1.
- Réponse 2 : alignement 0 : N comparé à A -> décalage 1.
- Réponse 3 : alignement 1 : ANA trouvé à l'indice 1.
