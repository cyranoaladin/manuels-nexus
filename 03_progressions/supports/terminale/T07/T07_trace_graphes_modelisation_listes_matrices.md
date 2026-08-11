---
title: "T07 - trace - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "trace"
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

# T07 - Trace - graphes, listes et matrices

## Trace courte
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Vocabulaire : graphe orienté, graphe non orienté, liste d adjacence, matrice d adjacence, degré.
- Étape 1 : lister voisins sortants.
- Étape 2 : remplir matrice 0/1.
- Résultat de référence : A -> [B,C], B -> [D], C -> [D], D -> [B].

## Cas limites à mémoriser
- sommet isolé E.
- boucle A->A.
- arête non orientée.

## Erreurs fréquentes
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Critères de réussite observables
- Capacité : T-STRUCT-05A.
- Résultat final : ligne A : colonnes B et C valent 1.
- Cas limite : sommet isolé E.
