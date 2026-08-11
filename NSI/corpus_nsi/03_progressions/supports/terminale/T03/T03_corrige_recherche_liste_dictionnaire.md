---
title: "T03 - Corrigé - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "corrige"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "recherche, liste, dictionnaire, index, clé, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03C"
---

# Corrigé — Recherche dans une liste vs dans un dictionnaire

## Capacité visée

> Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

## Corrigé du TD

### Exercice 1 — Tracer une recherche dans une liste

**1.1.** Tableau de trace pour `"datte" in fruits` :

| Étape | Élément courant | Comparaison avec `"datte"` | Résultat | Commentaire |
|-------|-----------------|----------------------------|----------|-------------|
| 1 | `"pomme"` | `"pomme" == "datte"` | `False` | Premier élément, pas de correspondance |
| 2 | `"banane"` | `"banane" == "datte"` | `False` | Deuxième élément, pas de correspondance |
| 3 | `"cerise"` | `"cerise" == "datte"` | `False` | Troisième élément, pas de correspondance |
| 4 | `"datte"` | `"datte" == "datte"` | `True` | Correspondance trouvée, arrêt du parcours |

**1.2.** 4 comparaisons ont été effectuées.

**1.3.** Si on cherche `"kiwi"` (absent), il faut parcourir toute la liste : **5 comparaisons** (autant que la taille de la liste). Dans le pire cas, on compare avec chaque élément sans trouver de correspondance.

**1.4.** Complexité de la recherche dans une liste de taille `n` :

- Meilleur cas : O(1) — l'élément est en première position.
- Pire cas : O(n) — l'élément est en dernière position ou absent.
- Cas moyen : O(n) — en moyenne, on parcourt n/2 éléments, soit O(n).

---

### Exercice 2 — Tracer une recherche dans un dictionnaire

**2.1.** Python calcule le **hachage** de la clé `"cerise"` via `hash("cerise")`, ce qui donne un entier qui détermine directement l'emplacement mémoire à vérifier dans la table de hachage interne du dictionnaire. Il n'y a pas de parcours des autres clés.

**2.2.** En moyenne, **1 seule comparaison** est nécessaire. Le hachage donne directement la position en mémoire ; Python vérifie juste que la clé à cette position correspond. La complexité est O(1).

**2.3.** `8 in stock` renvoie `False`. L'opérateur `in` appliqué à un dictionnaire cherche parmi les **clés**, pas parmi les valeurs. Or `8` n'est pas une clé de `stock` (les clés sont `"pomme"`, `"banane"`, `"cerise"`, `"datte"`, `"figue"`).

**2.4.** Pour chercher la valeur `8` parmi les valeurs :

```python
8 in stock.values()
```

Cette opération a une complexité **O(n)** car `stock.values()` renvoie une vue itérable et `in` effectue un parcours séquentiel de toutes les valeurs.

---

### Exercice 3 — Comparaison de complexité

**3.1.** Expressions Python :

```python
# Représentation A (liste de tuples)
any(nom == "Dupont" for nom, tel in annuaire_A)
# ou : "Dupont" in [nom for nom, tel in annuaire_A]

# Représentation B (dictionnaire)
"Dupont" in annuaire_B
```

**3.2.** Complexités :

- Représentation A : **O(n)** — il faut parcourir la liste de tuples séquentiellement pour comparer chaque nom.
- Représentation B : **O(1)** en moyenne — le dictionnaire utilise une table de hachage qui donne un accès direct par clé.

**3.3.** Tableau complété (n = 100 000) :

| Nombre de recherches `k` | Représentation A (liste) | Représentation B (dictionnaire) |
|--------------------------|--------------------------|-------------------------------|
| 1 | 100 000 opérations | 1 opération |
| 100 | 10 000 000 opérations | 100 opérations |
| 10 000 | 1 000 000 000 opérations | 10 000 opérations |

Le coût total est `k * n` pour la liste et `k * 1` pour le dictionnaire.

**3.4.** L'écart est significatif dès `k = 1` puisque chaque recherche individuelle prend déjà O(n) = 100 000 opérations dans la liste contre O(1) dans le dictionnaire. Cependant, l'impact devient critique pour des valeurs de `k` de l'ordre de la centaine ou plus. Le dictionnaire est le choix adapté dès que des recherches par nom sont fréquentes.

**3.5.** La liste reste préférable quand on a besoin de conserver un **ordre** précis des éléments (par exemple, un classement) ou quand on doit accéder aux éléments **par position** (le n-ième élément). Elle est aussi adaptée quand les données sont peu nombreuses et qu'aucune recherche par identifiant n'est nécessaire.

---

## Corrigé de l'évaluation

### Question 1

**1.a)** Python effectue un **parcours séquentiel** de la liste `villes_liste`. Il compare `"Marseille"` successivement avec `"Paris"` (non), `"Lyon"` (non), puis `"Marseille"` (oui, arrêt). **3 comparaisons** sont effectuées.

**1.b)** Python calcule `hash("Marseille")` pour déterminer directement l'emplacement de cette clé dans la table de hachage interne du dictionnaire. Il vérifie cet emplacement sans parcourir les autres clés. La complexité en moyenne est **O(1)**.

**1.c)**

- `"Marseille" in villes_liste` : **O(n)** — parcours séquentiel, le temps croît avec la taille de la liste.
- `"Marseille" in villes_dico` : **O(1)** — accès direct par hachage, le temps est constant quelle que soit la taille du dictionnaire.

