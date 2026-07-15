---
title: "P04 - Fiche cours - Tuples et p-uplets"
level: "premiere"
sequence_id: "P04"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "adapted_from_drive"
theme: "Types construits"
notion: "tuples"
official_program:
  capacities:
    - "P-DATA-CONSTR-01"
readiness: operational
private_data: false
---
# P04 - Fiche cours - Tuples et p-uplets

## À savoir
- types construits se travaille dans le contexte “tuples, listes et dictionnaires” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour tuples.
- Les capacités P-DATA-CONSTR-01 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de types construits avec une valeur, une table ou un code différent.
- Ressource locale adaptée : `Documents_DRIVE/2_NSI/Cours/Première NSI Pierrot caillabet/2_2020-2021/Bloc 3_Types construits-Traitement données en tables/types_construits_python-v2.pdf`.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : P-DATA-CONSTR-01.
2. P-DATA-CONSTR-01 : choisir une structure selon l’accès attendu.
3. Identifier les données d’entrée de tuples puis écrire le résultat attendu avant de conclure.
4. Contrôler tuples par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance P04 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Le tuple `point = (3, 5)` regroupe deux coordonnées liées. La fonction `milieu((1, 2), (5, 8))` renvoie `((1+5)/2, (2+8)/2)`, donc `(3.0, 5.0)`. On ne modifie pas directement `point[0]` : si une nouvelle coordonnée est nécessaire, on construit un nouveau tuple.
### Exemple corrigé 2 - Contrôle ou contre-exemple
La liste `temperatures = [18, 20, 19]` accepte `temperatures[1] = 21`, car elle est mutable. Le tuple `coord = (18, 20)` refuserait `coord[1] = 21`. Le choix de structure dépend donc de l’opération attendue : modifier une série ou figer un couple de valeurs.

## Erreurs fréquentes
- Confondre le vocabulaire de tuples avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de tuples, listes et dictionnaires : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur types construits : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour tuples, à traiter selon la convention du chapitre P04.
- Donnée invalide dans tuples, listes et dictionnaires, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de types construits où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
P-DATA-CONSTR-01 : appliquer la méthode de tuples à un exemple court choisi dans le chapitre P04.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de tuples, listes et dictionnaires.
### Mini-exercice 3
Proposer un cas limite pertinent pour types construits et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour tuples.

## Réponses rapides
1. La méthode attendue pour tuples commence par les données puis applique l’opération du chapitre P04.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans tuples, listes et dictionnaires.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon types construits.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de tuples.

## À retenir
- P04 : tuples se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités P-DATA-CONSTR-01 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de types construits doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour P04, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche P04 sur tuples reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P04-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/premiere/P04/P04_td_types_construits.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/premiere/P04/P04_tp_types_construits.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/premiere/P04/P04_evaluation_types_construits.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer tuples avec un exemple différent de ceux de la fiche P04.
- Je peux citer au moins une capacité parmi P-DATA-CONSTR-01 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à P04 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de types construits sans transformer la fiche en corrigé complet.
