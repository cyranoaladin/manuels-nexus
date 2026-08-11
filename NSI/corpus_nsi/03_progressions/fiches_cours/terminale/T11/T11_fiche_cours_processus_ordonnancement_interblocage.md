---
title: "T11 - Fiche cours - Processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Systèmes"
notion: "processus"
official_program:
  capacities:
    - "T-ARCH-01"
    - "T-ARCH-02A"
    - "T-ARCH-02B"
    - "T-ARCH-02C"
readiness: operational
private_data: false
---
# T11 - Fiche cours - Processus, ordonnancement et interblocage

## À savoir
- processus et ordonnancement se travaille dans le contexte “systèmes” avec des données vérifiables.
- La fiche distingue vocabulaire, méthode, exemple corrigé et contrôle pour processus.
- Les capacités T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C sont rappelées ici sans être déclarées couvertes.
- L’élève doit pouvoir refaire un exemple de processus et ordonnancement avec une valeur, une table ou un code différent.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C.
2. T-ARCH-01 : suivre états prêt, élu et bloqué.
3. Identifier les données d’entrée de processus puis écrire le résultat attendu avant de conclure.
4. Contrôler processus par un cas limite explicite et une vérification courte.
5. Relier la réponse à un support de séance T11 sans confondre fiche de révision et preuve de couverture.

## Exemples corrigés
### Exemple corrigé 1 - Exemple principal
Un processus qui attend une lecture disque passe de élu à bloqué.
### Exemple corrigé 2 - Contrôle ou contre-exemple
P1 détient A et attend B pendant que P2 détient B et attend A : interblocage.

## Erreurs fréquentes
- Confondre le vocabulaire de processus avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de systèmes : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur processus et ordonnancement : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour processus, à traiter selon la convention du chapitre T11.
- Donnée invalide dans systèmes, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de processus et ordonnancement où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-ARCH-01 : appliquer la méthode de processus à un exemple court choisi dans le chapitre T11.
### Mini-exercice 2
Repérer l’erreur dans une réponse qui oublie une hypothèse de systèmes.
### Mini-exercice 3
Proposer un cas limite pertinent pour processus et ordonnancement et expliquer le résultat attendu.
### Mini-exercice 4
Écrire une phrase de contrôle qui vérifie la conclusion obtenue pour processus.

## Réponses rapides
1. La méthode attendue pour processus commence par les données puis applique l’opération du chapitre T11.
2. L’erreur vient de l’hypothèse manquante ; elle se corrige en testant le cas mentionné dans systèmes.
3. Le cas limite doit donner un résultat explicite, par exemple 0, vide, absent ou hors plage selon processus et ordonnancement.
4. Le contrôle compare le résultat avec la définition ou avec une opération inverse de processus.

## À retenir
- T11 : processus se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de processus et ordonnancement doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T11, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T11 sur processus reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T11-S1 | réelle | séance présente dans la progression |
| TD | T11_TD_processus_ordonnancement_interblocage.md | existant | support TD créé en needs_review |
| Évaluation | T11_evaluation_processus_ordonnancement_interblocage.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer processus avec un exemple différent de ceux de la fiche T11.
- Je peux citer au moins une capacité parmi T-ARCH-01, T-ARCH-02A, T-ARCH-02B, T-ARCH-02C et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T11 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de processus et ordonnancement sans transformer la fiche en corrigé complet.
