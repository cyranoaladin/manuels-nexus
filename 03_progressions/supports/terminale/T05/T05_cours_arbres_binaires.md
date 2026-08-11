---
title: "T05 - Cours - Arbres binaires"
level: "terminale"
sequence_id: "T05"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Arbres et algorithmes"
notion: "arbre binaire, racine, feuille, parcours"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-04A"
---

# T05 - Cours - Arbres binaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-04A

## Prérequis
- Reconnaître une consigne liée à arbre binaire.
- Distinguer donnée, méthode et conclusion dans le thème Arbres et algorithmes.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T05-S1 à T05-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une expression arithmétique est représentée par un arbre dont les feuilles sont des valeurs et les nœuds internes des opérateurs.

## Activité d’entrée
1. Repérer racine, fils gauche et fils droit.
2. Calculer la hauteur d’un arbre réduit à une feuille.
3. Lister un parcours préfixe.
4. Évaluer une expression simple.

## Définitions et formalisation
- Définition D1 : arbre binaire est utilisé dans Arbres et algorithmes avec une donnée, une règle et un contrôle.
- Définition D2 : racine est utilisé dans Arbres et algorithmes avec une donnée, une règle et un contrôle.
- Définition D3 : feuille est utilisé dans Arbres et algorithmes avec une donnée, une règle et un contrôle.
- Définition D4 : parcours est utilisé dans Arbres et algorithmes avec une donnée, une règle et un contrôle.
- Cas limite principal : arbre vide.

## Exemples corrigés précis
### Exemple corrigé 1 - arbre feuille
- Donnée étudiée : `7`.
- Méthode : reconnaître l’absence de fils.
- Résultat obtenu : hauteur 0.
- Contrôle : le cas limite « arbre vide » est vérifié séparément.
### Exemple corrigé 2 - hauteur
- Donnée étudiée : racine avec deux feuilles.
- Méthode : prendre 1 plus le maximum des hauteurs des sous-arbres.
- Résultat obtenu : hauteur 1.
- Contrôle : le cas limite « un seul fils » est vérifié séparément.
### Exemple corrigé 3 - parcours préfixe
- Donnée étudiée : `+ 2 3`.
- Méthode : visiter racine puis gauche puis droite.
- Résultat obtenu : `+, 2, 3`.
- Contrôle : le cas limite « nœud feuille » est vérifié séparément.
### Exemple corrigé 4 - évaluation
- Donnée étudiée : `(2 + 3) * 4`.
- Méthode : évaluer les sous-arbres avant l’opérateur parent.
- Résultat obtenu : `20`.
- Contrôle : le cas limite « division par zéro si opérateur `/` » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-STRUCT-04A.
- Point de départ : `7`.
- Angle disciplinaire : repérage initial autour de arbre feuille.
- Démarche attendue : reconnaître l’absence de fils.
- Exemple associé : hauteur 0.
- Point de vigilance : Confondre hauteur et nombre de nœuds.
- Activité de reprise associée : Calculer séparément hauteur gauche et droite.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-STRUCT-04A.
- Point de départ : racine avec deux feuilles.
- Angle disciplinaire : méthode guidée autour de hauteur.
- Démarche attendue : prendre 1 plus le maximum des hauteurs des sous-arbres.
- Exemple associé : hauteur 1.
- Point de vigilance : Oublier le cas arbre vide.
- Activité de reprise associée : Décider une convention pour l’arbre vide puis l’appliquer partout.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-STRUCT-04A.
- Point de départ : `+ 2 3`.
- Angle disciplinaire : transfert argumenté autour de parcours préfixe.
- Démarche attendue : visiter racine puis gauche puis droite.
- Exemple associé : `+, 2, 3`.
- Point de vigilance : Mélanger parcours préfixe et infixe.
- Activité de reprise associée : Écrire l’ordre de visite au-dessus de chaque nœud.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-STRUCT-04A.
- Point de départ : `(2 + 3) * 4`.
- Angle disciplinaire : vérification critique autour de évaluation.
- Démarche attendue : évaluer les sous-arbres avant l’opérateur parent.
- Exemple associé : `20`.
- Point de vigilance : Évaluer un opérateur avant ses opérandes.
- Activité de reprise associée : Remonter les valeurs depuis les feuilles vers la racine.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre arbre feuille avec `7` ; attendu : hauteur 0.
- Exercice 2 : expliquer hauteur à partir de racine avec deux feuilles ; attendu : hauteur 1.
- Exercice 3 : comparer parcours préfixe avec `+ 2 3` ; attendu : `+, 2, 3`.
- Exercice 4 : corriger évaluation pour `(2 + 3) * 4` ; attendu : `20`.
- Exercice 5 : tester un cas limite lié à arbre vide ; attendu : le comportement de arbre feuille est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour hauteur ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise parcours préfixe avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur évaluation ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0 ; résultat : hauteur 0 ; contrôle : faire apparaître le contrôle « arbre vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1 ; résultat : hauteur 1 ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3` ; résultat : `+, 2, 3` ; contrôle : comparer avec le cas « nœud feuille ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte ; résultat : `20` ; contrôle : corriger l’erreur « Évaluer un opérateur avant ses opérandes. ».
- Corrigé exercice 5 : méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0 ; résultat : le comportement de arbre feuille est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1 ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Oublier le cas arbre vide. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Remonter les valeurs depuis les feuilles vers la racine. ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Confondre hauteur et nombre de nœuds.
- Erreur fréquente EF2 - Oublier le cas arbre vide.
- Erreur fréquente EF3 - Mélanger parcours préfixe et infixe.
- Erreur fréquente EF4 - Évaluer un opérateur avant ses opérandes.

## Remédiation ciblée
- Activité corrective EF1 : Calculer séparément hauteur gauche et droite.
- Activité corrective EF2 : Décider une convention pour l’arbre vide puis l’appliquer partout.
- Activité corrective EF3 : Écrire l’ordre de visite au-dessus de chaque nœud.
- Activité corrective EF4 : Remonter les valeurs depuis les feuilles vers la racine.

## Différenciation
- Socle : traiter `7` avec une fiche méthode fournie.
- Standard : traiter racine avec deux feuilles en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « nœud feuille » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre arbre feuille avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « arbre vide » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre hauteur avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « un seul fils » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre parcours préfixe avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « nœud feuille » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre évaluation avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « division par zéro si opérateur `/` » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier arbre feuille à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier hauteur à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier parcours préfixe à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier évaluation à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- arbre binaire : terme à employer dans une justification écrite de la séquence.
- racine : terme à employer dans une justification écrite de la séquence.
- feuille : terme à employer dans une justification écrite de la séquence.
- parcours : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante T05-A : modifier la donnée du premier exemple de T05 - Cours - Arbres binaires et conserver exactement la même méthode.
- Variante T05-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T05-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T05-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T05-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T05-F : construire une donnée minimale qui force une décision de méthode.
- Variante T05-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T05-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T05-I : relier une erreur fréquente à une activité corrective précise.
- Variante T05-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T05-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T05-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T05-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T05-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T05-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T05-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
