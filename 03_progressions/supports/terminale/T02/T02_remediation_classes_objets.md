---
title: "T02 - Remediation - Classes et objets"
level: "terminale"
sequence_id: "T02"
document_type: "remediation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Programmation orientée objet"
notion: "classe, attribut, méthode, invariant"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-02A"
---


# T02 - Remédiation - Classes et objets

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-02A

## Prérequis
- Reconnaître une consigne liée à classe.
- Distinguer donnée, méthode et conclusion dans le thème Programmation orientée objet.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T02-S1 à T02-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une application de gestion de comptes doit garantir qu’aucune opération ne crée un solde incohérent.

## Activité d’entrée
1. Identifier attributs et méthodes d’un compte.
2. Écrire l’invariant `solde >= 0`.
3. Prévoir un dépôt puis un retrait.
4. Décider quoi faire si le retrait dépasse le solde.

### Remédiation EF1
- Erreur fréquente EF1 - Modifier directement un attribut sans passer par la méthode.
- Diagnostic : refaire constructeur avec `Compte("Ada", 20)` et repérer l’étape fautive.
- Activité corrective EF1 : Tracer l’état avant et après chaque méthode.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « solde initial négatif ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF2
- Erreur fréquente EF2 - Oublier de maintenir l’invariant.
- Diagnostic : refaire méthode dépôt avec dépôt de 15 et repérer l’étape fautive.
- Activité corrective EF2 : Écrire l’invariant en marge de chaque opération.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « montant nul ou négatif ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF3
- Erreur fréquente EF3 - Utiliser une variable globale pour l’état de l’objet.
- Diagnostic : refaire méthode retrait avec retrait de 7 sur solde 20 et repérer l’étape fautive.
- Activité corrective EF3 : Créer deux comptes pour vérifier l’indépendance des états.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « retrait supérieur au solde ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF4
- Erreur fréquente EF4 - Confondre classe et instance.
- Diagnostic : refaire représentation avec `repr(compte)` et repérer l’étape fautive.
- Activité corrective EF4 : Colorer définition de classe, constructeur et instance.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « nom vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
## Exercices numérotés
- Exercice 1 : résoudre constructeur avec `Compte("Ada", 20)` ; attendu : propriétaire Ada, solde 20.
- Exercice 2 : expliquer méthode dépôt à partir de dépôt de 15 ; attendu : solde augmenté de 15.
- Exercice 3 : comparer méthode retrait avec retrait de 7 sur solde 20 ; attendu : solde 13.
- Exercice 4 : corriger représentation pour `repr(compte)` ; attendu : résumé lisible.
- Exercice 5 : tester un cas limite lié à solde initial négatif ; attendu : le comportement de constructeur est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour méthode dépôt ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise méthode retrait avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur représentation ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `Compte("Ada", 20)`, appliquer la méthode « initialiser les attributs après validation », puis écrire propriétaire Ada, solde 20 ; résultat : propriétaire Ada, solde 20 ; contrôle : faire apparaître le contrôle « solde initial négatif ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de vérifier le montant puis modifier le solde avant de conclure par solde augmenté de 15 ; résultat : solde augmenté de 15 ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « retrait supérieur au solde » et valider solde 13 ; résultat : solde 13 ; contrôle : comparer avec le cas « retrait supérieur au solde ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Confondre classe et instance. » puis reprendre la procédure correcte ; résultat : résumé lisible ; contrôle : corriger l’erreur « Confondre classe et instance. ».
- Corrigé exercice 5 : méthode : identifier `Compte("Ada", 20)`, appliquer la méthode « initialiser les attributs après validation », puis écrire propriétaire Ada, solde 20 ; résultat : le comportement de constructeur est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de vérifier le montant puis modifier le solde avant de conclure par solde augmenté de 15 ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Oublier de maintenir l’invariant. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « retrait supérieur au solde » et valider solde 13 ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Confondre classe et instance. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Colorer définition de classe, constructeur et instance. ».

## Erreurs fréquentes
- Erreur fréquente EF1 - Modifier directement un attribut sans passer par la méthode.
- Erreur fréquente EF2 - Oublier de maintenir l’invariant.
- Erreur fréquente EF3 - Utiliser une variable globale pour l’état de l’objet.
- Erreur fréquente EF4 - Confondre classe et instance.

## Remédiation ciblée
- Activité corrective EF1 : Tracer l’état avant et après chaque méthode.
- Activité corrective EF2 : Écrire l’invariant en marge de chaque opération.
- Activité corrective EF3 : Créer deux comptes pour vérifier l’indépendance des états.
- Activité corrective EF4 : Colorer définition de classe, constructeur et instance.

## Différenciation
- Socle : traiter `Compte("Ada", 20)` avec une fiche méthode fournie.
- Standard : traiter dépôt de 15 en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « retrait supérieur au solde » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
