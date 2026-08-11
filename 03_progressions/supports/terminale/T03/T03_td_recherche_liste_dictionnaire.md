---
title: "T03 - TD - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "td"
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

# TD — Recherche dans une liste vs dans un dictionnaire

## Capacité visée

> T-STRUCT-03C — Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

## Exercice 1 — Tracer une recherche dans une liste

On considère la liste suivante :

```python
fruits = ["pomme", "banane", "cerise", "datte", "figue"]
```

On exécute `"datte" in fruits`.

**1.1.** Reproduire et compléter le tableau de trace ci-dessous en indiquant, pour chaque étape du parcours séquentiel, l'élément comparé et le résultat de la comparaison.

| Étape | Élément courant | Comparaison avec `"datte"` | Résultat |
|-------|-----------------|----------------------------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

**1.2.** Combien de comparaisons ont été effectuées ?

**1.3.** Si on cherchait `"kiwi"` (absent de la liste), combien de comparaisons seraient nécessaires ? Justifier.

**1.4.** Quelle est la complexité de cette recherche en fonction de `n`, la taille de la liste ? Donner le meilleur cas, le pire cas et le cas moyen.

---

## Exercice 2 — Tracer une recherche dans un dictionnaire

On considère le dictionnaire suivant :

```python
stock = {"pomme": 30, "banane": 15, "cerise": 8, "datte": 22, "figue": 5}
```

On exécute `"cerise" in stock`.

**2.1.** Décrire en une phrase le mécanisme utilisé par Python pour vérifier si la clé `"cerise"` est présente dans `stock`. Utiliser le mot « hachage » dans la réponse.

**2.2.** Combien de comparaisons sont nécessaires en moyenne pour cette opération ? Justifier.

**2.3.** On exécute maintenant `8 in stock`. Que renvoie cette expression ? Expliquer pourquoi.

**2.4.** Comment faudrait-il écrire le test pour vérifier si la valeur `8` est présente parmi les valeurs du dictionnaire ? Quelle serait alors la complexité ?

---

## Exercice 3 — Comparaison de complexité

On dispose d’un annuaire contenant `n` entrées. On hésite entre deux représentations :

- **Représentation A** : une liste de tuples `[(nom, tel), ...]`
- **Représentation B** : un dictionnaire `{nom: tel, ...}`

**3.1.** Pour chaque représentation, écrire en Python l'expression qui teste si le nom `"Dupont"` est dans l'annuaire.

**3.2.** Donner la complexité de chaque test. Justifier.

**3.3.** On effectue `k` recherches successives dans un annuaire de `n = 100 000` entrées. Compléter le tableau suivant avec l'ordre de grandeur du nombre total d'opérations :

| Nombre de recherches `k` | Représentation A (liste) | Représentation B (dictionnaire) |
|--------------------------|--------------------------|-------------------------------|
| 1 | | |
| 100 | | |
| 10 000 | | |

**3.4.** Pour quelle valeur de `k` l'écart de performance devient-il significatif ? Justifier le choix de structure le plus adapté.

**3.5.** Donner un cas d'usage où la liste reste préférable au dictionnaire, malgré sa recherche plus lente. Justifier.


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

## Corrigé

Les corrigés détaillés sont dans T03_corrige_recherche_liste_dictionnaire.md.

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

### Exercice 1 — Recherche séquentielle dans une liste

**Donnée** : On dispose de la liste `villes = ["Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux"]`. On recherche `"Nantes"`.
**Consigne** : Écrire une fonction `recherche_sequentielle(lst, cible)` qui parcourt la liste élément par élément et renvoie l'indice de `cible` si elle est trouvée, ou `-1` sinon. Tracer l'exécution sur la recherche de `"Nantes"` en complétant un tableau (étape, élément comparé, trouvé ?). Compter le nombre de comparaisons effectuées. Indiquer le nombre de comparaisons dans le pire cas (élément absent).
**Livrable** : Le code de la fonction, le tableau de trace et le décompte des comparaisons.
**Corrigé** : Le corrigé détaillé se trouve dans le fichier corrigé complément, exercice 1.

### Exercice 2 — Recherche par clé dans un dictionnaire

**Donnée** : Le dictionnaire suivant est `population = {"Lyon": 516092, "Marseille": 870018, "Toulouse": 486828, "Nice": 340017, "Nantes": 314138}`.
**Consigne** : (a) Écrire l'expression Python qui teste si `"Toulouse"` est une clé de `population`. (b) Accéder à la population de Toulouse. (c) Expliquer en une phrase pourquoi cette opération ne nécessite pas de parcourir toutes les clés (utiliser le mot « table de hachage »). (d) Tester si la valeur `314138` est une clé du dictionnaire. Expliquer le résultat.
**Livrable** : Les expressions Python, les résultats et l'explication du mécanisme de hachage.
**Corrigé** : Voir la correction complète dans le corrigé complément (exercice 2).

### Exercice 3 — Complexité O(n) vs O(1)

