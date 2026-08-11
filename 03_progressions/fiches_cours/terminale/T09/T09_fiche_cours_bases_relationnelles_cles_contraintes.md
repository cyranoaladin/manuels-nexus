---
title: "T09 - Fiche cours - Bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "modèle relationnel"
official_program:
  capacities:
    - "T-BDD-01A"
    - "T-BDD-01B"
    - "T-BDD-01C"
    - "T-BDD-02"
readiness: operational
private_data: false
---
# T09 - Fiche cours - Bases relationnelles, clés et contraintes

## À savoir
- bases relationnelles se travaille dans le contexte “clés et contraintes” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour modèle relationnel.
- Les capacités T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de bases relationnelles avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02.
2. T-BDD-01A : identifier tables, clés primaires et références.
3. Identifier les données d’entrée de modèle relationnel puis écrire le résultat attendu avant de conclure.
4. Contrôler modèle relationnel par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T09 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
`Note.id_eleve` référence `Eleve.id_eleve` dans un schéma scolaire fictif.
### Exemple corrigé 2 - Contrôle ou contre-exemple
Une clé primaire dupliquée empêche d’identifier une ligne unique.

## Erreurs fréquentes
- Confondre le vocabulaire de modèle relationnel avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de clés et contraintes : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur bases relationnelles : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour modèle relationnel, à traiter selon la convention du chapitre T09.
- Donnée invalide dans clés et contraintes, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de bases relationnelles où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-BDD-01A : appliquer la méthode de modèle relationnel à un exemple court choisi dans le chapitre T09.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de clés et contraintes.
### Mini-exercice 3
Proposer un cas limite pertinent pour bases relationnelles et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour modèle relationnel.

## Réponses rapides
1. La méthode attendue pour modèle relationnel commence par les données puis applique l’opération du chapitre T09.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans clés et contraintes.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon bases relationnelles.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de modèle relationnel.

## À retenir
- T09 : modèle relationnel se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de bases relationnelles doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T09, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T09 sur modèle relationnel reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T09-S1 | réelle | séance présente dans la progression |
| TD | T09_TD_bases_relationnelles_cles_contraintes.md | existant | support produit en needs_review, non validé |
| Évaluation | T09_evaluation_bases_relationnelles_cles_contraintes.md | existant | support produit en needs_review, non validé |

## Auto-évaluation
- Je peux expliquer modèle relationnel avec un exemple différent de ceux de la fiche T09.
- Je peux citer au moins une capacité parmi T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T09 existe déjà ou existe ou reste explicitement qualifié.
- Je peux identifier un cas limite de bases relationnelles sans transformer la fiche en corrigé complet.
