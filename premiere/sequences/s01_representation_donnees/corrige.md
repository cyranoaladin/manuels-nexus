---
title: "Corrigé - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "corrige"
status: "needs_review"
version: "0.3.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "corrections et justifications"
duration: "1 h"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données"
  content: "Correction des activités"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Changer de base."
      evidence: [{section: "Exercices intégrés du cours", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#exercices-intégrés-du-cours", type: "corrige"}]
    - id: "P-DATA-BASE-02B"
      label: "Utiliser le complément à deux."
      evidence: [{section: "Exercices intégrés du cours", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#exercices-intégrés-du-cours", type: "corrige"}]
    - id: "P-DATA-BASE-04"
      label: "Tables de vérité."
      evidence: [{section: "Exercices intégrés du cours", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#exercices-intégrés-du-cours", type: "corrige"}]
    - id: "P-DATA-BASE-05A"
      label: "Encodage de texte."
      evidence: [{section: "Réponse attendue - TD", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#réponse-attendue--td", type: "corrige"}]
    - id: "P-DATA-CONSTR-01"
      label: "Tuples."
      evidence: [{section: "Réponse attendue - TD", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#réponse-attendue--td", type: "corrige"}]
    - id: "P-DATA-CONSTR-02A"
      label: "Listes."
      evidence: [{section: "Exercices intégrés du cours", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#exercices-intégrés-du-cours", type: "corrige"}]
    - id: "P-DATA-CONSTR-03A"
      label: "Dictionnaires."
      evidence: [{section: "Réponse attendue - TD", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#réponse-attendue--td", type: "corrige"}]
    - id: "P-LANG-04"
      label: "Jeux de tests."
      evidence: [{section: "Code testé", file: "premiere/sequences/s01_representation_donnees/corrige.md", anchor: "#code-testé", type: "corrige"}]
prerequisites: ["TD et TP S01"]
learning_objectives: ["Expliquer les réponses attendues et les variantes acceptables."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "26 juin 2026 - revue de substance", science: "", technical: ""}
---

# Corrigé — S01 Représentation des données

Ce corrigé couvre les exercices intégrés du cours, les exercices du TD et les questions de l'évaluation. Pour chaque réponse, la justification et les erreurs fréquentes sont indiquées afin de permettre l'auto-correction.

## Barème

Le barème global de l'évaluation est de 20 points : conversions, 4 points ; complément à deux, 4 points ; booléens et texte, 4 points ; structures Python, 5 points ; tests et justification, 3 points. Une réponse correcte sans justification peut obtenir une partie des points, mais les points de méthode exigent une trace vérifiable : développement en puissances, calcul du complément à deux, table de vérité complète, choix de structure relié à l'opération attendue ou test accompagné de sa sortie attendue.

## Exercices intégrés du cours

### Exercice intégré 1 — Conversions de bases (P-DATA-BASE-01)

**1. Convertir `31₁₀` en base 2.**

On divise successivement par 2 : 31 = 2×15 + 1, 15 = 2×7 + 1, 7 = 2×3 + 1, 3 = 2×1 + 1, 1 = 2×0 + 1. En lisant les restes du dernier au premier : `31₁₀ = 11111₂`. Vérification : 16 + 8 + 4 + 2 + 1 = 31. ✓

**2. Convertir `11110₂` en base 10.**

On développe les puissances : `1×2⁴ + 1×2³ + 1×2² + 1×2¹ + 0×2⁰ = 16 + 8 + 4 + 2 + 0 = 30₁₀`.

**3. Convertir `2F₁₆` en base 10.**

`2×16¹ + F×16⁰ = 2×16 + 15×1 = 32 + 15 = 47₁₀`.

**4. Vérifier que `1111₂` et `F₁₆` représentent la même valeur.**

`1111₂ = 8 + 4 + 2 + 1 = 15₁₀`, et `F₁₆ = 15₁₀`. Ce sont bien la même valeur, ce qui illustre qu'un chiffre hexadécimal correspond à 4 bits.

### Exercice intégré 2 — Complément à deux (P-DATA-BASE-02B)

**1. Encoder `7`, `−1` et `−8` sur 8 bits.**

- `7` est positif : `7₁₀ = 00000111₂`.
- `−1` : on calcule `256 − 1 = 255₁₀ = 11111111₂`.
- `−8` : on calcule `256 − 8 = 248₁₀ = 11111000₂`.

**2. Décoder `00001111`, `11111111` et `11111000` sur 8 bits.**

- `00001111₂ = 15₁₀`. Bit de gauche = 0, donc positif : la valeur est **15**.
- `11111111₂ = 255₁₀`. Bit de gauche = 1, donc négatif : `255 − 256 = −1`. La valeur est **−1**.
- `11111000₂ = 248₁₀`. Bit de gauche = 1 : `248 − 256 = −8`. La valeur est **−8**.

**3. Intervalle sur 4 bits :** de `−2³ = −8` à `2³ − 1 = 7`, soit **[−8 ; 7]**.

**4. Pourquoi 140 ne se code pas comme entier relatif sur 8 bits ?** L'intervalle du complément à deux sur 8 bits est [−128 ; 127]. Comme 140 > 127, cette valeur déborde : elle est représentable comme entier positif sur 8 bits (140 ≤ 255) mais pas comme entier relatif en complément à deux.

### Exercice intégré 3 — Tables de vérité (P-DATA-BASE-04)

**1. Table de vérité de `not a or b` :**

| `a` | `b` | `not a` | `not a or b` |
|-----|-----|---------|--------------|
| F   | F   | T       | T            |
| F   | T   | T       | T            |
| T   | F   | F       | F            |
| T   | T   | F       | T            |

Seul le cas `a = True, b = False` donne `False`.

**2. Table de vérité de `(a and b) or (a and not b)` :**

| `a` | `b` | `a and b` | `a and not b` | Résultat |
|-----|-----|-----------|---------------|----------|
| F   | F   | F         | F             | F        |
| F   | T   | F         | F             | F        |
| T   | F   | F         | T             | T        |
| T   | T   | T         | F             | T        |

**3. Simplification :** le résultat est `True` quand `a = True` et `False` quand `a = False`, quelle que soit la valeur de `b`. L'expression se simplifie donc en **`a`**. En effet, `(a and b) or (a and not b)` = `a and (b or not b)` = `a and True` = `a`.

### Exercice intégré 4 — Listes (P-DATA-CONSTR-02A)

**1.** `[x * 2 for x in [3, 5, 8]]` produit `[6, 10, 16]`.

**2.** `m[0][1]` vaut `0` (ligne 0, colonne 1) et `m[1][0]` vaut `0` (ligne 1, colonne 0). La matrice identité 2×2 a des zéros hors de la diagonale.

**3.** Boucle de somme :
```python
total = 0
for n in nombres:
    total += n
```
Variante acceptée : `total = sum(nombres)`.

## Réponse attendue — TD

### Exercice 1 — Conversions de bases

`18₁₀ = 10010₂` (16 + 2). `31₁₀ = 11111₂` (16 + 8 + 4 + 2 + 1). `42₁₀ = 101010₂` (32 + 8 + 2). `1010₂ = 10₁₀`. `1111₂ = 15₁₀`. `100000₂ = 32₁₀`. `2A₁₆ = 42₁₀`. `FF₁₆ = 255₁₀`. Justification : développer avec les puissances ou relire les restes des divisions.

### Exercice 2 — Octets

Sur 8 bits sans signe, l'intervalle est `[0 ; 255]`. `255` est représentable, `256` ne l'est pas, `128` et `0` sont représentables. `255₁₀ = 11111111₂ = FF₁₆`. Deux chiffres hexadécimaux suffisent car chaque chiffre représente exactement 4 bits, et un octet contient 8 bits.

### Exercice 3 — Complément à deux

`5` sur 8 bits : `00000101`. `−1` sur 8 bits : `11111111` (car 256 − 1 = 255). `−7` sur 8 bits : `11111001` (car 256 − 7 = 249). `−128` sur 8 bits : `10000000` (car 256 − 128 = 128). Décodage : `00000101 → 5`, `11111111 → 255 − 256 = −1`, `11111001 → 249 − 256 = −7`, `10000000 → 128 − 256 = −128`. Sur 4 bits, l'intervalle est [−8 ; 7]. `−9` est hors de cet intervalle, donc non représentable.

### Exercice 4 — Booléens

Pour `and`, seul le cas `(True, True)` donne `True`. Pour `or`, seul `(False, False)` donne `False`. Pour `a and not b`, seul `(True, False)` donne `True`. Le XOR donne `True` quand exactement une entrée est vraie — contrairement à `or` qui donne aussi `True` quand les deux sont vraies.

### Exercice 5 — Texte et encodage

`65` et `233` sont des **points de code** Unicode. `"A"` est codé sur un seul octet en UTF-8 (car son code est < 128), tandis que `"é"` est codé sur deux octets. Le nombre de caractères ne suffit donc pas à déduire le nombre d'octets en mémoire.

### Exercice 6 — Tuples et listes (P-DATA-CONSTR-01, P-DATA-CONSTR-02A)

```python
def milieu(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
```

La compréhension `[t + 1 for t in temperatures]` convient pour ajouter 1 à chaque température. Le tuple est adapté au point car il regroupe exactement deux coordonnées liées dans un ordre fixé, et on n'a pas besoin de les modifier après création. Deux variables séparées (`x_milieu`, `y_milieu`) perdraient le lien logique entre les deux coordonnées.

### Exercice 7 — Dictionnaires (P-DATA-CONSTR-03A)

Résultat attendu : `{"A": 3, "B": 2, "C": 1}`. La clé de plus grand effectif est `"A"`. Un dictionnaire est adapté car on associe chaque choix à son effectif et on y accède directement par le nom du choix. Une simple liste suffirait si l'on conserve seulement l'ordre brut des votes sans avoir besoin de compter.

### Exercice 8 — Choix de représentation

- Positions successives d'un robot : **liste** (ordre important, valeurs modifiables).
- Coordonnées fixes d'un point : **tuple** (deux valeurs liées, pas de modification).
- Stock par référence produit : **dictionnaire** (accès par nom de produit).
- Table de pixels ligne par ligne : **liste de listes** (structure 2D, modifiable).
- Fiche courte avec champs nommés : **dictionnaire** (accès par nom de champ).

Toute autre réponse est acceptable si elle est justifiée par les opérations attendues.

### Exercice 9 — Analyse de code (P-LANG-04)

`mystere(6)` : 6 % 2 = 0, bits = "0" ; 3 % 2 = 1, bits = "10" ; 1 % 2 = 1, bits = "110". Résultat : `"110"`, soit `6₁₀ = 110₂`. ✓

Le cas limite non géré est `n = 0` : la boucle `while n > 0` ne s'exécute pas, et la fonction renvoie une chaîne vide au lieu de `"0"`. Correction : ajouter `if n == 0: return "0"` au début.

Trois tests pertinents :
- `mystere(0)` doit renvoyer `"0"` (cas limite, traitement spécial) ;
- `mystere(1)` doit renvoyer `"1"` (plus petit entier non nul) ;
- `mystere(6)` doit renvoyer `"110"` (cas ordinaire).

### Exercice 10 — Justification

La liste de tuples `[(id, nom), ...]` impose un parcours linéaire pour retrouver un nom à partir d'un identifiant, car les éléments ne sont accessibles que par position. Un dictionnaire `{identifiant: nom, ...}` permet un accès direct par clé.

```python
annuaire = {identifiant: nom for identifiant, nom in utilisateurs}
```

Test : `assert annuaire["u2"] == "Bob"` vérifie que la transformation conserve l'association.

## Variante acceptable et variantes acceptables

- Pour le milieu, une solution décomposant `x1, y1 = p1` puis reconstruisant le tuple est acceptée.
- Pour le comptage de votes, une boucle avec `if choix not in effectifs` est acceptée, de même que `effectifs.get(choix, 0) + 1`.
- Pour le choix de représentation, plusieurs réponses sont acceptées si la justification cite l'opération principale.
- Pour les tests, les noms de fonctions peuvent différer tant que les entrées et sorties sont vérifiables.

Une variante acceptable doit conserver les mêmes valeurs d'entrée et produire un résultat vérifiable. Elle ne peut pas remplacer la méthode par une affirmation non contrôlée.

## Erreurs fréquentes

- Oublier le cas `n = 0` dans une conversion par divisions successives.
- Lire `11111111` sans préciser la convention (positif ou complément à deux).
- Oublier que `FF₁₆` vaut 255, pas 256.
- Confondre clé et valeur dans un dictionnaire.
- Donner une structure Python sans justification par l'opération attendue.
- Proposer un test sans indiquer le résultat attendu.

## Code testé

Les fonctions de référence sont dans `python/representation_tools.py` et les tests dans `tests/test_representation_tools.py`. La commande `python scripts/run_python_tests.py` vérifie les conversions de base, le complément à deux, les points de code Unicode et le choix de conteneur. Les tests couvrent des cas ordinaires (comme `to_base(42, 2)`) et des cas limites (comme `to_base(0, 2)` ou `encode_twos_complement(-128, 8)`).
