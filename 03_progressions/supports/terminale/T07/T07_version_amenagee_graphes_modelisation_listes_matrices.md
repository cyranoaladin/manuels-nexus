---
title: "T07 - version_amenagee - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "graphes, listes et matrices"
notion: "graphes, listes et matrices"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-05A"
    - "T-STRUCT-05B"
    - "T-STRUCT-05C"
    - "T-STRUCT-05D"
---

# T07 - Version aménagée - graphes, listes et matrices

## Aides intégrées
- Donnée fournie : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Mots utiles : graphe orienté, graphe non orienté, liste d adjacence, matrice d adjacence, degré.
- Méthode guidée : lister voisins sortants puis remplir matrice 0/1.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-STRUCT-05A ou T-STRUCT-05B.
3. Compléter le résultat : A -> [B,C], B -> [D], C -> [D], D -> [B].
4. Cocher le cas limite : sommet isolé E.

## Réponses rapides
- Réponse 1 : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Réponse 2 : ligne A : colonnes B et C valent 1.
- Réponse 3 : matrice 4x4 -> 16 cases.
