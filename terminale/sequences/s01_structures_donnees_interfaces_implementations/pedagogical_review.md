---
title: "Revue pédagogique - s01_structures_donnees_interfaces_implementations"
niveau: terminale
source: "Revue interne prototype"
status: needs_review
version: "0.3.0"
notion: "structures de données, interfaces et implémentations"
objectifs: "Évaluer la cohérence pédagogique de la séquence pilote Terminale."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Revue pédagogique - s01_structures_donnees_interfaces_implementations

## Cohérence de la séquence

Le renommage clarifie l'intention : poser interface, implémentation et choix de structures.

La séquence reste dense.

Elle combine abstraction, pile, file, dictionnaire, graphe, représentations de graphes, BFS, DFS, modularité, bugs et aperçu ABR.

Elle doit rester un pilote de consolidation, pas une séquence publiée.

## Surcharge cognitive

Les élèves doivent passer d'une structure abstraite à du code Python puis à des graphes.

Les représentations par liste d'adjacence et matrice demandent déjà une abstraction forte.

BFS et DFS doivent rester une application ponctuelle.

ABR doit rester un aperçu non évalué.

## Points solides

La distinction interface/implémentation est mieux posée.

Pile et file sont reliées à LIFO/FIFO.

Les tests Python couvrent les structures vides et les graphes invalides.

La comparaison liste d'adjacence/matrice est présente.

Les documents professeurs signalent les limites.

## Points faibles

La séquence traite encore trop de notions pour une entrée Terminale.

Les classes apparaissent indirectement par les dataclasses.

Les dictionnaires, graphes et parcours devraient être séparés si la classe est fragile.

La modularité et la gestion des bugs sont présentes comme contexte, mais ne doivent pas être déclarées couvertes.

## Erreurs scientifiques possibles

Confondre structure abstraite et type Python.

Confondre représentation de graphe et algorithme de parcours.

Présenter BFS comme preuve de couverture complète des parcours de graphes.

Présenter ABR comme objectif évalué alors qu'il relève d'une séquence dédiée.

## Points à déplacer

Déplacer ABR vers une séquence dédiée sur arbres et arbres binaires de recherche.

Déplacer BFS/DFS vers une séquence dédiée sur parcours de graphes.

Déplacer complexité détaillée des parcours vers une séquence algorithmique.

Déplacer modularité et bugs vers une séquence de programmation.

## Décision sur T-ALGO-02A

`T-ALGO-02A` doit rester `partial`.

BFS/DFS apparaissent seulement comme application et extension.

Cette séquence ne prouve pas une maîtrise complète des parcours de graphes.

`T-ALGO-01` ne doit pas être associé à cette séquence.

## Décision de publication

NON.

La séquence reste en `needs_review`.

Elle ne doit pas être marquée comme couverte.

Elle ne doit pas être publiée comme version élève finale.
