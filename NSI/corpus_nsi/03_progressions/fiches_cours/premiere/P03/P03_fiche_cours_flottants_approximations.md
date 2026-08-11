---
title: "P03 - Fiche cours - Flottants et approximations"
level: "premiere"
sequence_id: "P03"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation des réels"
notion: "flottants"
official_program:
  capacities:
    - "P-DATA-BASE-03"
readiness: operational
private_data: false
---
# P03 - Fiche cours - Flottants et approximations

## À savoir
- texte, Unicode et flottants se travaille dans le contexte “octets et approximations” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour flottants.
- Les capacités P-DATA-BASE-03 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de texte, Unicode et flottants avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : P-DATA-BASE-03.
2. P-DATA-BASE-03 : distinguer caractère, encodage et approximation numérique.
3. Identifier les données d’entrée de flottants puis écrire le résultat attendu avant de conclure.
4. Contrôler flottants par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance P03 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
`é` a pour point de code 233 et s’encode en UTF-8 par les octets C3 A9.
### Exemple corrigé 2 - Contrôle ou contre-exemple
`0.1 + 0.2` peut produire `0.30000000000000004`, d’où un test avec tolérance.

## Erreurs fréquentes
- Confondre le vocabulaire de flottants avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de octets et approximations : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur texte, Unicode et flottants : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour flottants, à traiter selon la convention du chapitre P03.
- Donnée invalide dans octets et approximations, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de texte, Unicode et flottants où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
P-DATA-BASE-03 : appliquer la méthode de flottants à un exemple court choisi dans le chapitre P03.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de octets et approximations.
### Mini-exercice 3
Proposer un cas limite pertinent pour texte, Unicode et flottants et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour flottants.

## Réponses rapides
1. La méthode attendue pour flottants commence par les données puis applique l’opération du chapitre P03.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans octets et approximations.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon texte, Unicode et flottants.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de flottants.

## À retenir
- P03 : flottants se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités P-DATA-BASE-03 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de texte, Unicode et flottants doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour P03, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche P03 sur flottants reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P03-S1 | prête | séance présente dans la progression |
| TD | 03_progressions/supports/premiere/P03/P03_td_texte_reels.md | existant | support associé existant dans 03_progressions/supports |
| TP | 03_progressions/supports/premiere/P03/P03_tp_texte_reels.md | existant | support associé existant dans 03_progressions/supports |
| Évaluation | 03_progressions/supports/premiere/P03/P03_evaluation_texte_reels.md | existant | support associé existant dans 03_progressions/supports |

## Auto-évaluation
- Je peux expliquer flottants avec un exemple différent de ceux de la fiche P03.
- Je peux citer au moins une capacité parmi P-DATA-BASE-03 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à P03 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de texte, Unicode et flottants sans transformer la fiche en corrigé complet.
