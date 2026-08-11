---
title: "T03 - Cours - Piles, files et dictionnaires"
level: "terminale"
sequence_id: "T03"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "pile, file, dictionnaire, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03A"
    - "T-STRUCT-03B"
---

# T03 - Cours - Piles, files et dictionnaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-03A
- T-STRUCT-03B

## Prérequis
- Reconnaître une consigne liée à pile.
- Distinguer donnée, méthode et conclusion dans le thème Structures linéaires et tables associatives.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T03-S1 à T03-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un serveur journalise des tâches en attente et doit choisir entre pile, file et dictionnaire selon l’usage.

## Activité d’entrée
1. Simuler une pile sur trois opérations.
2. Simuler une file sur trois clients.
3. Utiliser un dictionnaire pour retrouver une tâche par identifiant.
4. Comparer coût de recherche et d’accès direct.

## Définitions et formalisation
- Définition D1 : pile est utilisé dans Structures linéaires et tables associatives avec une donnée, une règle et un contrôle.
- Définition D2 : file est utilisé dans Structures linéaires et tables associatives avec une donnée, une règle et un contrôle.
- Définition D3 : dictionnaire est utilisé dans Structures linéaires et tables associatives avec une donnée, une règle et un contrôle.
- Définition D4 : complexité est utilisé dans Structures linéaires et tables associatives avec une donnée, une règle et un contrôle.
- Cas limite principal : pile vide.

## Exemples corrigés précis
### Exemple corrigé 1 - pile
- Donnée étudiée : empiler A puis B, dépiler.
- Méthode : appliquer LIFO.
- Résultat obtenu : B sort en premier.
- Contrôle : le cas limite « pile vide » est vérifié séparément.
### Exemple corrigé 2 - file
- Donnée étudiée : enfiler A puis B, défiler.
- Méthode : appliquer FIFO.
- Résultat obtenu : A sort en premier.
- Contrôle : le cas limite « file vide » est vérifié séparément.
### Exemple corrigé 3 - dictionnaire
- Donnée étudiée : `{"id7": "ok"}`.
- Méthode : tester la clé puis accéder.
- Résultat obtenu : `ok`.
- Contrôle : le cas limite « clé absente » est vérifié séparément.
### Exemple corrigé 4 - complexité
- Donnée étudiée : accès par identifiant.
- Méthode : choisir dictionnaire plutôt que parcours linéaire.
- Résultat obtenu : accès attendu constant.
- Contrôle : le cas limite « collision abstraite hors programme » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-STRUCT-03A.
- Point de départ : empiler A puis B, dépiler.
- Angle disciplinaire : repérage initial autour de pile.
- Démarche attendue : appliquer LIFO.
- Exemple associé : B sort en premier.
- Point de vigilance : Inverser LIFO et FIFO.
- Activité de reprise associée : Jouer les opérations avec des cartes empilées puis alignées.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-STRUCT-03A.
- Point de départ : enfiler A puis B, défiler.
- Angle disciplinaire : méthode guidée autour de file.
- Démarche attendue : appliquer FIFO.
- Exemple associé : A sort en premier.
- Point de vigilance : Retirer dans une structure vide sans test.
- Activité de reprise associée : Écrire le test `est_vide` avant chaque retrait.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-STRUCT-03A.
- Point de départ : `{"id7": "ok"}`.
- Angle disciplinaire : transfert argumenté autour de dictionnaire.
- Démarche attendue : tester la clé puis accéder.
- Exemple associé : `ok`.
- Point de vigilance : Parcourir tout un dictionnaire pour une clé connue.
- Activité de reprise associée : Remplacer une boucle de recherche par un accès par clé.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-STRUCT-03A.
- Point de départ : accès par identifiant.
- Angle disciplinaire : vérification critique autour de complexité.
- Démarche attendue : choisir dictionnaire plutôt que parcours linéaire.
- Exemple associé : accès attendu constant.
- Point de vigilance : Confondre clé et valeur.
- Activité de reprise associée : Surligner clés et valeurs de couleurs différentes.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre pile avec empiler A puis B, dépiler ; attendu : B sort en premier.
- Exercice 2 : expliquer file à partir de enfiler A puis B, défiler ; attendu : A sort en premier.
- Exercice 3 : comparer dictionnaire avec `{"id7": "ok"}` ; attendu : `ok`.
- Exercice 4 : corriger complexité pour accès par identifiant ; attendu : accès attendu constant.
- Exercice 5 : tester un cas limite lié à pile vide ; attendu : le comportement de pile est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour file ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur complexité ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier empiler A puis B, dépiler, appliquer la méthode « appliquer LIFO », puis écrire B sort en premier ; résultat : B sort en premier ; contrôle : faire apparaître le contrôle « pile vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de appliquer FIFO avant de conclure par A sort en premier ; résultat : A sort en premier ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `ok` ; résultat : `ok` ; contrôle : comparer avec le cas « clé absente ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Confondre clé et valeur. » puis reprendre la procédure correcte ; résultat : accès attendu constant ; contrôle : corriger l’erreur « Confondre clé et valeur. ».
- Corrigé exercice 5 : méthode : identifier empiler A puis B, dépiler, appliquer la méthode « appliquer LIFO », puis écrire B sort en premier ; résultat : le comportement de pile est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de appliquer FIFO avant de conclure par A sort en premier ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Retirer dans une structure vide sans test. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `ok` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Confondre clé et valeur. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Surligner clés et valeurs de couleurs différentes. ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Inverser LIFO et FIFO.
- Erreur fréquente EF2 - Retirer dans une structure vide sans test.
- Erreur fréquente EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Erreur fréquente EF4 - Confondre clé et valeur.

## Remédiation ciblée
- Activité corrective EF1 : Jouer les opérations avec des cartes empilées puis alignées.
- Activité corrective EF2 : Écrire le test `est_vide` avant chaque retrait.
- Activité corrective EF3 : Remplacer une boucle de recherche par un accès par clé.
- Activité corrective EF4 : Surligner clés et valeurs de couleurs différentes.

## Différenciation
- Socle : traiter empiler A puis B, dépiler avec une fiche méthode fournie.
- Standard : traiter enfiler A puis B, défiler en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « clé absente » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre pile avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « pile vide » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre file avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « file vide » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre dictionnaire avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « clé absente » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre complexité avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « collision abstraite hors programme » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier pile à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier file à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier dictionnaire à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier complexité à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- pile : terme à employer dans une justification écrite de la séquence.
- file : terme à employer dans une justification écrite de la séquence.
- dictionnaire : terme à employer dans une justification écrite de la séquence.
- complexité : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante T03-A : modifier la donnée du premier exemple de T03 - Cours - Piles, files et dictionnaires et conserver exactement la même méthode.
- Variante T03-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T03-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T03-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T03-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T03-F : construire une donnée minimale qui force une décision de méthode.
- Variante T03-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T03-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T03-I : relier une erreur fréquente à une activité corrective précise.
- Variante T03-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T03-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T03-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T03-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T03-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T03-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T03-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
