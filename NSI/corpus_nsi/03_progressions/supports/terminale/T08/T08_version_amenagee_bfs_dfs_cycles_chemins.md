---
title: "T08 - version_amenagee - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "BFS, DFS, cycles et chemins"
notion: "BFS, DFS, cycles et chemins"
private_data: false
official_program:
  capacities:
    - "T-ALGO-02A"
    - "T-ALGO-02B"
    - "T-ALGO-02C"
    - "T-ALGO-02D"
---

# T08 - Version aménagée - BFS, DFS, cycles et chemins

## Aides intégrées
- Donnée fournie : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Mots utiles : BFS avec file, DFS avec pile, marquage, prédécesseurs, chemin reconstruit.
- Méthode guidée : BFS file A puis B,C puis D,E puis mémoriser prédécesseurs.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-ALGO-02A ou T-ALGO-02B.
3. Compléter le résultat : BFS -> A,B,C,D,E.
4. Cocher le cas limite : sommet isolé F.

## Réponses rapides
- Réponse 1 : BFS -> A,B,C,D,E.
- Réponse 2 : prédécesseurs E<-C<-A donc chemin A-C-E.
- Réponse 3 : F isolé -> aucun chemin.
