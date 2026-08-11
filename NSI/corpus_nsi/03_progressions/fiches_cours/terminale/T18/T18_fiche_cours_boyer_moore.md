---
title: "T18 - Fiche cours - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "adapted_from_drive"
theme: "Recherche textuelle"
notion: "Boyer-Moore"
official_program:
  capacities:
    - "T-ALGO-05"
readiness: operational
private_data: false
---
# T18 - Fiche cours - Boyer-Moore

## À savoir
- Boyer-Moore se travaille dans le contexte “recherche textuelle” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour Boyer-Moore.
- Les capacités T-ALGO-05 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de Boyer-Moore avec une valeur, une table ou un code différent.
- Ressource locale adaptée : `Documents_DRIVE/NSI_Tle/Séquence17_Boyer-Moore`.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-ALGO-05.
2. T-ALGO-05 : comparer un motif depuis sa droite et décaler.
3. Identifier les données d’entrée de Boyer-Moore puis écrire le résultat attendu avant de conclure.
4. Contrôler Boyer-Moore par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T18 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Dans le motif `ANA`, la table du mauvais caractère donne `A -> 2` et `N -> 1` si l’on retient la dernière position dans le motif. Sur le texte `BANANA`, on aligne d’abord `ANA` sous les positions 0 à 2 : la comparaison depuis la droite trouve `A` contre `N`, donc un mauvais caractère `N` présent dans le motif à l’indice 1 ; on décale le motif pour aligner ce `N`.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Si le mauvais caractère est absent du motif, par exemple comparer `ANA` à une fenêtre contenant `B` en position de désaccord, on peut décaler le motif au-delà de ce caractère. Le contrôle consiste à vérifier que le décalage ne saute pas une occurrence possible du motif.

## Erreurs fréquentes
- Confondre le vocabulaire de Boyer-Moore avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de recherche textuelle : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur Boyer-Moore : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour Boyer-Moore, à traiter selon la convention du chapitre T18.
- Donnée invalide dans recherche textuelle, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de Boyer-Moore où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-ALGO-05 : appliquer la méthode de Boyer-Moore à un exemple court choisi dans le chapitre T18.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de recherche textuelle.
### Mini-exercice 3
Proposer un cas limite pertinent pour Boyer-Moore et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour Boyer-Moore.

## Réponses rapides
1. La méthode attendue pour Boyer-Moore commence par les données puis applique l’opération du chapitre T18.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans recherche textuelle.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon Boyer-Moore.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de Boyer-Moore.

## À retenir
- T18 : Boyer-Moore se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-ALGO-05 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de Boyer-Moore doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T18, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T18 sur Boyer-Moore reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T18-S1 | réelle | séance présente dans la progression |
| TD | T18_TD_boyer_moore.md | existant | support TD créé en needs_review |
| Évaluation | T18_evaluation_boyer_moore.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer Boyer-Moore avec un exemple différent de ceux de la fiche T18.
- Je peux citer au moins une capacité parmi T-ALGO-05 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T18 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de Boyer-Moore sans transformer la fiche en corrigé complet.

## Trace complète Boyer-Moore
- Motif : `ABA`.
- Texte : `CABAABABA`.
- Table du mauvais caractère : `A -> 2`, `B -> 1`, tout autre caractère -> `-1`.
- Comparaison de droite à gauche, alignement `i=0` : on compare motif[2] = `A` avec texte[2] = `B`, désaccord sur `B`.
- Décalage : `j=2`, dernier `B` dans le motif à `1`, donc `max(1, 2-1) = 1`.
- Alignement `i=1` : fenêtre `ABA`; comparaisons `A=A`, `B=B`, `A=A`; motif trouvé à l’indice `1`.
- Cas absent : dans `texte="CCCC"` et `motif="ABA"`, le caractère de désaccord `C` absent du motif donne un décalage de `3`, puis aucun alignement complet ne réussit.
- Comparaison naïve : la recherche naïve teste le motif depuis chaque position ; Boyer-Moore exploite un désaccord à droite pour sauter des alignements.

## Pseudo-code
```text
last = table_mauvais_caractere(motif)
i = 0
tant que i <= len(texte) - len(motif):
    j = len(motif) - 1
    tant que j >= 0 et motif[j] == texte[i+j]:
        j = j - 1
    si j < 0:
        renvoyer i
    mauvais = texte[i+j]
    i = i + max(1, j - last.get(mauvais, -1))
renvoyer -1
```
