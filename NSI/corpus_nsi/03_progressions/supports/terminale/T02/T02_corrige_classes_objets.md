---
title: "T02 - Corrige - Classes et objets"
level: "terminale"
sequence_id: "T02"
document_type: "corrige"
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


# T02 - Corrigé professeur - Classes et objets

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

## Méthode générale de correction
- Point 1 : pour constructeur, exiger la donnée `Compte("Ada", 20)`, la méthode « initialiser les attributs après validation » et le contrôle « solde initial négatif ».
- Point 2 : pour méthode dépôt, exiger la donnée dépôt de 15, la méthode « vérifier le montant puis modifier le solde » et le contrôle « montant nul ou négatif ».
- Point 3 : pour méthode retrait, exiger la donnée retrait de 7 sur solde 20, la méthode « contrôler disponibilité puis soustraire » et le contrôle « retrait supérieur au solde ».
- Point 4 : pour représentation, exiger la donnée `repr(compte)`, la méthode « exposer une chaîne utile sans révéler de données inutiles » et le contrôle « nom vide ».
## Exercices numérotés
- Exercice 1 : résoudre constructeur avec `Compte("Ada", 20)` ; attendu : propriétaire Ada, solde 20.
- Exercice 2 : expliquer méthode dépôt à partir de dépôt de 15 ; attendu : solde augmenté de 15.
- Exercice 3 : comparer méthode retrait avec retrait de 7 sur solde 20 ; attendu : solde 13.
- Exercice 4 : corriger représentation pour `repr(compte)` ; attendu : résumé lisible.
- Exercice 5 : tester un cas limite lié à solde initial négatif ; attendu : le comportement de constructeur est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour méthode dépôt ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise méthode retrait avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur représentation ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `Compte("Ada", 20)`, appliquer la méthode « initialiser les attributs après validation », puis écrire propriétaire Ada, solde 20.
- Résultat : propriétaire Ada, solde 20.
- Contrôle : faire apparaître le contrôle « solde initial négatif ».
- Erreur traitée : EF1 - Modifier directement un attribut sans passer par la méthode.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de vérifier le montant puis modifier le solde avant de conclure par solde augmenté de 15.
- Résultat : solde augmenté de 15.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Oublier de maintenir l’invariant.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « retrait supérieur au solde » et valider solde 13.
- Résultat : solde 13.
- Contrôle : comparer avec le cas « retrait supérieur au solde ».
- Erreur traitée : EF3 - Utiliser une variable globale pour l’état de l’objet.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Confondre classe et instance. » puis reprendre la procédure correcte.
- Résultat : résumé lisible.
- Contrôle : corriger l’erreur « Confondre classe et instance. ».
- Erreur traitée : EF4 - Confondre classe et instance.
### Corrigé exercice 5
- Méthode : identifier `Compte("Ada", 20)`, appliquer la méthode « initialiser les attributs après validation », puis écrire propriétaire Ada, solde 20.
- Résultat : le comportement de constructeur est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Modifier directement un attribut sans passer par la méthode.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de vérifier le montant puis modifier le solde avant de conclure par solde augmenté de 15.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Oublier de maintenir l’invariant. » est une erreur.
- Erreur traitée : EF2 - Oublier de maintenir l’invariant.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « retrait supérieur au solde » et valider solde 13.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Utiliser une variable globale pour l’état de l’objet.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Confondre classe et instance. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Colorer définition de classe, constructeur et instance. ».
- Erreur traitée : EF4 - Confondre classe et instance.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « solde initial négatif » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « retrait supérieur au solde » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Confondre classe et instance. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Oublier de maintenir l’invariant. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Colorer définition de classe, constructeur et instance. » ».
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
