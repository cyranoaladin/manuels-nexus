---
title: "T01 - Fiche cours - Interface, implémentation et TAD"
level: "terminale"
sequence_id: "T01"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "adapted_from_drive"
theme: "Structures abstraites"
notion: "TAD"
official_program:
  capacities:
    - "T-STRUCT-01A"
    - "T-STRUCT-01B"
    - "T-STRUCT-01C"
readiness: operational
private_data: false
---
# T01 - Fiche cours - Interface, implémentation et TAD

## À savoir
- interface et TAD se travaille dans le contexte “structures abstraites” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour TAD.
- Les capacités T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de interface et TAD avec une valeur, une table ou un code différent.
- Ressource locale adaptée : `Documents_DRIVE/NSI_Tle/Séquence1_TAD_Théorie`.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C.
2. T-STRUCT-01A : séparer opérations visibles et représentation interne.
3. Identifier les données d’entrée de TAD puis écrire le résultat attendu avant de conclure.
4. Contrôler TAD par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T01 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Une pile expose `empiler(x)`, `depiler()` et `est_vide()` sans révéler sa représentation interne. Avec l’état abstrait vide, après `empiler("A")`, puis `empiler("B")`, l’appel `depiler()` doit renvoyer `"B"` : c’est la règle LIFO qui définit l’interface, pas le fait d’utiliser une liste Python.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Deux implémentations peuvent respecter la même interface : une pile stockée dans une liste avec ajout en fin, ou dans une liste chaînée. Elles doivent produire la même suite abstraite de résultats, mais leurs coûts et invariants internes peuvent différer.

## Erreurs fréquentes
- Confondre le vocabulaire de TAD avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de structures abstraites : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur interface et TAD : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour TAD, à traiter selon la convention du chapitre T01.
- Donnée invalide dans structures abstraites, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de interface et TAD où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-STRUCT-01A : appliquer la méthode de TAD à un exemple court choisi dans le chapitre T01.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de structures abstraites.
### Mini-exercice 3
Proposer un cas limite pertinent pour interface et TAD et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour TAD.

## Réponses rapides
1. La méthode attendue pour TAD commence par les données puis applique l’opération du chapitre T01.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans structures abstraites.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon interface et TAD.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de TAD.

## À retenir
- T01 : TAD se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de interface et TAD doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T01, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T01 sur TAD reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T01-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/terminale/T01/T01_td_interfaces_structures.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/terminale/T01/T01_tp_interfaces_structures.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/terminale/T01/T01_evaluation_interfaces_structures.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer TAD avec un exemple différent de ceux de la fiche T01.
- Je peux citer au moins une capacité parmi T-STRUCT-01A, T-STRUCT-01B, T-STRUCT-01C et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T01 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de interface et TAD sans transformer la fiche en corrigé complet.

## Bloc TAD opérationnel
### Interface pile
- Opérations pile : création, test de vacuité, empilement, dépilement et lecture du sommet.
- Contrat : `depiler` et `sommet` sont interdits sur une pile vide, sauf convention explicite d’exception.
- Règle abstraite : LIFO, le dernier élément empilé est le premier dépilé.

### Interface file
- Opérations file : création, test de vacuité, ajout en queue, retrait en tête et consultation du premier élément.
- Contrat : `defiler` et `premier` sont interdits sur une file vide.
- Règle abstraite : FIFO, le premier élément entré est le premier sorti.

### Deux implémentations
- Pile par liste : `empiler` utilise `append`, `depiler` utilise `pop`; complexité amortie `O(1)`.
- File naïve par liste : `enfiler` utilise `append`, `defiler` utilise `pop(0)`; coût `O(n)` car les éléments sont décalés.
- File avec deux listes : une liste d’entrée et une liste de sortie ; les transferts donnent un coût amorti `O(1)`.

### Invariants et tests
- Invariant pile : la représentation interne garde l’ordre d’empilement ; le sommet correspond à la dernière case utile.
- Invariant file : l’ordre FIFO est conservé même si la représentation change.
- Test de conformité pile : après `empiler("A")`, `empiler("B")`, `depiler()` renvoie `"B"`, puis `depiler()` renvoie `"A"`.
- Test de conformité file : après `enfiler("A")`, `enfiler("B")`, `defiler()` renvoie `"A"`, puis `"B"`.
- Cas limite : dépiler ou défiler une structure vide doit lever une erreur documentée.
