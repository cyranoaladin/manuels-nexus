---
title: "P12 - cours - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - Cours - tris, invariants et complexité

## Objectifs spécifiques
- Identifier les données utiles de la situation : temps=[42,17,23,17,9].
- Employer le vocabulaire : tri par insertion, tri par sélection, invariant, variant, coût quadratique, stabilité.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-ALGO-02A.
- P-ALGO-02B.
- P-ALGO-02C.
- P-ALGO-02D.

## Situation-problème
temps=[42,17,23,17,9]

## À savoir
- tri par insertion.
- tri par sélection.
- invariant.
- variant.
- coût quadratique.
- stabilité.
- doublon 17.

## Méthodes
- insérer la clé dans la partie gauche triée.
- chercher le minimum du suffixe.
- écrire invariant gauche triée.
- compter comparaisons intuitives.

## Exemples guidés

### Exemple 1 — insertion
- Donnée : `temps=[42,17,23,17,9]`.
- Consigne : tracez le premier passage en séparant le préfixe déjà trié du reste ; nommez la clé et le décalage éventuel.
- Vérification : votre trace conserve les mêmes valeurs et traite aussi le cas `liste vide`.

### Exemple 2 — sélection
- Donnée : `cotes=[31,8,26,14,19]`.
- Consigne : repérez le minimum du suffixe, notez son indice, puis décidez si un échange est nécessaire.
- Vérification : expliquez pourquoi cette recherche examine le suffixe entier, y compris lorsque celui-ci paraît déjà rangé.

### Exemple 3 — invariant
- Donnée : une boucle dont l'indice de tour est `i`.
- Consigne : formulez ce qui est garanti avant le tour, puis ce qui doit rester vrai après le placement de la clé.
- Vérification : testez votre phrase sur des doublons 17 portant des étiquettes différentes.

### Exemple 4 — coût
- Donnée : une liste déjà triée et une liste inverse de même taille.
- Consigne : comparez qualitativement les comparaisons et les décalages de l'insertion à ceux de la sélection.
- Vérification : indiquez pourquoi un petit nombre d'échanges ne suffit pas à annoncer un coût linéaire.

## Cas limites
- liste vide.
- liste déjà triée.
- doublons 17.

## Erreurs fréquentes
- invariant confondu avec résultat.
- décalage oublié.
- coût linéaire annoncé.

## Exercices intégrés
1. Identifier les données utiles dans `temps=[42,17,23,17,9]`.
2. Appliquer : insérer la clé dans la partie gauche triée.
3. Appliquer : chercher le minimum du suffixe.
4. Décider le cas limite `liste vide`.

## Critères de réussite observables
- Une capacité parmi P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D est citée et utilisée.
- La trace explicite une clé, une action et un état intermédiaire vérifiable.
- Le cas limite `liste déjà triée` est tranché.

## Lien avec la progression
- Séance : P12-S1 à P12-S4.
- TD : `P12_TD_tris_invariants_complexite.md`.
- TP : `P12_tp_tris_invariants_complexite.md`.
- Évaluation : `P12_evaluation_tris_invariants_complexite.md`.

## Repères enseignant — exemples corrigés

### Exemple 1
- Résultat de la première insertion : `insertion après i=1 -> [17,42,23,17,9]`.
- La clé `17` décale `42` : le préfixe à gauche de `i` est alors trié.

### Exemple 2
- La première sélection place `8` au début de `[31,8,26,14,19]` ; le minimum est choisi dans le suffixe entier.

### Exemple corrigé 3
- Méthode : écrire invariant gauche triée.
- Résultat attendu : invariant : indices < i triés.
- Repère : l'invariant d'insertion indique que les indices strictement inférieurs à `i` sont triés avant le tour.

### Exemple corrigé 4
- Méthode : compter comparaisons intuitives.
- Résultat attendu : pire cas quadratique.
- Contrôle : capacité P-ALGO-02D et cas limite `liste vide`.
- Repère : le meilleur cas de l'insertion est linéaire, tandis que la sélection garde un nombre quadratique de comparaisons.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur tris, invariants et complexité. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : tri par insertion, tri par sélection, invariant, comparaison, échange, coût quadratique.
- Capacités reliées : P-ALGO-02A, P-ALGO-02B, P-ALGO-02C, P-ALGO-02D.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- énoncer l’invariant après chaque passage.
- compter les comparaisons sur une petite liste.
- vérifier que la liste reste une permutation des données initiales.

### Erreurs fréquentes spécifiques
- Un élève peut confondre tri stable et tri en place ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier le cas déjà trié ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut annoncer une complexité sans préciser la grandeur n ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de tris, invariants et complexité.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
