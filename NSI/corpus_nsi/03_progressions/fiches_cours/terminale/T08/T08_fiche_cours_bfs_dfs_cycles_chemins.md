---
title: "T08 - Fiche cours - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Graphes"
notion: "parcours de graphes"
official_program:
  capacities:
    - "T-ALGO-02A"
    - "T-ALGO-02B"
    - "T-ALGO-02C"
    - "T-ALGO-02D"
readiness: operational
private_data: false
---
# T08 - Fiche cours - BFS, DFS, cycles et chemins

## À savoir
- BFS, DFS et chemins se travaille dans le contexte “parcours de graphes” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour parcours de graphes.
- Les capacités T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de BFS, DFS et chemins avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D.
2. T-ALGO-02A : explorer avec file ou pile et marquer les sommets.
3. Identifier les données d’entrée de parcours de graphes puis écrire le résultat attendu avant de conclure.
4. Contrôler parcours de graphes par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T08 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
BFS depuis A traite B et C avant les descendants de B.
### Exemple corrigé 2 - Contrôle ou contre-exemple
DFS peut suivre A-B-D avant de revenir explorer C.

## Erreurs fréquentes
- Confondre le vocabulaire de parcours de graphes avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de parcours de graphes : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur BFS, DFS et chemins : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour parcours de graphes, à traiter selon la convention du chapitre T08.
- Donnée invalide dans parcours de graphes, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de BFS, DFS et chemins où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-ALGO-02A : appliquer la méthode de parcours de graphes à un exemple court choisi dans le chapitre T08.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de parcours de graphes.
### Mini-exercice 3
Proposer un cas limite pertinent pour BFS, DFS et chemins et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour parcours de graphes.

## Réponses rapides
1. La méthode attendue pour parcours de graphes commence par les données puis applique l’opération du chapitre T08.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans parcours de graphes.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon BFS, DFS et chemins.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de parcours de graphes.

## À retenir
- T08 : parcours de graphes se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de BFS, DFS et chemins doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T08, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T08 sur parcours de graphes reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T08-S1 | réelle | séance présente dans la progression |
| TD | T08_TD_bfs_dfs_cycles_chemins.md | existant | support produit en needs_review, non validé |
| TP | T08_TP_bfs_dfs_cycles_chemins.md | existant | support produit en needs_review, non validé |
| Évaluation | T08_evaluation_bfs_dfs_cycles_chemins.md | existant | support produit en needs_review, non validé |

## Auto-évaluation
- Je peux expliquer parcours de graphes avec un exemple différent de ceux de la fiche T08.
- Je peux citer au moins une capacité parmi T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T08 existe déjà ou existe ou reste explicitement qualifié.
- Je peux identifier un cas limite de BFS, DFS et chemins sans transformer la fiche en corrigé complet.
