---
title: "P11 - cours - parcours, recherche, extremum et moyenne"
level: "premiere"
sequence_id: "P11"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "parcours, recherche, extremum et moyenne"
notion: "parcours, recherche, extremum et moyenne"
private_data: false
official_program:
  capacities:
    - "P-ALGO-01A"
    - "P-ALGO-01B"
---

# P11 - Cours - parcours, recherche, extremum et moyenne

## Objectifs spécifiques
- Identifier les données utiles de la situation : mesures=[18,21,17,24,21], cible=21, seuil=22.
- Employer le vocabulaire : parcours linéaire, recherche occurrence, premier indice, maximum, minimum, somme.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-ALGO-01A.
- P-ALGO-01B.

## Situation-problème
mesures=[18,21,17,24,21], cible=21, seuil=22

## À savoir
- parcours linéaire.
- recherche occurrence.
- premier indice.
- maximum.
- minimum.
- somme.
- moyenne.
- liste vide.

## Méthodes
- parcourir avec indice.
- mémoriser le premier indice de 21.
- initialiser maximum à la première valeur.
- tester liste vide avant moyenne.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
- Méthode : parcourir avec indice.
- Résultat attendu : première occurrence de 21 -> indice 1.
- Contrôle : capacité P-ALGO-01A et cas limite `liste vide`.
### Exemple corrigé 2
- Donnée : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
- Méthode : mémoriser le premier indice de 21.
- Résultat attendu : maximum -> 24.
- Contrôle : capacité P-ALGO-01B et cas limite `cible absente`.
### Exemple corrigé 3
- Donnée : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
- Méthode : initialiser maximum à la première valeur.
- Résultat attendu : somme=101, len=5, moyenne=20.2.
- Contrôle : capacité P-ALGO-01A et cas limite `doublon de 21`.
### Exemple corrigé 4
- Donnée : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
- Méthode : tester liste vide avant moyenne.
- Résultat attendu : liste vide -> ValueError.
- Contrôle : capacité P-ALGO-01B et cas limite `liste vide`.

## Cas limites
- liste vide.
- cible absente.
- doublon de 21.

## Erreurs fréquentes
- maximum initialisé à 0.
- division par len sans test.
- indice changé après première occurrence.

## Exercices intégrés
1. Identifier les données utiles dans `mesures=[18,21,17,24,21], cible=21, seuil=22`.
2. Appliquer : parcourir avec indice.
3. Appliquer : mémoriser le premier indice de 21.
4. Décider le cas limite `liste vide`.

## Critères de réussite observables
- Une capacité parmi P-ALGO-01A, P-ALGO-01B est citée et utilisée.
- Le résultat attendu est explicite : première occurrence de 21 -> indice 1.
- Le cas limite `cible absente` est tranché.

## Lien avec la progression
- Séance : P11-S1 à P11-S4.
- TD : `P11_TD_parcours_recherche_extremum_moyenne.md`.
- TP : `P11_tp_parcours_recherche_extremum_moyenne.md`.
- Évaluation : `P11_evaluation_parcours_recherche_extremum_moyenne.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur parcours et recherche. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : indice, accumulateur, maximum, moyenne, compteur, cas liste vide.
- Capacités reliées : P-ALGO-01A, P-ALGO-01B.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- initialiser correctement un extremum avec le premier élément.
- parcourir chaque valeur une seule fois.
- tester le cas liste vide avant de diviser.

### Erreurs fréquentes spécifiques
- Un élève peut initialiser un maximum à 0 alors que les valeurs peuvent être négatives ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier d’incrémenter le compteur ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut diviser par zéro sur une liste vide ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de parcours et recherche.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
