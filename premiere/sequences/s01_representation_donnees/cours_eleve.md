---
title: "S01 - Représenter des données : bits, textes et types construits"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "cours"
status: "needs_review"
version: "0.3.0"
authors: ["NSI"]
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "bits, bases, complément à deux, booléens, texte, listes, tuples, dictionnaires"
duration: "5 séances"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données : types et valeurs de base ; types construits"
  content: "Bases 2/10/16, entiers relatifs, booléens, texte, p-uplets, tableaux, dictionnaires"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Passer de la représentation d'une base dans une autre."
      evidence:
        - section: "Bases 2, 10 et 16"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#bases-2-10-et-16"
          type: "cours"
    - id: "P-DATA-BASE-02B"
      label: "Evaluer un codage binaire d'entier relatif et utiliser le complément à deux."
      evidence:
        - section: "Entiers relatifs et complément à deux"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#entiers-relatifs-et-complément-à-deux"
          type: "cours"
    - id: "P-DATA-BASE-04"
      label: "Dresser la table d'une expression booléenne."
      evidence:
        - section: "Booléens et tables de vérité"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#booléens-et-tables-de-vérité"
          type: "cours"
    - id: "P-DATA-BASE-05A"
      label: "Identifier l'intérêt des systèmes d'encodage de texte."
      evidence:
        - section: "Texte, ASCII et Unicode"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#texte-ascii-et-unicode"
          type: "cours"
    - id: "P-DATA-CONSTR-01"
      label: "Ecrire une fonction renvoyant un p-uplet de valeurs."
      evidence:
        - section: "Tuples et p-uplets"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#tuples-et-p-uplets"
          type: "cours"
    - id: "P-DATA-CONSTR-02A"
      label: "Lire, modifier, construire et itérer sur des tableaux."
      evidence:
        - section: "Listes et tableaux Python"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#listes-et-tableaux-python"
          type: "cours"
    - id: "P-DATA-CONSTR-03A"
      label: "Construire et parcourir un dictionnaire."
      evidence:
        - section: "Dictionnaires"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#dictionnaires"
          type: "cours"
    - id: "P-LANG-04"
      label: "Utiliser des jeux de tests."
      evidence:
        - section: "Tests et cas limites"
          file: "premiere/sequences/s01_representation_donnees/cours_eleve.md"
          anchor: "#tests-et-cas-limites"
          type: "cours"
prerequisites:
  - "Utiliser Python pour affecter une variable et appeler une fonction."
  - "Lire une expression arithmétique simple."
learning_objectives:
  - "Comprendre pourquoi toute donnée manipulée par une machine est codée."
  - "Passer entre bases 2, 10 et 16 pour des entiers positifs."
  - "Interpréter un entier relatif codé en complément à deux."
  - "Choisir entre liste, tuple et dictionnaire selon le problème."
assessment:
  formative: true
  summative: false
last_review:
  pedagogy: "26 juin 2026 - revue de substance"
  science: ""
  technical: ""
---

# S01 — Représenter des données : bits, textes et types construits

## Situation-problème

Imaginons un badge de cantine identifié `B-17`. Ce badge contient un identifiant numérique (17), une variation de solde qui peut être négative (−3), un droit d'accès qui est soit autorisé soit refusé (vrai ou faux), et une initiale affichée sur l'écran (le caractère `É`). La machine qui lit ce badge ne manipule pourtant aucune de ces informations sous la forme que nous, humains, utilisons au quotidien : elle ne travaille qu'avec des suites de `0` et de `1`, appelées **bits**.

Pour que la machine puisse stocker, traiter et restituer chacune de ces informations, il faut une **convention de représentation** — un accord sur la manière dont les bits correspondent à une valeur. Sans cette convention, la suite `11111101` pourrait aussi bien désigner le nombre 253 qu'un entier relatif valant −3 : les bits sont les mêmes, mais leur interprétation change tout. C'est cette question centrale — comment choisir une représentation adaptée à la donnée et au traitement attendu — que nous allons explorer dans cette séquence.

**Questions de départ :**

1. Parmi les quatre informations du badge (identifiant 17, variation −3, accès autorisé, initiale É), lesquelles peut-on coder directement par un entier positif ?
2. Lesquelles nécessitent une convention supplémentaire (signe, valeur logique, encodage de caractère) ?
3. Si l'on lit la suite `11111101` comme un entier positif, on obtient 253. Mais si on la lit en complément à deux sur 8 bits, on obtient −3. Qu'est-ce qui détermine la bonne lecture ?
4. Pourquoi le caractère `É` peut-il poser problème dans certains anciens systèmes d'encodage ?

