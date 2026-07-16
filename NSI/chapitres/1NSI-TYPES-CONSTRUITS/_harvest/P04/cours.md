---
title: "P04 - Cours - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Tuples, listes, dictionnaires"
notion: "tuple, liste, dictionnaire, mutabilité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-CONSTR-02A"
    - "P-DATA-CONSTR-02D"
---

# P04 - Cours - Types construits

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-CONSTR-02A
- P-DATA-CONSTR-02D

## Prérequis
- Reconnaître une consigne liée à tuple.
- Distinguer donnée, méthode et conclusion dans le thème Tuples, listes, dictionnaires.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P04-S1 à P04-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une station météo stocke des coordonnées fixes, des relevés horaires modifiables et des mesures accessibles par nom.

## Activité d’entrée
1. Identifier ce qui doit rester immuable dans un tuple.
2. Modifier une liste de températures.
3. Lire une clé dans un dictionnaire de station.
4. Décrire ce qui se passe avec une liste vide.

## Définitions et formalisation
- Définition D1 : tuple est utilisé dans Tuples, listes, dictionnaires avec une donnée, une règle et un contrôle.
- Définition D2 : liste est utilisé dans Tuples, listes, dictionnaires avec une donnée, une règle et un contrôle.
- Définition D3 : dictionnaire est utilisé dans Tuples, listes, dictionnaires avec une donnée, une règle et un contrôle.
- Définition D4 : mutabilité est utilisé dans Tuples, listes, dictionnaires avec une donnée, une règle et un contrôle.
- Cas limite principal : tentative de modification interdite.

## Exemples corrigés précis
### Exemple corrigé 1 - tuple de coordonnées
- Donnée étudiée : `(36.8, 10.2)`.
- Méthode : lire sans modifier et nommer latitude puis longitude.
- Résultat obtenu : coordonnées conservées.
- Contrôle : le cas limite « tentative de modification interdite » est vérifié séparément.
### Exemple corrigé 2 - liste de relevés
- Donnée étudiée : `[18, 20, 19]`.
- Méthode : parcourir les valeurs et calculer une moyenne.
- Résultat obtenu : `19`.
- Contrôle : le cas limite « liste vide » est vérifié séparément.
### Exemple corrigé 3 - dictionnaire
- Donnée étudiée : `{"temperature": 21, "vent": 12}`.
- Méthode : tester la présence de la clé avant lecture.
- Résultat obtenu : `21` pour `temperature`.
- Contrôle : le cas limite « clé absente » est vérifié séparément.
### Exemple corrigé 4 - copie de liste
- Donnée étudiée : `[[1], [2]]`.
- Méthode : distinguer copie superficielle et copie indépendante.
- Résultat obtenu : modification locale contrôlée.
- Contrôle : le cas limite « liste imbriquée » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-DATA-CONSTR-02A.
- Point de départ : `(36.8, 10.2)`.
- Angle disciplinaire : repérage initial autour de tuple de coordonnées.
- Démarche attendue : lire sans modifier et nommer latitude puis longitude.
- Exemple associé : coordonnées conservées.
- Point de vigilance : Modifier un tuple comme une liste.
- Activité de reprise associée : Identifier mutabilité et usage avant d’écrire une affectation.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-DATA-CONSTR-02A.
- Point de départ : `[18, 20, 19]`.
- Angle disciplinaire : méthode guidée autour de liste de relevés.
- Démarche attendue : parcourir les valeurs et calculer une moyenne.
- Exemple associé : `19`.
- Point de vigilance : Parcourir les indices quand les valeurs suffisent.
- Activité de reprise associée : Écrire deux boucles, avec indices puis avec valeurs, et comparer.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-DATA-CONSTR-02A.
- Point de départ : `{"temperature": 21, "vent": 12}`.
- Angle disciplinaire : transfert argumenté autour de dictionnaire.
- Démarche attendue : tester la présence de la clé avant lecture.
- Exemple associé : `21` pour `temperature`.
- Point de vigilance : Accéder à une clé sans vérifier sa présence.
- Activité de reprise associée : Tester `cle in dictionnaire` avant la lecture.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-DATA-CONSTR-02A.
- Point de départ : `[[1], [2]]`.
- Angle disciplinaire : vérification critique autour de copie de liste.
- Démarche attendue : distinguer copie superficielle et copie indépendante.
- Exemple associé : modification locale contrôlée.
- Point de vigilance : Copier une liste imbriquée seulement au premier niveau.
- Activité de reprise associée : Modifier une sous-liste et observer l’effet sur la copie.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre tuple de coordonnées avec `(36.8, 10.2)` ; attendu : coordonnées conservées.
- Exercice 2 : expliquer liste de relevés à partir de `[18, 20, 19]` ; attendu : `19`.
- Exercice 3 : comparer dictionnaire avec `{"temperature": 21, "vent": 12}` ; attendu : `21` pour `temperature`.
- Exercice 4 : corriger copie de liste pour `[[1], [2]]` ; attendu : modification locale contrôlée.
- Exercice 5 : tester un cas limite lié à tentative de modification interdite ; attendu : le comportement de tuple de coordonnées est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste de relevés ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur copie de liste ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées ; résultat : coordonnées conservées ; contrôle : faire apparaître le contrôle « tentative de modification interdite ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19` ; résultat : `19` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature` ; résultat : `21` pour `temperature` ; contrôle : comparer avec le cas « clé absente ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte ; résultat : modification locale contrôlée ; contrôle : corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. ».
- Corrigé exercice 5 : méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées ; résultat : le comportement de tuple de coordonnées est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Modifier un tuple comme une liste.
- Erreur fréquente EF2 - Parcourir les indices quand les valeurs suffisent.
- Erreur fréquente EF3 - Accéder à une clé sans vérifier sa présence.
- Erreur fréquente EF4 - Copier une liste imbriquée seulement au premier niveau.

## Remédiation ciblée
- Activité corrective EF1 : Identifier mutabilité et usage avant d’écrire une affectation.
- Activité corrective EF2 : Écrire deux boucles, avec indices puis avec valeurs, et comparer.
- Activité corrective EF3 : Tester `cle in dictionnaire` avant la lecture.
- Activité corrective EF4 : Modifier une sous-liste et observer l’effet sur la copie.

## Différenciation
- Socle : traiter `(36.8, 10.2)` avec une fiche méthode fournie.
- Standard : traiter `[18, 20, 19]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « clé absente » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre tuple de coordonnées avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « tentative de modification interdite » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre liste de relevés avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « liste vide » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre dictionnaire avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « clé absente » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre copie de liste avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « liste imbriquée » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier tuple de coordonnées à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier liste de relevés à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier dictionnaire à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier copie de liste à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- tuple : terme à employer dans une justification écrite de la séquence.
- liste : terme à employer dans une justification écrite de la séquence.
- dictionnaire : terme à employer dans une justification écrite de la séquence.
- mutabilité : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P04-A : modifier la donnée du premier exemple de P04 - Cours - Types construits et conserver exactement la même méthode.
- Variante P04-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P04-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P04-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P04-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P04-F : construire une donnée minimale qui force une décision de méthode.
- Variante P04-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P04-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P04-I : relier une erreur fréquente à une activité corrective précise.
- Variante P04-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P04-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P04-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P04-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P04-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P04-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P04-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
