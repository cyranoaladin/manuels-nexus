---
title: "P07 - cours - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "fonctions, tests et spécifications"
notion: "fonctions, tests et spécifications"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
    - "P-LANG-02"
    - "P-LANG-03A"
    - "P-LANG-03B"
    - "P-LANG-03C"
    - "P-LANG-04"
    - "P-LANG-05"
---

# P07 - Cours - fonctions, tests et spécifications

## Objectifs spécifiques
- Identifier les données utiles de la situation : prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError.
- Employer le vocabulaire : signature, précondition, postcondition, assertion, test unitaire, test limite.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-LANG-01.
- P-LANG-02.
- P-LANG-03A.
- P-LANG-03B.
- P-LANG-03C.
- P-LANG-04.
- P-LANG-05.

## Situation-problème
prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError

## À savoir
- signature.
- précondition.
- postcondition.
- assertion.
- test unitaire.
- test limite.
- erreur de type.
- fonction pure.

## Méthodes
- écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- poser prix_ht >= 0 et taux >= 0.
- vérifier résultat >= prix_ht.
- écrire tests nominal, limite et invalide.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Méthode : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- Résultat attendu : signature complète de prix_ttc.
- Contrôle : capacité P-LANG-01 et cas limite `prix_ht=0`.
### Exemple corrigé 2
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Méthode : poser prix_ht >= 0 et taux >= 0.
- Résultat attendu : prix_ttc(80,0.20) -> 96.0.
- Contrôle : capacité P-LANG-02 et cas limite `taux=0`.
### Exemple corrigé 3
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Méthode : vérifier résultat >= prix_ht.
- Résultat attendu : prix_ttc(-5,0.20) -> ValueError.
- Contrôle : capacité P-LANG-03A et cas limite `type chaîne "80"`.
### Exemple corrigé 4
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Méthode : écrire tests nominal, limite et invalide.
- Résultat attendu : taux=0 -> résultat 80.0.
- Contrôle : capacité P-LANG-03B et cas limite `prix_ht=0`.

## Cas limites
- prix_ht=0.
- taux=0.
- type chaîne "80".

## Erreurs fréquentes
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Exercices intégrés
1. Identifier les données utiles dans `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
2. Appliquer : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
3. Appliquer : poser prix_ht >= 0 et taux >= 0.
4. Décider le cas limite `prix_ht=0`.

## Critères de réussite observables
- Une capacité parmi P-LANG-01, P-LANG-02, P-LANG-03A, P-LANG-03B, P-LANG-03C, P-LANG-04, P-LANG-05 est citée et utilisée.
- Le résultat attendu est explicite : signature complète de prix_ttc.
- Le cas limite `taux=0` est tranché.

## Lien avec la progression
- Séance : P07-S1 à P07-S4.
- TD : `P07_TD_fonctions_tests_specifications.md`.
- TP : `P07_tp_fonctions_tests_specifications.md`.
- Évaluation : `P07_evaluation_fonctions_tests_specifications.md`.

## Repérer les traits communs et particuliers d'un langage

La capacité P-LANG-02 demande de repérer dans un nouveau langage les traits communs et particuliers par rapport à Python. On compare l'écriture d'un même programme simple dans différents langages.

### Traits communs à la plupart des langages

Tout langage impératif dispose de :
- **variables et affectation** (`x = 5` en Python, `let x = 5;` en JavaScript, `int x = 5;` en C) ;
- **structures conditionnelles** (`if/else`) ;
- **boucles** (`for`, `while`) ;
- **fonctions** avec paramètres et valeur de retour.

### Traits particuliers à Python

- **Indentation significative** : les blocs sont délimités par l'indentation, pas par des accolades `{}`.
- **Typage dynamique** : pas de déclaration de type obligatoire (`x = 5` suffit, pas besoin de `int x`).
- **Syntaxe légère** : pas de point-virgule en fin de ligne, pas de `main()` obligatoire.

### Exemple comparatif — calcul du prix TTC

En Python :
```python
def prix_ttc(prix_ht, taux):
    return prix_ht * (1 + taux)
```

En JavaScript :
```javascript
function prix_ttc(prix_ht, taux) {
    return prix_ht * (1 + taux);
}
```

En C :
```c
float prix_ttc(float prix_ht, float taux) {
    return prix_ht * (1 + taux);
}
```

Traits communs : les trois versions ont une fonction nommée avec paramètres et un `return`. Traits particuliers : Python n'a pas d'accolades ni de type de retour explicite ; C exige les types ; JavaScript utilise `function` au lieu de `def`.

## Utiliser la documentation d'une bibliothèque

La capacité P-LANG-05 demande de savoir utiliser la documentation d'une bibliothèque pour découvrir et employer ses fonctions.

### Qu'est-ce qu'une bibliothèque ?

Une bibliothèque (ou module) est un ensemble de fonctions prêtes à l'emploi, regroupées par thème. En Python, on importe une bibliothèque avec `import`.

### Lire une documentation : les informations essentielles

Pour chaque fonction d'une bibliothèque, la documentation indique :
1. **Le nom** de la fonction.
2. **Les paramètres** (nombre, type attendu, valeurs par défaut).
3. **La valeur de retour** (type et signification).
4. **Des exemples d'utilisation**.

### Exemple : le module `math`

```python
import math

# Documentation : math.sqrt(x)
# Paramètre : x (nombre >= 0)
# Retour : la racine carrée de x (float)
# Exemple :
print(math.sqrt(16))  # 4.0
print(math.sqrt(2))   # 1.4142135623730951
```

Pour explorer les fonctions disponibles :
```python
import math
help(math.sqrt)   # affiche la documentation de sqrt
dir(math)          # liste toutes les fonctions du module
```

### Exemple : le module `random`

```python
import random

# Documentation : random.randint(a, b)
# Paramètres : a, b (entiers, a <= b)
# Retour : un entier aléatoire entre a et b inclus
print(random.randint(1, 6))  # simule un dé à 6 faces
```

### Cas limites

- `math.sqrt(-1)` lève `ValueError` : la documentation précise que `x` doit être positif ou nul.
- `random.randint(5, 5)` renvoie toujours 5 : un seul entier possible dans l'intervalle.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur fonctions et tests. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : signature, précondition, postcondition, assertion, test unitaire, effet de bord.
- Capacités reliées : P-LANG-01, P-LANG-02, P-LANG-03A, P-LANG-03B, P-LANG-03C, P-LANG-04, P-LANG-05.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- vérifier une signature avant d’écrire le corps de la fonction.
- tester une valeur limite avant une valeur ordinaire.
- isoler une fonction pure d’une procédure qui modifie une liste.

### Erreurs fréquentes spécifiques
- Un élève peut confondre précondition et test de sortie ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier le cas liste vide dans une moyenne ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut mélanger valeur renvoyée et affichage avec print ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de fonctions et tests.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