**Conclusion attendue :** une suite de bits n'a de sens que si l'on connaît la convention de représentation utilisée.

## Activité d'introduction

Cette activité reprend l'idée d'une ressource locale sur le codage d'un entier naturel : passer d'une représentation externe lisible par un humain à une représentation interne binaire, en explicitant la règle de passage. Elle est adaptée ici sans copier la fiche source, avec des valeurs et contrôles alignés sur la séquence S01.

1. Écrire le nombre `35` sous la forme d'une somme de puissances de 2.
2. En déduire son écriture binaire et vérifier que `100011₂ = 35₁₀`.
3. Refaire la même démarche avec `0`, puis avec `1`, pour ne pas oublier les cas minimaux.
4. Expliquer en une phrase pourquoi les bits seuls ne suffisent pas : il faut aussi connaître la base, la taille disponible et la convention de codage.

**Trace attendue :** divisions successives ou développement positionnel, puis phrase de conclusion. Une réponse qui donne seulement `100011` sans méthode n'est pas suffisante.

## Objectifs

À l'issue de cette séquence, vous saurez :

- définir ce qu'est un bit et expliquer son rôle comme unité élémentaire d'information ;
- convertir un entier positif entre les bases 2, 10 et 16, et repérer l'intervalle représentable sur un nombre de bits donné ;
- encoder et décoder de petits entiers relatifs en complément à deux ;
- construire la table de vérité d'une expression booléenne ;
- expliquer la différence entre un caractère, un point de code et un encodage ;
- choisir entre liste, tuple et dictionnaire en justifiant par les opérations attendues ;
- vérifier une fonction à l'aide de tests simples couvrant des cas ordinaires et des cas limites.

## Prérequis

Cette séquence suppose que vous savez additionner et diviser des entiers, lire une écriture décimale positionnelle, exécuter une fonction Python simple, distinguer une valeur d'une variable et d'une expression, lire une condition `if`, et utiliser une liste Python en lecture.

## Limites de la séquence

Cette séquence pilote regroupe deux blocs liés du programme de Première : les types et valeurs de base d'une part, les types construits d'autre part. Elle ne traite ni l'import de fichiers CSV, ni le tri ou la fusion de tables, qui relèvent d'une autre séquence. Les nombres flottants sont seulement signalés comme un sujet à part, car leur représentation (norme IEEE 754) mérite un traitement séparé. L'objectif ici est de consolider les représentations indispensables avant d'aborder les traitements de données tabulaires.

## Formalisation

Une donnée informatique n'est pas seulement une valeur visible à l'écran : c'est une valeur **associée à une représentation**. La même suite de bits peut représenter des choses très différentes selon la convention adoptée. Par exemple, les huit bits `11111111` représentent 255 si l'on choisit la convention « entier positif sur 8 bits », mais −1 si l'on choisit la convention « complément à deux sur 8 bits ».

Choisir une représentation revient à répondre à trois questions fondamentales :

