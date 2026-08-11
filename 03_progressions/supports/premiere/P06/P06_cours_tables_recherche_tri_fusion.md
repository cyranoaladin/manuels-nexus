---
title: "P06 - cours - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "recherche, tri et fusion de tables"
notion: "recherche, tri et fusion de tables"
private_data: false
official_program:
  capacities:
    - "P-TABLE-03"
    - "P-TABLE-04"
---

# P06 - Cours - recherche, tri et fusion de tables

## Objectifs spécifiques
- Identifier les données utiles de la situation : inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}].
- Employer le vocabulaire : recherche dans une table, clé id, doublon id=17, tri stable, tri par clé composée, fusion de tables.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-TABLE-03.
- P-TABLE-04.

## Situation-problème
inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]

## À savoir
- recherche dans une table.
- clé id.
- doublon id=17.
- tri stable.
- tri par clé composée.
- fusion de tables.
- clé absente.
- complexité linéaire.

## Méthodes
- chercher la première ligne id=17.
- détecter le doublon id=17.
- trier par (nom, atelier).
- fusionner inscriptions et présences.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Méthode : chercher la première ligne id=17.
- Résultat attendu : première ligne id=17 -> Ada/robot.
- Contrôle : capacité P-TABLE-03 et cas limite `table vide`.
### Exemple corrigé 2
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Méthode : détecter le doublon id=17.
- Résultat attendu : doublon id=17 -> Ada/python signalé.
- Contrôle : capacité P-TABLE-04 et cas limite `clé id=9 absente`.
### Exemple corrigé 3
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Méthode : trier par (nom, atelier).
- Résultat attendu : tri -> Ada/python, Ada/robot, Linus/web.
- Contrôle : capacité P-TABLE-03 et cas limite `conflit de clé id=17`.
### Exemple corrigé 4
- Donnée : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- Méthode : fusionner inscriptions et présences.
- Résultat attendu : fusion -> erreur id_absent=9.
- Contrôle : capacité P-TABLE-04 et cas limite `table vide`.

## Cas limites
- table vide.
- clé id=9 absente.
- conflit de clé id=17.

## Erreurs fréquentes
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Exercices intégrés
1. Identifier les données utiles dans `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
2. Appliquer : chercher la première ligne id=17.
3. Appliquer : détecter le doublon id=17.
4. Décider le cas limite `table vide`.

## Critères de réussite observables
- Une capacité parmi P-TABLE-03, P-TABLE-04 est citée et utilisée.
- Le résultat attendu est explicite : première ligne id=17 -> Ada/robot.
- Le cas limite `clé id=9 absente` est tranché.

## Lien avec la progression
- Séance : P06-S1 à P06-S4.
- TD : `P06_TD_tables_recherche_tri_fusion.md`.
- TP : `P06_tp_tables_recherche_tri_fusion.md`.
- Évaluation : `P06_evaluation_tables_recherche_tri_fusion.md`.
