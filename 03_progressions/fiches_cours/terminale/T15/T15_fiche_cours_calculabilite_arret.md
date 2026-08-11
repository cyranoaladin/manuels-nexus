---
title: "T15 - Fiche cours - Calculabilité et problème de l’arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Calculabilité"
notion: "arrêt"
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
readiness: operational
private_data: false
---
# T15 - Fiche cours - Calculabilité et problème de l’arrêt

## À savoir
- calculabilité et arrêt se travaille dans le contexte “programmes comme données” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour arrêt.
- Les capacités T-LANG-01A, T-LANG-01B, T-LANG-01C sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de calculabilité et arrêt avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-LANG-01A, T-LANG-01B, T-LANG-01C.
2. T-LANG-01A : distinguer exemple terminé et décision générale.
3. Identifier les données d’entrée de arrêt puis écrire le résultat attendu avant de conclure.
4. Contrôler arrêt par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T15 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
`while True: pass` est un programme qui ne termine pas.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Une fonction qui renvoie immédiatement 0 termine pour toute entrée.

## Erreurs fréquentes
- Confondre le vocabulaire de arrêt avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de programmes comme données : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur calculabilité et arrêt : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour arrêt, à traiter selon la convention du chapitre T15.
- Donnée invalide dans programmes comme données, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de calculabilité et arrêt où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-LANG-01A : appliquer la méthode de arrêt à un exemple court choisi dans le chapitre T15.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de programmes comme données.
### Mini-exercice 3
Proposer un cas limite pertinent pour calculabilité et arrêt et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour arrêt.

## Réponses rapides
1. La méthode attendue pour arrêt commence par les données puis applique l’opération du chapitre T15.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans programmes comme données.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon calculabilité et arrêt.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de arrêt.

## À retenir
- T15 : arrêt se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-LANG-01A, T-LANG-01B, T-LANG-01C restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de calculabilité et arrêt doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T15, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T15 sur arrêt reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T15-S1 | réelle | séance présente dans la progression |
| TD | T15_TD_calculabilite_arret.md | existant | support TD créé en needs_review |
| Évaluation | T15_evaluation_calculabilite_arret.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer arrêt avec un exemple différent de ceux de la fiche T15.
- Je peux citer au moins une capacité parmi T-LANG-01A, T-LANG-01B, T-LANG-01C et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T15 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de calculabilité et arrêt sans transformer la fiche en corrigé complet.
