---
title: "T12 - Fiche cours - Routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Réseaux"
notion: "routage"
official_program:
  capacities:
    - "T-ARCH-03"
readiness: operational
private_data: false
---
# T12 - Fiche cours - Routage RIP et OSPF

## À savoir
- routage RIP et OSPF se travaille dans le contexte “réseaux Terminale” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour routage.
- Les capacités T-ARCH-03 sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de routage RIP et OSPF avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-ARCH-03.
2. T-ARCH-03 : comparer nombre de sauts et coût de liens.
3. Identifier les données d’entrée de routage puis écrire le résultat attendu avant de conclure.
4. Contrôler routage par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T12 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
RIP préfère un chemin de 2 sauts à un chemin de 4 sauts.
### Exemple corrigé 2 - Contrôle ou contre-exemple
OSPF peut préférer 2+2+2 à 1+10 car le coût total est plus faible.

## Erreurs fréquentes
- Confondre le vocabulaire de routage avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de réseaux Terminale : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur routage RIP et OSPF : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour routage, à traiter selon la convention du chapitre T12.
- Donnée invalide dans réseaux Terminale, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de routage RIP et OSPF où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-ARCH-03 : appliquer la méthode de routage à un exemple court choisi dans le chapitre T12.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de réseaux Terminale.
### Mini-exercice 3
Proposer un cas limite pertinent pour routage RIP et OSPF et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour routage.

## Réponses rapides
1. La méthode attendue pour routage commence par les données puis applique l’opération du chapitre T12.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans réseaux Terminale.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon routage RIP et OSPF.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de routage.

## À retenir
- T12 : routage se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-ARCH-03 restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de routage RIP et OSPF doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T12, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T12 sur routage reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T12-S1 | réelle | séance présente dans la progression |
| TD | T12_TD_routage_rip_ospf.md | existant | support TD créé en needs_review |
| Évaluation | T12_evaluation_routage_rip_ospf.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer routage avec un exemple différent de ceux de la fiche T12.
- Je peux citer au moins une capacité parmi T-ARCH-03 et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T12 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de routage RIP et OSPF sans transformer la fiche en corrigé complet.
