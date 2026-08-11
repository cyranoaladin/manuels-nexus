---
title: "T14 - Fiche cours - Modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Langages"
notion: "modularité API"
official_program:
  capacities:
    - "T-LANG-03A"
    - "T-LANG-03B"
    - "T-LANG-03C"
    - "T-LANG-04A"
    - "T-LANG-04B"
    - "T-LANG-05"
readiness: operational
private_data: false
---
# T14 - Fiche cours - Modularité, API, paradigmes et bugs

## À savoir
- modularité, API et bugs se travaille dans le contexte “langages” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour modularité API.
- Les capacités T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de modularité, API et bugs avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05.
2. T-LANG-03A : découper le code et isoler les défauts.
3. Identifier les données d’entrée de modularité API puis écrire le résultat attendu avant de conclure.
4. Contrôler modularité API par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T14 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Un module `stats.py` expose `moyenne` et garde `verifier_liste` en auxiliaire.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Un bug sur liste vide se réduit à un test minimal avec `[]`.

## Erreurs fréquentes
- Confondre le vocabulaire de modularité API avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de langages : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur modularité, API et bugs : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour modularité API, à traiter selon la convention du chapitre T14.
- Donnée invalide dans langages, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de modularité, API et bugs où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-LANG-03A : appliquer la méthode de modularité API à un exemple court choisi dans le chapitre T14.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de langages.
### Mini-exercice 3
Proposer un cas limite pertinent pour modularité, API et bugs et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour modularité API.

## Réponses rapides
1. La méthode attendue pour modularité API commence par les données puis applique l’opération du chapitre T14.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans langages.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon modularité, API et bugs.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de modularité API.

## À retenir
- T14 : modularité API se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de modularité, API et bugs doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T14, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T14 sur modularité API reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T14-S1 | réelle | séance présente dans la progression |
| TD | T14_TD_modularite_api_paradigmes_bugs.md | existant | support TD créé en needs_review |
| Évaluation | T14_evaluation_modularite_api_paradigmes_bugs.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer modularité API avec un exemple différent de ceux de la fiche T14.
- Je peux citer au moins une capacité parmi T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T14 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de modularité, API et bugs sans transformer la fiche en corrigé complet.
