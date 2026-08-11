---
title: "T08 - cours - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "cours"
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

# T08 - Cours - BFS, DFS, cycles et chemins

## Objectifs spécifiques
- Identifier les données utiles de la situation : adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}.
- Employer le vocabulaire : BFS avec file, DFS avec pile, marquage, prédécesseurs, chemin reconstruit, cycle.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-ALGO-02A.
- T-ALGO-02B.
- T-ALGO-02C.
- T-ALGO-02D.

## Situation-problème
adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}

## À savoir
- BFS avec file.
- DFS avec pile.
- marquage.
- prédécesseurs.
- chemin reconstruit.
- cycle.
- graphe non connexe.
- complexité.

## Méthodes
- BFS file A puis B,C puis D,E.
- mémoriser prédécesseurs.
- DFS explore un chemin avant retour.
- détecter cycle par sommet gris.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Méthode : BFS file A puis B,C puis D,E.
- Résultat attendu : BFS -> A,B,C,D,E.
- Contrôle : capacité T-ALGO-02A et cas limite `sommet isolé F`.
### Exemple corrigé 2
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Méthode : mémoriser prédécesseurs.
- Résultat attendu : prédécesseurs E<-C<-A donc chemin A-C-E.
- Contrôle : capacité T-ALGO-02B et cas limite `destination absente`.
### Exemple corrigé 3
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Méthode : DFS explore un chemin avant retour.
- Résultat attendu : F isolé -> aucun chemin.
- Contrôle : capacité T-ALGO-02C et cas limite `cycle D-C-D`.
### Exemple corrigé 4
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Méthode : détecter cycle par sommet gris.
- Résultat attendu : complexité O(V+E).
- Contrôle : capacité T-ALGO-02D et cas limite `sommet isolé F`.

## Cas limites
- sommet isolé F.
- destination absente.
- cycle D-C-D.

## Erreurs fréquentes
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Exercices intégrés
1. Identifier les données utiles dans `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
2. Appliquer : BFS file A puis B,C puis D,E.
3. Appliquer : mémoriser prédécesseurs.
4. Décider le cas limite `sommet isolé F`.

## Critères de réussite observables
- Une capacité parmi T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D est citée et utilisée.
- Le résultat attendu est explicite : BFS -> A,B,C,D,E.
- Le cas limite `destination absente` est tranché.

## Lien avec la progression
- Séance : T08-S1 à T08-S4.
- TD : `T08_TD_bfs_dfs_cycles_chemins.md`.
- TP : `T08_tp_bfs_dfs_cycles_chemins.md`.
- Évaluation : `T08_evaluation_bfs_dfs_cycles_chemins.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur parcours de graphes. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : BFS, DFS, file, pile, marquage, prédécesseur, chemin, cycle.
- Capacités reliées : T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- enfiler les voisins dans un BFS.
- empiler ou appeler récursivement en DFS.
- reconstruire un chemin avec les prédécesseurs.

### Erreurs fréquentes spécifiques
- Un élève peut marquer un sommet trop tard ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut annoncer un chemin sans prédécesseur cohérent ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut ignorer une composante non connexe ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de parcours de graphes.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
