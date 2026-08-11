---
title: "Revue pédagogique - s01_representation_donnees"
niveau: premiere
source: "Revue interne prototype"
status: needs_review
version: "0.3.0"
notion: "représentation des données"
objectifs: "Évaluer la cohérence pédagogique de la séquence pilote Première."
sequence: s01_representation_donnees
private_data: false
---

# Revue pédagogique - s01_representation_donnees

## Cohérence de la séquence

La séquence est exploitable comme pilote de consolidation.

Elle regroupe cependant trop de notions pour une séquence finale stable.

Elle mélange représentation machine, encodage, booléens, texte et types construits Python.

La cohérence existe comme parcours de découverte, mais elle n'est pas assez ciblée pour une publication.

## Surcharge cognitive

La charge cognitive est élevée.

Les élèves doivent manipuler bases, complément à deux, tables de vérité, Unicode, listes, tuples, dictionnaires et tests.

Cette densité risque de masquer les objectifs prioritaires.

Les élèves fragiles peuvent confondre valeur, représentation, type Python et structure de collection.

## Points solides

Le cours distingue valeur et représentation.

Les conversions de base et le complément à deux sont testés.

Les erreurs fréquentes sont explicites.

Les aides progressives existent.

Les fichiers Python disposent de tests renforcés.

## Points faibles

Les types construits arrivent trop tôt dans une séquence centrée sur les représentations de base.

Les dictionnaires introduisent une abstraction supplémentaire.

Les tests Python peuvent prendre le dessus sur l'objectif de représentation des données.

Les flottants ne sont pas traités.

Les tables CSV ne sont pas traitées.

La recherche, le tri et la fusion de tables ne sont pas traités.

## Erreurs scientifiques possibles

Confondre représentation binaire d'un entier positif et encodage en complément à deux.

Présenter Unicode comme un simple prolongement d'ASCII sans discuter les points de code.

Laisser croire qu'une liste Python est équivalente à un tableau machine dans tous les contextes.

Laisser croire que le choix list/tuple/dict remplace une réflexion sur le modèle de données.

## Points à déplacer

Les listes, tuples et dictionnaires doivent être déplacés vers une séquence dédiée sur types construits.

Les tables CSV doivent être déplacées vers une séquence dédiée au traitement de données en tables.

Les tests Python doivent être conservés comme support technique, pas comme objectif principal.

Les flottants doivent être traités dans une séquence spécifique ou un complément clairement identifié.

## Recommandation de découpage

Séquence A : bits, bases 2/10/16, entiers naturels.

Séquence B : entiers relatifs, complément à deux, booléens.

Séquence C : texte, ASCII, Unicode, encodage.

Séquence D : types construits Python, listes, tuples, dictionnaires.

Séquence E : tables CSV, recherche, tri et fusion.

## Décision de publication

NON.

La séquence reste en `needs_review`.

Elle ne doit pas être marquée comme couverte.

Elle ne doit pas être publiée comme version élève finale.