- **Quelles valeurs** doit-on pouvoir représenter ? (un entier positif ? un entier relatif ? un caractère ? une collection ?)
- **Quelles opérations** effectue-t-on le plus souvent ? (comparer ? additionner ? chercher par clé ? parcourir dans l'ordre ?)
- **Quelles erreurs** faut-il éviter ? (débordement de capacité ? confusion entre caractère et octet ? accès hors bornes ?)

Un bon choix de représentation simplifie les traitements et réduit les risques d'erreur. Un mauvais choix impose des conversions inutiles ou introduit des erreurs silencieuses.

## Définitions

- **Bit** : unité élémentaire d'information, qui prend la valeur `0` ou `1`.
- **Base de numération** : système positionnel utilisant un nombre fixé de chiffres (2 en binaire, 10 en décimal, 16 en hexadécimal).
- **Complément à deux** : convention de codage des entiers relatifs sur un nombre fixe de bits, où le bit de poids fort indique le signe.
- **Booléen** : valeur logique qui vaut `True` (vrai) ou `False` (faux).
- **Table de vérité** : tableau qui énumère toutes les combinaisons possibles des variables booléennes d'une expression et le résultat associé.
- **Encodage de texte** : règle qui associe des caractères à des suites d'octets (ASCII, UTF-8, etc.).
- **Liste Python** : collection ordonnée et modifiable, où les éléments sont repérés par leur index.
- **Tuple Python** : collection ordonnée, généralement utilisée comme p-uplet de valeurs liées, non modifié après création.
- **Dictionnaire Python** : structure qui associe des clés uniques à des valeurs, permettant un accès direct par clé.

Définition formelle 1 — Sur `n` bits non signés, l'ensemble des valeurs représentables est `{0, 1, ..., 2ⁿ - 1}`.

Définition formelle 2 — En base `b`, une écriture `aₖ...a₁a₀` représente la valeur `aₖ×bᵏ + ... + a₁×b + a₀`, avec `0 ≤ aᵢ < b`.

Définition formelle 3 — Une structure de données associe une organisation des valeurs à des opérations autorisées : lecture par indice pour une liste, accès par clé pour un dictionnaire, décomposition positionnelle pour un tuple.

## Exemples corrigés — repères

Les exemples corrigés qui suivent doivent être lus comme des modèles de méthode : conversion par divisions successives, développement en puissances, calcul de complément à deux, table de vérité, encodage de texte et choix de conteneur Python. Pour chaque exemple, on vérifie le résultat par une opération inverse ou par un cas limite.

## Exercices intégrés — progression

Les exercices intégrés sont répartis dans le cours pour alterner méthode et entraînement immédiat. Ils couvrent les conversions, les bornes de représentation, le complément à deux, les booléens, l'encodage de texte, les listes, tuples, dictionnaires et les tests. Une correction exploitable figure dans `corrige.md`.

## Bases 2, 10 et 16

En base 10, nous utilisons dix chiffres (de `0` à `9`) et chaque position correspond à une puissance de 10. En base 2 (binaire), seuls deux chiffres sont disponibles (`0` et `1`) et chaque position correspond à une puissance de 2. En base 16 (hexadécimal), on dispose de seize symboles : les chiffres `0` à `9` complétés par les lettres `A` à `F` qui représentent respectivement les valeurs 10 à 15.

Dans toute écriture positionnelle, le **poids** d'un chiffre dépend de sa position. Ainsi, l'écriture `1011₂` se décompose en `1×2³ + 0×2² + 1×2¹ + 1×2⁰`, soit `8 + 0 + 2 + 1 = 11₁₀`. De même, `2A₁₆` se lit `2×16¹ + 10×16⁰ = 32 + 10 = 42₁₀`.

La base 16 est particulièrement commode en informatique car chaque chiffre hexadécimal correspond exactement à 4 bits. Par exemple, `F₁₆ = 1111₂` et `A₁₆ = 1010₂`. Un **octet** (8 bits) se représente donc toujours avec exactement deux chiffres hexadécimaux : `11111111₂ = FF₁₆ = 255₁₀`.

### Exemple corrigé 1 — Convertir 45₁₀ en base 2

Pour convertir un entier positif de la base 10 vers la base 2, on effectue des divisions successives par 2 en notant chaque reste, puis on lit les restes du dernier au premier :

| Division   | Quotient | Reste |
|-----------|----------|-------|
| 45 ÷ 2   | 22       | 1     |
| 22 ÷ 2   | 11       | 0     |
| 11 ÷ 2   | 5        | 1     |
| 5 ÷ 2    | 2        | 1     |
| 2 ÷ 2    | 1        | 0     |
| 1 ÷ 2    | 0        | 1     |

En lisant les restes de bas en haut, on obtient : `45₁₀ = 101101₂`. On vérifie : `32 + 8 + 4 + 1 = 45`. ✓

### Contre-exemple 1 — « 101 vaut toujours cent-un »

C'est faux. L'écriture `101` dépend entièrement de la base dans laquelle on la lit : en base 10, elle vaut cent-un ; en base 2, `101₂` vaut cinq (`4 + 0 + 1`) ; en base 16, `101₁₆` vaut deux-cent-cinquante-sept (`256 + 0 + 1`). C'est pourquoi il faut **toujours préciser la base** quand il y a ambiguïté.

### Erreur fréquente 1 — Confondre nombre de chiffres décimaux et nombre de bits

Le nombre 100 s'écrit avec trois chiffres en base 10, mais sa représentation binaire `1100100₂` utilise sept bits. Le nombre de symboles nécessaires dépend de la base : plus la base est petite, plus il faut de symboles pour représenter la même valeur.

### Exercice intégré 1

1. Convertir `31₁₀` en base 2 par divisions successives.
2. Convertir `11110₂` en base 10 en développant les puissances de 2.
3. Convertir `2F₁₆` en base 10.
4. Vérifier que `1111₂` et `F₁₆` représentent bien la même valeur.

## Entiers positifs et intervalle représentable

Lorsqu'on dispose de `n` bits pour représenter un entier positif, les valeurs possibles vont de `0` à `2ⁿ − 1`. Par exemple, sur 4 bits, l'intervalle est `[0 ; 15]` ; sur 8 bits, il est `[0 ; 255]` ; sur 16 bits, il atteint `[0 ; 65 535]`. Le nombre de bits impose donc une **limite supérieure** : si un compteur codé sur 8 bits dépasse 255, la représentation déborde et le résultat devient incohérent.

Python masque en partie cette limite pour ses entiers natifs, car il utilise en interne une taille variable qui s'ajuste automatiquement. Cependant, dans les fichiers, les protocoles réseau, les formats d'image et les systèmes embarqués, les tailles sont fixées et la question du débordement est concrète.

### Exemple corrigé 2 — Combien de bits pour écrire 100₁₀ ?

On cherche le plus petit entier `n` tel que `2ⁿ > 100`. Comme `2⁶ = 64` ne suffit pas et `2⁷ = 128` dépasse 100, il faut au minimum **7 bits**. En effet, `100₁₀ = 1100100₂`, qui comporte bien 7 chiffres binaires.

## Entiers relatifs et complément à deux

Pour représenter des entiers négatifs, il ne suffit pas d'ajouter un bit de signe devant un entier positif (cette convention, dite « signe-magnitude », crée deux représentations pour zéro et complique l'addition). La convention la plus utilisée est le **complément à deux**, qui présente l'avantage de permettre les additions et soustractions avec le même circuit matériel.

