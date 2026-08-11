---
title: "Audit qualité - s01_structures_donnees_interfaces_implementations"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "structures de données, interfaces et implémentations"
objectifs: "Auditer séparément les documents de la séquence pilote Terminale après refonte."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Audit qualité - s01_structures_donnees_interfaces_implementations

## Périmètre

Séquence auditée : `terminale/sequences/s01_structures_donnees_interfaces_implementations/`.

Documents inspectés : [cours_eleve.md](./cours_eleve.md), [trace_ecrite.md](./trace_ecrite.md), [td.md](./td.md), [tp.md](./tp.md), [corrige.md](./corrige.md), [guide_professeur.md](./guide_professeur.md), [evaluation.md](./evaluation.md), [qcm.json](./qcm.json), [projet_associe.md](./projet_associe.md), [fiche_methode.md](./fiche_methode.md), [aides_progressives.md](./aides_progressives.md).

Fichiers techniques inspectés : [python/structures_tools.py](./python/structures_tools.py), [tests/test_structures_tools.py](./tests/test_structures_tools.py).

Statut général : `needs_review`.

Aucune publication n'est déclarée pour cette séquence.

## Décision sur le titre

L'ancien dossier centré sur les graphes a été renommé.

Nom retenu : `s01_structures_donnees_interfaces_implementations`.

La séquence pose les bases : structure abstraite, interface, implémentation, pile, file, dictionnaire, graphe comme relation.

BFS est limité à une activité d'application de la file.

ABR est signalé comme aperçu hors évaluation.

## Profondeur du cours

Le cours introduit les structures abstraites avant les algorithmes de parcours.

Il traite interface, implémentation, pile, file, dictionnaire, liste d'adjacence, matrice d'adjacence, coût comparé et choix selon problème.

Les exemples corrigés sont présents et reliés au TD ou au TP.

Les erreurs fréquentes ciblent la confusion pile/file, l'usage réflexe des listes et la représentation des graphes.

Point de vigilance : la densité conceptuelle exige probablement deux séances de manipulation avant le code.

## Qualité scientifique

Le vocabulaire interface/implémentation est installé.

La file est reliée au principe FIFO et la pile au principe LIFO.

Le dictionnaire est présenté comme association clé-valeur.

Le graphe est présenté comme structure relationnelle avant sa représentation.

La liste d'adjacence et la matrice d'adjacence sont comparées selon l'opération visée.

Point de vigilance : la complexité reste qualitative dans cette séquence ; les notations asymptotiques détaillées sont à réserver à une suite.

## Progressivité

La progression commence par des situations concrètes.

Elle passe ensuite aux interfaces, puis aux implémentations Python.

Les graphes arrivent après pile, file et dictionnaire.

Le TP demande d'abord la construction des structures avant tout parcours.

Point de vigilance : ne pas laisser l'activité BFS absorber le temps de synthèse.

## Exercices

Le TD comporte des exercices de niveau socle, standard et expert.

Il inclut analyse de code, écriture de code, justification et comparaison de coût.

Il demande explicitement de choisir une structure selon un besoin.

Point de vigilance : vérifier que les élèves formulent les justifications avant de coder.

## TP

Le TP porte sur un mini-réseau et utilise [python/structures_tools.py](./python/structures_tools.py).

Il impose des fichiers fournis, des étapes, des tests, un livrable, des critères de réussite, des aides progressives et une extension experte.

Point de vigilance : préparer un rappel sur dictionnaires de listes si la classe en a besoin.

## Corrigé

Le corrigé traite les exercices, le TP, l'évaluation et les cas limites.

Il fournit des variantes acceptables et des erreurs fréquentes.

Point de vigilance : les solutions de code doivent rester alignées avec le niveau Terminale sans introduire de bibliothèque non nécessaire.

## Guide professeur

Le guide propose objectifs, durée, scénario séance par séance, difficultés, remédiations, différenciation, questions orales, critères et prolongements.

Il explicite le déplacement d'ABR vers une séquence ultérieure.

Point de vigilance : la séquence doit être reliée plus tard aux parcours de graphes et aux arbres.

## QCM

Le QCM contient au moins huit questions.

Chaque question comporte difficulté, capacité officielle, erreur ciblée et explications par proposition.

Point de vigilance : les questions expertes doivent rester des vérifications de raisonnement, pas des questions de performance Python.

## Évaluation

L'évaluation porte sur interface/implémentation, pile/file, dictionnaire, graphe, représentation et justification.

Elle contient une programmation courte avec file explicite.

Le corrigé lié est [corrige.md](./corrige.md).

Point de vigilance : l'accès à Python pendant l'épreuve doit être décidé avant passation.

## Différenciation

Les aides progressives décomposent le choix de structure en niveaux.

La fiche méthode fournit une grille de décision.

Le projet associé propose version minimale, standard et experte.

Point de vigilance : le vocabulaire abstrait peut nécessiter des supports manipulables.

## Cohérence avec programme officiel

Les preuves explicites sont déclarées dans le frontmatter.

La séquence cible les capacités relatives à l'interface, l'implémentation, les piles, files, dictionnaires et graphes.

Les capacités sur arbres binaires, ABR, parcours de graphes avancés et programmation dynamique ne sont pas déclarées couvertes par cette séquence.

La couverture globale du programme reste partielle tant que toutes les rubriques ne sont pas appuyées par des preuves.

## Bloquants restants

Aucune ressource Drive n'est intégrée.

Aucun statut final n'est attribué.

Une relecture pédagogique et scientifique externe reste nécessaire.

Les preuves de terrain en classe ne sont pas disponibles.

## Conclusion d'audit

La séquence est une base pilote en `needs_review`.

Elle n'est pas une ressource publiable.
