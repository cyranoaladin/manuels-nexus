---
title: "T08 - trace - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "trace"
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

# T08 - Trace - BFS, DFS, cycles et chemins

## Trace courte
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Vocabulaire : BFS avec file, DFS avec pile, marquage, prédécesseurs, chemin reconstruit.
- Étape 1 : BFS file A puis B,C puis D,E.
- Étape 2 : mémoriser prédécesseurs.
- Résultat de référence : BFS -> A,B,C,D,E.

## Cas limites à mémoriser
- sommet isolé F.
- destination absente.
- cycle D-C-D.

## Erreurs fréquentes
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Critères de réussite observables
- Capacité : T-ALGO-02A.
- Résultat final : prédécesseurs E<-C<-A donc chemin A-C-E.
- Cas limite : sommet isolé F.