Sur `n` bits en complément à deux, l'intervalle représentable va de **−2ⁿ⁻¹** à **2ⁿ⁻¹ − 1**. Concrètement :

- Sur 4 bits : de −8 à 7.
- Sur 8 bits : de −128 à 127.

Le **bit de poids fort** (le bit le plus à gauche) joue le rôle d'indicateur de signe : s'il vaut `0`, le nombre est positif ou nul ; s'il vaut `1`, le nombre est négatif.

**Pour encoder** un entier négatif `−x` sur `n` bits, on calcule `2ⁿ − x`. Par exemple, pour coder `−5` sur 8 bits : `256 − 5 = 251`, et `251₁₀ = 11111011₂`.

**Pour décoder** une valeur binaire dont le bit de poids fort vaut `1`, on interprète d'abord la suite comme un entier positif, puis on soustrait `2ⁿ`. Par exemple, `11111011₂ = 251₁₀`, et comme le bit de gauche vaut `1`, on calcule `251 − 256 = −5`.

### Exemple corrigé 3 — Coder −5 en complément à deux sur 8 bits

1. On calcule `2⁸ − 5 = 256 − 5 = 251`.
2. On convertit 251 en binaire : `251₁₀ = 11111011₂`.
3. Le résultat est `11111011` (8 bits, bit de gauche à `1` : bien négatif).
4. Vérification par décodage : `11111011₂ = 251₁₀`, puis `251 − 256 = −5`. ✓

### Contre-exemple 2 — La même suite de bits, deux valeurs différentes

La suite `11111011` représente **251** si on la lit comme un entier positif, mais **−5** si on la lit en complément à deux sur 8 bits. Ce n'est pas une erreur de calcul : c'est simplement que la convention d'interprétation n'est pas la même. Sans préciser cette convention, la suite de bits est ambiguë.

### Exercice intégré 2

