---
title: "T02 - Cours - Classes et objets"
level: "terminale"
sequence_id: "T02"
document_type: "cours"
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
    - "T-STRUCT-02B"
---

# T02 - Cours - Classes et objets

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

## Définitions et formalisation
- Définition D1 : classe est utilisé dans Programmation orientée objet avec une donnée, une règle et un contrôle.
- Définition D2 : attribut est utilisé dans Programmation orientée objet avec une donnée, une règle et un contrôle.
- Définition D3 : méthode est utilisé dans Programmation orientée objet avec une donnée, une règle et un contrôle.
- Définition D4 : invariant est utilisé dans Programmation orientée objet avec une donnée, une règle et un contrôle.
- Cas limite principal : solde initial négatif.

## Exemples corrigés précis
### Exemple corrigé 1 - constructeur
- Donnée étudiée : `Compte("Ada", 20)`.
- Méthode : initialiser les attributs après validation.
- Résultat obtenu : propriétaire Ada, solde 20.
- Contrôle : le cas limite « solde initial négatif » est vérifié séparément.
### Exemple corrigé 2 - méthode dépôt
- Donnée étudiée : dépôt de 15.
- Méthode : vérifier le montant puis modifier le solde.
- Résultat obtenu : solde augmenté de 15.
- Contrôle : le cas limite « montant nul ou négatif » est vérifié séparément.
### Exemple corrigé 3 - méthode retrait
- Donnée étudiée : retrait de 7 sur solde 20.
- Méthode : contrôler disponibilité puis soustraire.
- Résultat obtenu : solde 13.
- Contrôle : le cas limite « retrait supérieur au solde » est vérifié séparément.
### Exemple corrigé 4 - représentation
- Donnée étudiée : `repr(compte)`.
- Méthode : exposer une chaîne utile sans révéler de données inutiles.
- Résultat obtenu : résumé lisible.
- Contrôle : le cas limite « nom vide » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-STRUCT-02A.
- Point de départ : `Compte("Ada", 20)`.
- Angle disciplinaire : repérage initial autour de constructeur.
- Démarche attendue : initialiser les attributs après validation.
- Exemple associé : propriétaire Ada, solde 20.
- Point de vigilance : Modifier directement un attribut sans passer par la méthode.
- Activité de reprise associée : Tracer l’état avant et après chaque méthode.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-STRUCT-02A.
- Point de départ : dépôt de 15.
- Angle disciplinaire : méthode guidée autour de méthode dépôt.
- Démarche attendue : vérifier le montant puis modifier le solde.
- Exemple associé : solde augmenté de 15.
- Point de vigilance : Oublier de maintenir l’invariant.
- Activité de reprise associée : Écrire l’invariant en marge de chaque opération.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-STRUCT-02A.
- Point de départ : retrait de 7 sur solde 20.
- Angle disciplinaire : transfert argumenté autour de méthode retrait.
- Démarche attendue : contrôler disponibilité puis soustraire.
- Exemple associé : solde 13.
- Point de vigilance : Utiliser une variable globale pour l’état de l’objet.
- Activité de reprise associée : Créer deux comptes pour vérifier l’indépendance des états.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-STRUCT-02A.
- Point de départ : `repr(compte)`.
- Angle disciplinaire : vérification critique autour de représentation.
- Démarche attendue : exposer une chaîne utile sans révéler de données inutiles.
- Exemple associé : résumé lisible.
- Point de vigilance : Confondre classe et instance.
- Activité de reprise associée : Colorer définition de classe, constructeur et instance.
- Mini-production : produire une correction d’erreur avec un nouveau test.
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre constructeur avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « solde initial négatif » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre méthode dépôt avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « montant nul ou négatif » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre méthode retrait avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « retrait supérieur au solde » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre représentation avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « nom vide » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier constructeur à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier méthode dépôt à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier méthode retrait à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier représentation à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- classe : terme à employer dans une justification écrite de la séquence.
- attribut : terme à employer dans une justification écrite de la séquence.
- méthode : terme à employer dans une justification écrite de la séquence.
- invariant : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante T02-A : modifier la donnée du premier exemple de T02 - Cours - Classes et objets et conserver exactement la même méthode.
- Variante T02-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T02-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T02-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T02-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T02-F : construire une donnée minimale qui force une décision de méthode.
- Variante T02-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T02-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T02-I : relier une erreur fréquente à une activité corrective précise.
- Variante T02-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T02-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T02-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T02-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T02-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T02-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T02-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
