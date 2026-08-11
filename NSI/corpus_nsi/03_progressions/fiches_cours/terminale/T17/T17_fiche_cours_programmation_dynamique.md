---
title: "T17 - Fiche cours - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique avancée"
notion: "programmation dynamique"
official_program:
  capacities:
    - "T-ALGO-04"
readiness: operational
private_data: false
---
# T17 - Fiche cours - Programmation dynamique

## À savoir
- programmation dynamique se travaille dans le contexte “mémoïsation” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour programmation dynamique.
- Les capacités T-ALGO-04 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de programmation dynamique avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-ALGO-04.
2. T-ALGO-04 : mémoriser des sous-résultats réutilisés.
3. Identifier les données d’entrée de programmation dynamique puis écrire le résultat attendu avant de conclure.
4. Contrôler programmation dynamique par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T17 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Dans Fibonacci, `fib(3)` est demandé plusieurs fois sans mémoïsation.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Une table de sommes cible stocke le meilleur résultat pour chaque montant intermédiaire.
### Exemple corrigé 3 - Somme cible par tabulation
On dispose des valeurs `[2, 5, 7]` et on veut atteindre la cible `9`. État : `dp[s]` vaut `True` si la somme `s` est atteignable. Initialisation : `dp[0] = True` et `dp[1..9] = False`. Relation de récurrence : pour chaque valeur `v`, mettre `dp[s] = dp[s] or dp[s-v]` pour `s` décroissant de `9` à `v`. Table partielle après `2` puis `5` : `dp[0]=True`, `dp[2]=True`, `dp[5]=True`, `dp[7]=True`. Après `7`, `dp[9]=True` car `9 = 2 + 7`. Résultat final : la cible 9 est atteignable.

## Erreurs fréquentes
- Confondre le vocabulaire de programmation dynamique avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de mémoïsation : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur programmation dynamique : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour programmation dynamique, à traiter selon la convention du chapitre T17.
- Donnée invalide dans mémoïsation, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de programmation dynamique où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-ALGO-04 : appliquer la méthode de programmation dynamique à un exemple court choisi dans le chapitre T17.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de mémoïsation.
### Mini-exercice 3
Proposer un cas limite pertinent pour programmation dynamique et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour programmation dynamique.

## Réponses rapides
1. La méthode attendue pour programmation dynamique commence par les données puis applique l’opération du chapitre T17.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans mémoïsation.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon programmation dynamique.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de programmation dynamique.

## À retenir
- T17 : programmation dynamique se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-ALGO-04 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de programmation dynamique doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T17, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T17 sur programmation dynamique reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T17-S1 | réelle | séance présente dans la progression |
| TD | T17_TD_programmation_dynamique.md | existant | support TD créé en needs_review |
| Évaluation | T17_evaluation_programmation_dynamique.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer programmation dynamique avec un exemple différent de ceux de la fiche T17.
- Je peux citer au moins une capacité parmi T-ALGO-04 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T17 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de programmation dynamique sans transformer la fiche en corrigé complet.
