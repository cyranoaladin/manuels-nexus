---
title: "P06 - tp - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "tp"
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

# P06 - TP - recherche, tri et fusion de tables

## Statut du TP
TP exécutable avec starter, corrigé professeur et tests attendus.

## Donnée fournie
`inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`


## Fonctions Python attendues
- `rechercher_premiere_ligne(rows, key, value)` renvoie la première ligne qui porte la clé demandée.
- `detecter_doublons(rows, key)` renvoie `[17]` sur la table d inscriptions de référence.
- `trier_par_nom_atelier(rows)` renvoie les ateliers dans l ordre `python`, `robot`, `web`.
- `fusionner_presences(inscriptions, presences)` renvoie la fusion et `erreurs == ["id_absent=9"]`.

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : chercher la première ligne id=17.
3. Réaliser : détecter le doublon id=17.
4. Tester le cas limite `table vide`.
5. Produire le livrable : première ligne id=17 -> Ada/robot.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `première ligne id=17 -> Ada/robot`.
- 2 points : cas limite `table vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
### Corrigé question 2
Résultat attendu : première ligne id=17 -> Ada/robot.
### Corrigé question 3
Résultat attendu : doublon id=17 -> Ada/python signalé.
### Corrigé question 4
Résultat attendu : `table vide` traité sans ambiguïté.

## Liens
- TD lié : `P06_TD_tables_recherche_tri_fusion.md`.
- Évaluation liée : `P06_evaluation_tables_recherche_tri_fusion.md`.

## Cas limites travaillés
- table vide.
- clé id=9 absente.
- conflit de clé id=17.

## Erreurs fréquentes
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première ligne id=17 -> Ada/robot`.
- Au moins un cas limite de la section précédente est décidé.