1. Sur 8 bits, encoder `7`, `−1` et `−8` en complément à deux.
2. Sur 8 bits, décoder les suites `00001111`, `11111111` et `11111000`.
3. Donner l'intervalle représentable sur 4 bits en complément à deux.
4. Expliquer pourquoi la valeur `140` ne peut pas être codée comme entier relatif sur 8 bits (alors qu'elle entre sur 8 bits comme entier positif).

## Booléens et tables de vérité

Un **booléen** ne peut prendre que deux valeurs : `True` (vrai) ou `False` (faux). En Python, les trois opérateurs fondamentaux sont `and` (et logique), `or` (ou logique) et `not` (négation). On peut combiner ces opérateurs pour former des **expressions booléennes** arbitrairement complexes.

Une **table de vérité** est un outil systématique qui liste toutes les combinaisons possibles des variables d'entrée et le résultat de l'expression pour chacune. Avec une variable, il y a 2 lignes ; avec deux variables, 4 lignes ; avec trois variables, 8 lignes (en général, `2ⁿ` lignes pour `n` variables).

Voici les règles de base à retenir :

- `and` vaut `True` uniquement si **les deux** entrées sont vraies ;
- `or` vaut `True` si **au moins une** entrée est vraie (c'est un « ou inclusif ») ;
- `not` inverse la valeur : `not True` donne `False`, et réciproquement.

Le **ou exclusif** (souvent noté XOR) est une opération différente de `or` : il vaut `True` si **exactement une** des deux entrées est vraie, mais `False` si les deux sont vraies. En Python, il n'existe pas de mot-clé `xor` pour les booléens, mais on peut l'exprimer par `(a and not b) or (not a and b)`.

### Exemple corrigé 4 — Table de vérité de `a and not b`

| `a`     | `b`     | `not b` | `a and not b` |
|---------|---------|---------|----------------|
| `False` | `False` | `True`  | `False`        |
| `False` | `True`  | `False` | `False`        |
| `True`  | `False` | `True`  | **`True`**     |
| `True`  | `True`  | `False` | `False`        |

Seule la combinaison `a = True, b = False` donne `True`. La table de vérité permet de raisonner de manière exhaustive au lieu de deviner le résultat.

### Erreur fréquente 2 — Confondre `or` et « ou exclusif »

Beaucoup d'élèves croient que `or` signifie « l'un ou l'autre, mais pas les deux ». C'est faux en Python : `True or True` vaut `True`, car `or` est **inclusif**. Si l'on veut un ou exclusif, il faut le formuler explicitement, par exemple avec `(a and not b) or (not a and b)`.

### Exercice intégré 3

1. Dresser la table de vérité complète de `not a or b` (4 lignes).
2. Dresser la table de vérité de `(a and b) or (a and not b)`.
3. Observer le résultat de la deuxième table : peut-on simplifier cette expression ?

## Texte, ASCII et Unicode

Un texte informatique est une suite de **caractères**, mais un caractère n'est pas directement un octet. Pour passer de l'un à l'autre, il faut un **système d'encodage** qui définit comment chaque caractère est représenté en mémoire.

**ASCII** (American Standard Code for Information Interchange) est un ancien encodage qui attribue un code numérique à 128 caractères : les lettres anglaises non accentuées, les chiffres, quelques signes de ponctuation et des caractères de contrôle. Par exemple, la lettre `A` a le code 65 et la lettre `a` le code 97. Cet encodage suffit pour l'anglais de base, mais il est incapable de représenter les lettres accentuées du français, les caractères arabes, chinois, ou les émojis.

**Unicode** résout ce problème en attribuant un **point de code** unique à un très grand nombre de caractères (plus de 150 000 aujourd'hui). Le point de code est un numéro abstrait : par exemple, `A` a le point de code U+0041 (soit 65 en décimal) et `é` a le point de code U+00E9 (soit 233). Mais le point de code ne dit pas encore comment le caractère est stocké en octets.

**UTF-8** est l'encodage le plus courant d'Unicode en octets. Il utilise un nombre variable d'octets par caractère : un seul octet pour les caractères ASCII (compatibilité totale), deux octets pour les lettres accentuées européennes, et jusqu'à quatre octets pour les caractères rares ou les émojis. C'est pourquoi le nombre de caractères d'une chaîne n'est pas toujours égal au nombre d'octets qu'elle occupe.

### Exemple corrigé 5 — Points de code et encodage UTF-8

En Python, la fonction `ord` renvoie le point de code d'un caractère, et `chr` fait l'inverse :

```python
>>> ord("A")
65
>>> chr(65)
'A'
>>> ord("é")
233
```

Pour voir la représentation en octets, on peut utiliser la méthode `encode` :

```python
>>> "A".encode("utf-8")
b'\x41'          # 1 octet
>>> "é".encode("utf-8")
b'\xc3\xa9'      # 2 octets
```

La lettre `A` occupe un seul octet (car son point de code est inférieur à 128), tandis que `é` en occupe deux. Cela signifie que pour une chaîne comme `"Aé"`, la longueur en caractères est 2, mais la taille en octets UTF-8 est 3.

### Contre-exemple 3 — « Un caractère vaut toujours un octet »

Cette affirmation est fausse en général. Elle est vraie uniquement pour les 128 caractères ASCII de base. Dès qu'on utilise un caractère accentué, un idéogramme ou un émoji, l'encodage UTF-8 nécessite plusieurs octets. Confondre le nombre de caractères et le nombre d'octets peut provoquer des erreurs dans le traitement de fichiers texte ou dans les communications réseau.

## Listes et tableaux Python

En Python, une **liste** est une collection ordonnée et modifiable d'éléments, repérés par des **index** entiers commençant à 0. On peut lire un élément (`notes[0]`), le modifier (`notes[1] = 14`), ajouter un élément en fin de liste (`notes.append(18)`), ou parcourir tous les éléments avec une boucle `for`.

La liste est le type construit le plus polyvalent en Python. Elle convient bien lorsque l'**ordre** des éléments compte, lorsqu'on a besoin de **parcourir** tous les éléments, ou lorsqu'on veut **modifier** la collection au fil du programme.

Une **compréhension de liste** permet de construire une liste à partir d'une règle concise. Par exemple, `[x*x for x in range(5)]` produit la liste `[0, 1, 4, 9, 16]` en élevant au carré chaque entier de 0 à 4.

On peut aussi représenter une **matrice** (tableau à deux dimensions) par une liste de listes. Par exemple, si `m = [[1, 2, 3], [4, 5, 6]]`, alors `m[1][2]` désigne l'élément à la ligne 1, colonne 2, soit la valeur 6.

### Exemple corrigé 6 — Lecture, modification et compréhension

```python
valeurs = [4, 7, 9]
```

- `valeurs[0]` vaut `4` (premier élément, index 0).
- `valeurs[1]` vaut `7` (deuxième élément, index 1).
- `valeurs[2]` vaut `9` (troisième élément, index 2).
- La somme se calcule par `total = sum(valeurs)`, soit 20.
- La compréhension `[v + 1 for v in valeurs]` produit `[5, 8, 10]` : chaque élément est augmenté de 1.

### Erreur fréquente 3 — Index commençant à 1

En Python, les index commencent à **0**, pas à 1. Dans une liste de longueur 3, les index valides sont `0`, `1` et `2`. Tenter d'accéder à `valeurs[3]` provoque une erreur `IndexError`. C'est un cas limite classique qu'il faut systématiquement tester.

### Exercice intégré 4

1. Écrire une compréhension de liste qui double chaque élément de `[3, 5, 8]`.
2. Soit `m = [[1, 0], [0, 1]]`. Que vaut `m[0][1]` ? Et `m[1][0]` ?
3. Écrire une boucle qui additionne tous les éléments d'une liste `nombres`.

## Tuples et p-uplets

Un **tuple** Python est une collection ordonnée qui sert à regrouper un petit nombre de valeurs liées entre elles. Contrairement à une liste, un tuple n'est généralement pas modifié après sa création (on dit qu'il est **immutable** dans l'usage courant, bien que Python n'interdise pas de remplacer la variable qui le contient).

Le tuple est adapté aux situations où le **nombre de champs est fixe** et où l'**ordre des champs est connu** par convention. Par exemple, un point du plan se représente naturellement par `(x, y)`, et une couleur RGB par `(rouge, vert, bleu)`. En revanche, un tuple devient fragile et peu lisible dès que le nombre de champs augmente, car le lecteur doit mémoriser la position de chaque valeur.

L'intérêt principal du tuple dans le cadre du programme est qu'une **fonction peut renvoyer un p-uplet** — c'est-à-dire plusieurs valeurs regroupées en un seul objet retourné.

### Exemple corrigé 7 — Fonction renvoyant un tuple (milieu de deux points)

On veut écrire une fonction qui calcule le milieu de deux points du plan, chaque point étant représenté par un tuple `(x, y)` :

```python
def milieu(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
```

L'appel `milieu((1, 3), (5, 7))` renvoie le tuple `(3.0, 5.0)`. Le tuple permet de renvoyer les deux coordonnées du milieu en un seul objet, sans avoir à créer deux variables séparées ou à utiliser une structure plus lourde.

### Contre-exemple 4 — Un tuple trop long perd en lisibilité

Représenter une fiche élève par un tuple comme `(id, nom, groupe, option, date, mail)` est techniquement possible, mais fragile : le lecteur du code doit se souvenir que l'index 3 correspond à l'option et l'index 5 au mail. Un **dictionnaire** avec des clés nommées (`{"id": 42, "nom": "Ada", ...}`) serait ici bien plus lisible et moins sujet aux erreurs d'index.

## Dictionnaires

Un **dictionnaire** Python associe des **clés** à des **valeurs**. Chaque clé est unique et permet d'accéder directement à la valeur correspondante, sans avoir à parcourir toute la structure. Par exemple, `stock = {"stylo": 18, "cahier": 5}` associe la clé `"stylo"` à la valeur 18 et la clé `"cahier"` à la valeur 5. On accède ensuite au stock de stylos par `stock["stylo"]`.

Le dictionnaire est le type construit adapté lorsque l'opération la plus fréquente est un **accès par nom ou identifiant**, lorsqu'on veut **compter des occurrences** (chaque clé étant un élément à compter, et la valeur associée étant l'effectif), ou lorsqu'on veut représenter un **enregistrement** avec des champs nommés.

Les méthodes `keys()`, `values()` et `items()` permettent de parcourir un dictionnaire :

- `stock.keys()` donne les clés : `"stylo"`, `"cahier"`.
- `stock.values()` donne les valeurs : `18`, `5`.
- `stock.items()` donne les couples clé-valeur : `("stylo", 18)`, `("cahier", 5)`.

### Exemple corrigé 8 — Compter des votes avec un dictionnaire

On dispose d'une liste de votes : `votes = ["A", "B", "A", "C", "A"]`. On veut compter le nombre de votes pour chaque choix.

```python
effectifs = {}
for choix in votes:
    if choix in effectifs:
        effectifs[choix] += 1
    else:
        effectifs[choix] = 1
```

Après exécution, `effectifs` vaut `{"A": 3, "B": 1, "C": 1}`. La clé est le choix de vote, la valeur est l'effectif. Le dictionnaire est ici la structure adaptée car on a besoin d'associer chaque choix à son compte, et d'y accéder directement par le nom du choix.

### Contre-exemple 5 — Liste de couples vs dictionnaire

On pourrait stocker les mêmes données avec une liste de couples : `[("A", 3), ("B", 1), ("C", 1)]`. Mais si l'on cherche souvent le nombre de votes pour un choix donné (par exemple `"C"`), il faudrait parcourir toute la liste à chaque fois, car les éléments ne sont accessibles que par leur position. Avec un dictionnaire, l'accès par clé `effectifs["C"]` est direct. Le choix entre les deux structures dépend donc des opérations que l'on prévoit d'effectuer le plus souvent.

## Choisir une représentation

Le choix entre liste, tuple et dictionnaire ne se fait pas au hasard : il doit être guidé par les **opérations prévues** sur les données.

| Situation | Structure adaptée | Justification |
|-----------|-------------------|---------------|
| Suite de mesures à parcourir et modifier | Liste | L'ordre compte, les valeurs changent |
| Coordonnées `(x, y)` d'un point fixe | Tuple | Nombre de champs fixe, pas de modification |
| Stock de produits accessibles par référence | Dictionnaire | L'accès se fait par nom de produit |
| Table de pixels ligne par ligne | Liste de listes | Structure à deux dimensions, modifiable |
| Fiche courte avec champs nommés | Dictionnaire | L'accès par nom de champ est prioritaire |

Pour les types de base, le choix de la taille en bits détermine l'intervalle représentable (entiers positifs ou relatifs), et le choix de l'encodage détermine comment les caractères sont stockés. Dans tous les cas, le choix doit être **justifié par un traitement** — c'est-à-dire par une opération concrète que l'on effectuera sur les données.

## Tests et cas limites

Un **test** vérifie qu'une fonction produit le résultat attendu pour une entrée choisie. Un **cas limite** est une valeur particulière qui risque de révéler une erreur de programmation : une valeur à la frontière du domaine de validité, un cas dégénéré, ou une entrée qui déclenche un traitement spécial.

Voici des exemples de cas limites pertinents pour cette séquence :

- **Conversions de base** : tester avec `0` (traitement spécial dans beaucoup d'algorithmes), avec `1` (plus petit entier non nul), et avec la plus grande valeur autorisée par le nombre de bits.
- **Complément à deux** : tester `−1` (tous les bits à `1`), les bornes de l'intervalle (`−128` et `127` sur 8 bits), et une valeur juste hors de l'intervalle.
- **Texte et encodage** : tester avec un caractère accentué (`"é"`) et un caractère multi-octets.
- **Listes** : tester avec une liste vide (`[]`).
- **Dictionnaires** : tester l'accès à une clé absente (provoque un `KeyError`).

Un jeu de tests ne prouve jamais que la fonction est correcte dans tous les cas possibles, mais un bon jeu de tests — couvrant des cas ordinaires **et** des cas limites — réduit considérablement le risque d'erreurs non détectées.

Le fichier Python associé à ce cours est `python/representation_tools.py`, et les tests correspondants sont dans `tests/test_representation_tools.py`. Vous pouvez les exécuter pour vérifier le bon fonctionnement de chaque fonction.

## Erreurs fréquentes — Récapitulatif

1. **Oublier de préciser la base** d'une écriture : `101` n'a pas de sens unique sans indication de base.
2. **Lire un complément à deux comme un entier positif** : `11111111` ne vaut pas 255 si la convention est le complément à deux sur 8 bits.
3. **Confondre caractère et octet** : `"é"` est un seul caractère mais occupe deux octets en UTF-8.
4. **Utiliser une liste quand un dictionnaire s'impose** : si l'accès par clé est fréquent, une liste force un parcours inutile.
5. **Oublier que les index Python commencent à zéro** : dans une liste de 3 éléments, le dernier index est 2, pas 3.
6. **Croire qu'un test réussi prouve tout** : un test ne couvre qu'un cas ; il faut varier les entrées et inclure des cas limites.

## À retenir

- Une suite de bits n'a de sens que par la convention de représentation qui lui est associée.
- Les bases 2, 10 et 16 sont trois écritures positionnelles d'une même valeur entière.
- Le complément à deux permet de coder les entiers relatifs sur un nombre fixé de bits, avec un intervalle asymétrique (une valeur négative de plus que de valeurs positives).
- Une table de vérité rend explicite le comportement d'une expression booléenne pour toutes les entrées possibles.
- Unicode attribue un point de code à chaque caractère ; UTF-8 est l'encodage le plus courant pour stocker ces points de code en octets.
- Une liste est ordonnée et modifiable ; un tuple regroupe un petit nombre de valeurs liées ; un dictionnaire associe des clés à des valeurs.
- Le choix d'une représentation dépend toujours des traitements que l'on prévoit d'effectuer.
- Les tests doivent couvrir des cas ordinaires **et** des cas limites pour être utiles.

## Extension

Pour aller plus loin sans sortir du programme, comparer deux manières de coder une même information :

1. un entier naturel `35` stocké sur 6 bits (`100011`) puis sur 8 bits (`00100011`) ;
2. la valeur `11111111` lue comme entier naturel (`255`) puis comme entier relatif en complément à deux (`−1`) ;
3. une table de pixels représentée par une liste de listes, puis par un dictionnaire associant chaque coordonnée à une couleur.

L'objectif n'est pas d'ajouter des notions nouvelles, mais de montrer qu'une représentation peut être correcte dans un contexte et dangereuse dans un autre.

## Aides progressives

- **Aide 1 — Conversion décimal vers binaire :** écrire les divisions successives par 2 et conserver les restes.
- **Aide 2 — Conversion binaire vers décimal :** écrire les puissances de 2 sous chaque bit avant d'additionner.
- **Aide 3 — Complément à deux :** si le bit de gauche vaut `1`, décoder d'abord comme entier positif puis soustraire `2ⁿ`.
- **Aide 4 — Choix de structure :** si l'accès se fait par position, penser liste ou tuple ; si l'accès se fait par nom, penser dictionnaire.
- **Aide 5 — Test :** vérifier au moins un cas minimal (`0`, liste vide, clé absente) avant de considérer la réponse robuste.

## Auto-évaluation

Avant de passer au TD, vérifiez que vous savez :

- convertir `37₁₀` en base 2 et `2A₁₆` en base 10 ;
- donner l'intervalle des entiers relatifs représentables sur 8 bits ;
- décoder `11111110` en complément à deux sur 8 bits ;
- dresser la table de vérité d'une expression à deux variables ;
- expliquer pourquoi `é` n'est pas un caractère ASCII simple ;
- choisir entre liste, tuple et dictionnaire pour un problème donné ;
- proposer au moins deux cas limites pour tester une fonction de conversion.