**Donnée** : On considère une liste de `n` éléments et un dictionnaire de `n` clés contenant les mêmes données.
**Consigne** : (a) Rappeler la complexité de `element in liste` et de `cle in dico`. Justifier chaque réponse. (b) Pour `n = 1 000 000`, estimer le nombre d'opérations dans le pire cas pour chaque structure. (c) Si chaque opération prend 1 microseconde, calculer le temps total pour 10 000 recherches dans la liste puis dans le dictionnaire. (d) Compléter un tableau comparatif avec les colonnes `n`, `temps liste (pire cas)`, `temps dico`.
**Livrable** : Le tableau comparatif rempli pour `n = 100`, `n = 10 000` et `n = 1 000 000`, avec les temps estimés.
**Corrigé** : Corrigé avec justification : fichier corrigé complément, exercice 3.

### Exercice 4 — Construction d'un dictionnaire depuis une liste

**Donnée** : On dispose d'une liste de tuples représentant des produits et leurs prix : `produits = [("pain", 1.20), ("lait", 0.95), ("beurre", 2.50), ("farine", 1.10), ("oeufs", 3.20)]`.
**Consigne** : (a) Construire un dictionnaire `catalogue` à partir de cette liste en utilisant une boucle `for`. (b) Refaire la construction en une seule ligne avec `dict()` et la liste de tuples. (c) Ajouter le produit `("sucre", 1.80)` au dictionnaire. (d) Écrire une recherche de prix : comparer le code et la complexité entre chercher un prix dans la liste de tuples (parcours séquentiel) et dans le dictionnaire (accès par clé).
**Livrable** : Les deux méthodes de construction, l'ajout, et la comparaison de recherche avec complexité.
**Corrigé** : Solution détaillée : exercice 4 du corrigé complément associé.

### Exercice 5 — Mesure de temps avec timeit

**Donnée** : On dispose du code suivant pour créer une liste et un dictionnaire de `n` éléments :
```python
import timeit
n = 100_000
liste = list(range(n))
dico = {i: True for i in range(n)}
```
**Consigne** : (a) Utiliser `timeit.timeit` pour mesurer le temps de `n - 1 in liste` (recherche du dernier élément, pire cas). (b) Mesurer le temps de `n - 1 in dico`. (c) Répéter pour `n = 1000`, `n = 10 000` et `n = 100 000`. (d) Consigner les résultats dans un tableau et calculer le ratio `temps_liste / temps_dico` pour chaque valeur de `n`. Conclure sur l'évolution du ratio quand `n` augmente.
**Livrable** : Le code de benchmark, le tableau de mesures et la conclusion sur la scalabilité.
**Corrigé** : Consulter le corrigé complément pour la solution de l'exercice 5.

### Exercice 6 — Recherche par valeur dans un dictionnaire O(n)

**Donnée** : Soit le dictionnaire `notes = {"Alice": 15, "Bob": 12, "Charlie": 18, "Diana": 15, "Eve": 9}`.
**Consigne** : (a) Écrire une fonction `trouver_par_valeur(dico, valeur)` qui renvoie la liste de toutes les clés associées à une valeur donnée. (b) Appeler cette fonction pour trouver tous les élèves ayant la note 15. (c) Expliquer pourquoi cette recherche est en O(n) et non en O(1), contrairement à la recherche par clé. (d) Proposer une structure de données inversée (dictionnaire `note -> [noms]`) qui permettrait une recherche par note en O(1). La construire.
**Livrable** : La fonction, l'appel de test, l'explication de complexité et le dictionnaire inversé.
**Corrigé** : La réponse attendue et sa justification sont dans le corrigé complément, exercice 6.

### Exercice 7 — Cas clé absente et méthode get()

**Donnée** : On travaille avec le dictionnaire `config = {"host": "localhost", "port": 8080, "debug": True}`.
**Consigne** : (a) Tenter d'accéder à `config["timeout"]` et noter l'erreur obtenue (`KeyError`). (b) Utiliser `config.get("timeout", 30)` pour obtenir une valeur par défaut. Expliquer la différence. (c) Écrire une fonction `acces_securise(dico, cle, defaut=None)` qui utilise `if cle in dico` pour renvoyer la valeur ou le défaut. (d) Comparer les trois approches (accès direct, `get()`, test `in`) en termes de lisibilité et de robustesse. Indiquer laquelle est préférable en production et pourquoi.
**Livrable** : Le code des trois approches, les résultats et la comparaison argumentée.
**Corrigé** : Exercice 7 : solution dans le corrigé complément (avec trace d'exécution).

### Exercice 8 — Comparaison de scalabilité à n = 10^6

**Donnée** : On souhaite comparer les performances de recherche dans une liste et un dictionnaire pour de très grandes tailles de données (`n = 10^6`).
**Consigne** : (a) Générer une liste de `n = 1 000 000` entiers et un dictionnaire de `n` clés entières. (b) Mesurer le temps de 1 000 recherches d'éléments présents (choisis aléatoirement) dans la liste puis dans le dictionnaire. (c) Mesurer le temps de 1 000 recherches d'éléments absents (`n + i` pour `i` de 0 à 999). (d) Présenter les résultats dans un tableau avec les colonnes : structure, type de recherche (présent/absent), temps total, temps moyen par recherche. (e) Conclure : à partir de quelle taille de données le dictionnaire devient-il indispensable ?
**Livrable** : Le code complet de benchmark, le tableau de résultats et la conclusion argumentée.
**Corrigé** : Pour la correction : voir exercice 8 dans le document corrigé complément.


Cas limite : recherche dans une liste vide. Cas limite : clé absente du dictionnaire.

