---
title: "T04 - Fiche cours - Récursivité, cas de base et terminaison"
level: "terminale"
sequence_id: "T04"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Récursivité"
notion: "récursivité"
official_program:
  capacities:
    - "T-LANG-02A"
    - "T-LANG-02B"
readiness: operational
private_data: false
---
# T04 - Fiche cours - Récursivité, cas de base et terminaison

## À savoir
- récursivité se travaille dans le contexte “cas de base et terminaison” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour récursivité.
- Les capacités T-LANG-02A, T-LANG-02B sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de récursivité avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-LANG-02A, T-LANG-02B.
2. T-LANG-02A : définir un cas de base et une diminution stricte.
3. Identifier les données d’entrée de récursivité puis écrire le résultat attendu avant de conclure.
4. Contrôler récursivité par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T04 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
`fact(3)` appelle `fact(2)`, puis `fact(1)`, puis le cas `fact(0)`.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Une somme récursive de liste vide renvoie 0 avant tout appel sur le reste.

## Erreurs fréquentes
- Confondre le vocabulaire de récursivité avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de cas de base et terminaison : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur récursivité : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour récursivité, à traiter selon la convention du chapitre T04.
- Donnée invalide dans cas de base et terminaison, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de récursivité où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-LANG-02A : appliquer la méthode de récursivité à un exemple court choisi dans le chapitre T04.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de cas de base et terminaison.
### Mini-exercice 3
Proposer un cas limite pertinent pour récursivité et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour récursivité.

## Réponses rapides
1. La méthode attendue pour récursivité commence par les données puis applique l’opération du chapitre T04.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans cas de base et terminaison.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon récursivité.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de récursivité.

## À retenir
- T04 : récursivité se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-LANG-02A, T-LANG-02B restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de récursivité doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T04, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T04 sur récursivité reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T04-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/terminale/T04/T04_td_recursivite.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/terminale/T04/T04_tp_recursivite.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/terminale/T04/T04_evaluation_recursivite.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer récursivité avec un exemple différent de ceux de la fiche T04.
- Je peux citer au moins une capacité parmi T-LANG-02A, T-LANG-02B et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T04 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de récursivité sans transformer la fiche en corrigé complet.
