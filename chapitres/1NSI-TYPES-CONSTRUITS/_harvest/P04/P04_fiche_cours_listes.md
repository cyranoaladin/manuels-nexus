---
title: "P04 - Fiche cours - Listes et tableaux indexés"
level: "premiere"
sequence_id: "P04"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Types construits"
notion: "listes"
official_program:
  capacities:
    - "P-DATA-CONSTR-02A"
    - "P-DATA-CONSTR-02B"
    - "P-DATA-CONSTR-02C"
    - "P-DATA-CONSTR-02D"
readiness: operational
private_data: false
---
# P04 - Fiche cours - Listes et tableaux indexés

## À savoir
- types construits se travaille dans le contexte “tuples, listes et dictionnaires” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour listes.
- Les capacités P-DATA-CONSTR-02A, P-DATA-CONSTR-02B, P-DATA-CONSTR-02C, P-DATA-CONSTR-02D sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de types construits avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : P-DATA-CONSTR-02A, P-DATA-CONSTR-02B, P-DATA-CONSTR-02C, P-DATA-CONSTR-02D.
2. P-DATA-CONSTR-02A : choisir une structure selon l’accès attendu.
3. Identifier les données d’entrée de listes puis écrire le résultat attendu avant de conclure.
4. Contrôler listes par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance P04 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
`notes[1] = 14` modifie la deuxième valeur de `[8,12,10]`.
### Exemple corrigé 2 - Contrôle ou contre-exemple
`eleve["score"]` lit une valeur par clé dans un dictionnaire.

## Erreurs fréquentes
- Confondre le vocabulaire de listes avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de tuples, listes et dictionnaires : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur types construits : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour listes, à traiter selon la convention du chapitre P04.
- Donnée invalide dans tuples, listes et dictionnaires, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de types construits où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
P-DATA-CONSTR-02A : appliquer la méthode de listes à un exemple court choisi dans le chapitre P04.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de tuples, listes et dictionnaires.
### Mini-exercice 3
Proposer un cas limite pertinent pour types construits et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour listes.

## Réponses rapides
1. La méthode attendue pour listes commence par les données puis applique l’opération du chapitre P04.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans tuples, listes et dictionnaires.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon types construits.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de listes.

## À retenir
- P04 : listes se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités P-DATA-CONSTR-02A, P-DATA-CONSTR-02B, P-DATA-CONSTR-02C, P-DATA-CONSTR-02D restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de types construits doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour P04, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche P04 sur listes reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P04-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/premiere/P04/P04_td_types_construits.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/premiere/P04/P04_tp_types_construits.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/premiere/P04/P04_evaluation_types_construits.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer listes avec un exemple différent de ceux de la fiche P04.
- Je peux citer au moins une capacité parmi P-DATA-CONSTR-02A, P-DATA-CONSTR-02B, P-DATA-CONSTR-02C, P-DATA-CONSTR-02D et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à P04 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de types construits sans transformer la fiche en corrigé complet.

## Complément types construits P04
- Tuple immuable : `point = (3.0, 5.0)` représente une coordonnée fixe ; `point[0] = 4.0` doit être refusé car un tuple ne se modifie pas.
- Liste mutable : `notes = [8, 12, 10]`, puis `notes[1] = 14` donne `[8, 14, 10]`.
- Dictionnaire par clé : `station = {"nom": "Carthage", "temperature": 21}` ; `station["temperature"]` vaut `21`.
- Liste de dictionnaires : `stations = [{"nom": "A", "temperature": 21}, {"nom": "B", "temperature": 18}]` permet de filtrer les stations dont `temperature >= 20`.
- Tuple de coordonnées : pour `A = (2, 3)` et `B = (8, 7)`, le milieu vaut `((2+8)/2, (3+7)/2) = (5.0, 5.0)`.
- Distance : avec les mêmes points, `dx = 6`, `dy = 4`, donc `distance = sqrt(6**2 + 4**2) = sqrt(52)`.
- Cas limite tuple : `(2,)` n’a pas deux coordonnées ; une fonction `milieu(A, B)` doit lever `ValueError` si `len(A) != 2`.
- Cas limite dictionnaire : `station["pression"]` lève `KeyError`; on utilise `"pression" in station` ou `station.get("pression")`.
- Cas limite liste : la moyenne d’une liste vide n’est pas définie ; le code doit tester `if not notes`.

## Mini-exercices corrigés complémentaires
### Mini-exercice 5
Calculer le milieu de `A=(0, 4)` et `B=(6, 10)`.

Réponse : `((0+6)/2, (4+10)/2) = (3.0, 7.0)`.

### Mini-exercice 6
Après `mesures = [{"jour": "lundi", "temperature": 20}, {"jour": "mardi", "temperature": 17}]`, donner les jours de température au moins 18.

Réponse : seul `"lundi"` est gardé, car `20 >= 18` et `17 < 18`.

### Mini-exercice 7
Dire pourquoi `point[1] = 9` est incorrect si `point = (2, 3)`.

Réponse : `point` est un tuple immuable ; il faut créer un nouveau tuple, par exemple `(2, 9)`.
