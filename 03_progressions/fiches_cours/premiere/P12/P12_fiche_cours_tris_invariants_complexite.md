---
title: "P12 - Fiche cours - Tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "tris"
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
readiness: operational
private_data: false
---
# P12 - Fiche cours - Tris, invariants et complexité

## À savoir
- tris et invariants se travaille dans le contexte “algorithmique de tri” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour tris.
- Les capacités P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de tris et invariants avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D.
2. P-ALGO-02A : décrire la partie déjà triée et la partie restante.
3. Identifier les données d’entrée de tris puis écrire le résultat attendu avant de conclure.
4. Contrôler tris par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance P12 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Une passe de sélection sur `[5,2,4]` place 2 en tête.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Insérer 3 dans `[1,2,5]` donne `[1,2,3,5]`.

## Erreurs fréquentes
- Confondre le vocabulaire de tris avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de algorithmique de tri : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur tris et invariants : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour tris, à traiter selon la convention du chapitre P12.
- Donnée invalide dans algorithmique de tri, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de tris et invariants où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
P-ALGO-02A : appliquer la méthode de tris à un exemple court choisi dans le chapitre P12.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de algorithmique de tri.
### Mini-exercice 3
Proposer un cas limite pertinent pour tris et invariants et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour tris.

## Réponses rapides
1. La méthode attendue pour tris commence par les données puis applique l’opération du chapitre P12.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans algorithmique de tri.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon tris et invariants.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de tris.

## À retenir
- P12 : tris se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de tris et invariants doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour P12, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche P12 sur tris reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P12-S1 | réelle | séance présente dans la progression |
| TD | P12_TD_tris_invariants_complexite.md | existant | support TD créé en needs_review |
| Évaluation | P12_evaluation_tris_invariants_complexite.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer tris avec un exemple différent de ceux de la fiche P12.
- Je peux citer au moins une capacité parmi P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à P12 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de tris et invariants sans transformer la fiche en corrigé complet.
