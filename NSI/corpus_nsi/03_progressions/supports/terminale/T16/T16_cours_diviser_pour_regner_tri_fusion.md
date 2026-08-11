---
title: "T16 - cours - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "diviser pour régner et tri fusion"
notion: "diviser pour régner et tri fusion"
private_data: false
official_program:
  capacities:
    - "T-ALGO-03"
---

# T16 - Cours - diviser pour régner et tri fusion

## Objectifs spécifiques
- Identifier les données utiles de la situation : valeurs=[38,12,27,12,5,44].
- Employer le vocabulaire : diviser pour régner, cas de base, division, récursion, fusion, tri fusion.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-ALGO-03.

## Situation-problème
valeurs=[38,12,27,12,5,44]

## À savoir
- diviser pour régner.
- cas de base.
- division.
- récursion.
- fusion.
- tri fusion.
- coût n log n.
- stabilité.

## Méthodes
- couper en deux sous-listes.
- trier récursivement.
- fusionner deux listes triées.
- compter niveaux et comparaisons.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Méthode : couper en deux sous-listes.
- Résultat attendu : division -> [38,12,27] et [12,5,44].
- Contrôle : capacité T-ALGO-03 et cas limite `liste vide`.
### Exemple corrigé 2
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Méthode : trier récursivement.
- Résultat attendu : fusion -> [5,12,12,27,38,44].
- Contrôle : capacité T-ALGO-03 et cas limite `liste taille 1`.
### Exemple corrigé 3
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Méthode : fusionner deux listes triées.
- Résultat attendu : cas taille 1 renvoie la liste.
- Contrôle : capacité T-ALGO-03 et cas limite `doublons 12`.
### Exemple corrigé 4
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Méthode : compter niveaux et comparaisons.
- Résultat attendu : coût environ n log n.
- Contrôle : capacité T-ALGO-03 et cas limite `liste vide`.

## Cas limites
- liste vide.
- liste taille 1.
- doublons 12.

## Erreurs fréquentes
- cas de base oublié.
- concaténation sans fusion.
- coût quadratique annoncé.

## Exercices intégrés
1. Identifier les données utiles dans `valeurs=[38,12,27,12,5,44]`.
2. Appliquer : couper en deux sous-listes.
3. Appliquer : trier récursivement.
4. Décider le cas limite `liste vide`.

## Critères de réussite observables
- Une capacité parmi T-ALGO-03 est citée et utilisée.
- Le résultat attendu est explicite : division -> [38,12,27] et [12,5,44].
- Le cas limite `liste taille 1` est tranché.

## Lien avec la progression
- Séance : T16-S1 à T16-S4.
- TD : `T16_TD_diviser_pour_regner_tri_fusion.md`.
- TP : `T16_tp_diviser_pour_regner_tri_fusion.md`.
- Évaluation : `T16_evaluation_diviser_pour_regner_tri_fusion.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur diviser pour régner. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : division, cas de base, combinaison, tri fusion, complexité en n log n.
- Capacités reliées : T-ALGO-03.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- identifier le cas de base.
- fusionner deux listes déjà triées.
- compter les niveaux de récursion.

### Erreurs fréquentes spécifiques
- Un élève peut oublier le cas liste de taille 0 ou 1 ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut fusionner sans conserver tous les éléments ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut confondre coût d’un niveau et coût total ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de diviser pour régner.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