La différence vient du mécanisme : la liste impose un parcours, le dictionnaire utilise le hachage pour un accès direct.

### Question 2

**2.a)** Solution A : pour chaque mot parmi les 10 000, on effectue une recherche dans une liste de 300 000 mots, soit O(n) = 300 000 comparaisons dans le pire cas. Total : `10 000 * 300 000 = 3 * 10^9` opérations (3 milliards).

**2.b)** Solution B : pour chaque mot parmi les 10 000, on effectue une recherche dans un dictionnaire en O(1), soit 1 opération en moyenne. Total : `10 000 * 1 = 10 000` opérations.

**2.c)** La solution B est bien plus adaptée. Elle effectue 10 000 opérations contre 3 milliards pour la solution A, soit un facteur 300 000 (la taille du lexique). Pour un lexique volumineux avec de nombreuses requêtes, le dictionnaire est indispensable.

### Question 3

**3.a)**

- Test 1 : `50 in inventaire` renvoie **`False`**. L'opérateur `in` cherche parmi les **clés** du dictionnaire. Les clés sont `"stylo"`, `"cahier"`, `"gomme"`, `"règle"`. L'entier `50` n'en fait pas partie.
- Test 2 : `"stylo" in inventaire` renvoie **`True`**. `"stylo"` est bien une clé du dictionnaire.

**3.b)** L'erreur de l'élève est de croire que `in` cherche parmi les **valeurs** du dictionnaire. En réalité, `in` appliqué à un dictionnaire cherche parmi les **clés**. La valeur `50` est bien présente (associée à la clé `"stylo"`), mais `50` n'est pas une clé, donc le résultat est `False`.

**3.c)** Pour vérifier si la valeur `50` est présente :

```python
50 in inventaire.values()
```

Cette opération est en **O(n)** car `inventaire.values()` renvoie une vue itérable et l'opérateur `in` doit parcourir séquentiellement toutes les valeurs (pas de hachage sur les valeurs).


## Objectifs


## Capacités officielles


## Prérequis


## Situation-problème

Un programme de correcteur orthographique doit vérifier si un mot appartient au dictionnaire français (300 000 mots). La recherche séquentielle prend trop de temps. Comment accélérer ?

## Activité d’entrée

Mesurer le temps de recherche de 10 000 mots dans une liste de 100 000 éléments, puis dans un dictionnaire de 100 000 clés. Comparer.

## Exemple

Démonstration collective du temps de recherche dans une liste de 100 000 éléments vs un dictionnaire de même taille.

## Exercices

Exercices de recherche dans des listes et dictionnaires avec analyse de complexité.

## Erreurs fréquentes

- EF1 : confondre la complexité de recherche dans une liste (O(n)) et dans un dictionnaire (O(1)).
- EF2 : oublier que `val in dico.values()` est en O(n) et non O(1).
- EF3 : mélanger index de position (liste) et clé d'accès (dictionnaire).


## Remédiation

Exercice de remédiation : chronométrer manuellement 100 recherches dans une liste puis dans un dictionnaire et expliquer l'écart.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

- Critère de réussite : les mesures de temps confirment O(n) pour la liste et O(1) pour le dictionnaire.
- Critère de validation : l'élève justifie la différence de complexité par le mécanisme d'accès.
- Observable : le code de benchmark est correct et les résultats cohérents.


## Séance(s) correspondante(s)

Séance dédiée.

### Corrigé exercice 1

**Méthode** : on trace la recherche séquentielle dans la liste en comptant les comparaisons.
Pour chercher `42` dans `[10, 20, 30, 42, 50]`, on compare `10`, `20`, `30`, `42` : trouvé après `4` comparaisons. La recherche renvoie `True` et la complexité vaut `O(n)` dans le pire cas.

















### Corrigé exercice 2

Réponse détaillée avec justification.

Résultat attendu : `"cerise" in stock` renvoie `True` en `1` seule comparaison grâce au hachage, avec une complexité de `O(1)`.

### Corrigé exercice 3

Réponse détaillée avec justification.

Résultat attendu : pour `100000` éléments et `k = 10000` recherches, la liste donne `10^9` opérations contre `10000` pour le dictionnaire, soit une complexité de `O(n)` vs `O(1)`.

### Corrigé exercice 4

Réponse détaillée avec justification.

Résultat attendu : `"Marseille" in villes_liste` renvoie `True` après `3` comparaisons avec une complexité de `O(n)`.

### Corrigé exercice 5

Réponse détaillée avec justification.

Résultat attendu : `"Marseille" in villes_dico` renvoie `True` en `O(1)` grâce au hachage, contre `O(n)` pour la liste.

### Corrigé exercice 6

Réponse détaillée avec justification.

Résultat attendu : la solution B donne `10000` opérations contre `3 * 10^9` pour la solution A, soit un facteur `300000`.

### Corrigé exercice 7

Réponse détaillée avec justification.

Résultat attendu : `50 in inventaire` renvoie `False` car `in` cherche parmi les clés, et `"stylo" in inventaire` renvoie `True`.

### Corrigé exercice 8

Réponse détaillée avec justification.

Résultat attendu : `50 in inventaire.values()` renvoie `True` avec une complexité de `O(n)` car les valeurs sont parcourues séquentiellement.

