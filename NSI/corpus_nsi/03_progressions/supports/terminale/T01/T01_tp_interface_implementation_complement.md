---
title: "T01 - TP - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "tp"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures de données abstraites"
notion: "interface, implémentation, pile, file, liste chaînée, tableau"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-01B"
    - "T-STRUCT-01C"
---

# T01 - TP - Interface et implémentation complément

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

## Durée estimée : 1h30

---

## Partie A — Deux implémentations d’une pile (45 min)

### A.1 — Implémentation par liste Python

Créer un fichier `pile_liste.py` contenant la classe `PileListe` avec les méthodes suivantes :
- `__init__(self)` : initialise une pile vide (liste Python interne).
- `push(self, valeur)` : empile `valeur` au sommet.
- `pop(self)` : dépile et renvoie le sommet. Lève `IndexError` si la pile est vide.
- `is_empty(self)` : renvoie `True` si la pile est vide.

**Consignes :**
1. Écrire le code complet de la classe.
2. Tester dans la console :
   ```python
   p = PileListe()
   p.push(10)
   p.push(20)
   print(p.pop())       # attendu : 20
   print(p.is_empty())  # attendu : False
   print(p.pop())       # attendu : 10
   print(p.is_empty())  # attendu : True
   ```

### A.2 — Implémentation par liste chaînée

Créer un fichier `pile_chainee.py` contenant :
- La classe `Maillon` avec les attributs `valeur` et `suivant`.
- La classe `PileChainee` avec les mêmes méthodes que `PileListe` (même interface).

**Consignes :**
1. Écrire le code complet des deux classes.
2. Refaire exactement les mêmes tests que pour A.1 en remplaçant `PileListe` par `PileChainee`.
3. Vérifier que les résultats sont identiques.

### A.3 — Tests communs

Créer un fichier `tests_pile.py` contenant :

```python
def tests_communs_pile(classe_pile):
    """Suite de tests commune validant toute implémentation de pile."""
    # Test 1 : pile neuve est vide
    p = classe_pile()
    assert p.is_empty() == True, "Échec : pile neuve non vide"

    # Test 2 : push rend la pile non vide
    p.push(42)
    assert p.is_empty() == False, "Échec : pile non vide après push"

    # Test 3 : pop renvoie le dernier empilé (LIFO)
    p.push(10)
    p.push(20)
    assert p.pop() == 20, "Échec : LIFO non respecté"
    assert p.pop() == 10, "Échec : LIFO non respecté"

    # Test 4 : pile vide après push + pop
    p2 = classe_pile()
    p2.push(1)
    p2.pop()
    assert p2.is_empty() == True, "Échec : pile non vide après push+pop"

    # Test 5 : cas limite — pop sur pile vide
    try:
        classe_pile().pop()
        assert False, "Échec : pas d'erreur sur pop pile vide"
    except IndexError:
        pass

    # Test 6 : empilements multiples
    p3 = classe_pile()
    for i in range(100):
        p3.push(i)
    for i in range(99, -1, -1):
        assert p3.pop() == i, f"Échec : valeur {i} incorrecte"
    assert p3.is_empty() == True

    print(f"OK — tous les tests passent pour {classe_pile.__name__}")
```

**Consignes :**
1. Compléter le fichier avec les imports nécessaires.
2. Appeler `tests_communs_pile(PileListe)` et `tests_communs_pile(PileChainee)`.
3. Les deux appels doivent afficher "OK".

---

## Partie B — Deux implémentations d’une file (35 min)

### B.1 — Interface de la file

L'interface de la file comporte :
- `enfiler(valeur)` : ajoute un élément à la fin.
- `defiler()` : retire et renvoie l'élément au début. Lève `IndexError` si vide.
- `est_vide()` : renvoie `True` si la file est vide.

### B.2 — Implémentation par liste Python

Créer un fichier `file_liste.py` contenant la classe `FileListe` :
- Stockage interne : une `list` Python.
- `enfiler` : utilise `append`.
- `defiler` : utilise `pop(0)`.

### B.3 — Implémentation par liste chaînée

Créer un fichier `file_chainee.py` contenant la classe `FileChainee` :
- Stockage interne : maillons chaînés avec pointeurs `_tete` et `_queue`.
- `enfiler` : ajoute un maillon en queue.
- `defiler` : retire le maillon en tête.

**Indication** : la file chaînée nécessite deux pointeurs pour être efficace.

### B.4 — Tests communs de la file

Créer un fichier `tests_file.py` et écrire une fonction `tests_communs_file(classe_file)` qui teste :

1. Une file neuve est vide.
2. Après `enfiler("A")`, la file n'est plus vide.
3. L'ordre FIFO : `enfiler("A")`, `enfiler("B")`, `defiler()` renvoie `"A"`.
4. La file est vide après avoir défilé tous les éléments.
5. Cas limite : `defiler()` sur file vide lève `IndexError`.

Valider les deux implémentations avec cette même suite de tests.

---

## Partie C — Bilan (10 min)

Répondre par écrit dans un commentaire en haut de `tests_pile.py` :

1. Pourquoi est-il possible d'écrire une seule suite de tests pour deux implémentations différentes ?
2. Quel est l'intérêt de séparer interface et implémentation pour un projet en équipe ?
3. Si on vous demande d'ajouter une méthode `taille()` à la pile, faut-il modifier les tests existants ? Faut-il en ajouter ?


## Objectifs


## Prérequis


## Situation-problème

Deux équipes de développement utilisent la même interface de pile dans leur projet, mais l'une stocke les données dans un tableau et l'autre dans une liste chaînée. Les tests passent pour les deux. Pourquoi ?

## Activité d’entrée

Dessiner sur papier les opérations empiler(3), empiler(7), depiler(), empiler(1) sur une pile, puis réfléchir : le dessin changerait-il si la pile était implémentée différemment ?

## Exemple

Comparaison collective de deux implémentations de Pile (liste Python vs liste chaînée) sur les mêmes opérations.

## Exercices

Exercices d'identification d'interfaces et d'écriture d'implémentations alternatives.

## Corrigé

Les corrigés détaillés sont dans T01_corrige_interface_implementation_complement.md.

## Erreurs fréquentes

- EF1 : confondre l'interface (contrat public) et l'implémentation (détail interne).
- EF2 : oublier de tester les deux implémentations avec le même jeu de tests.
- EF3 : mélanger les méthodes spécifiques à une implémentation dans l'interface.


## Remédiation

Exercice de remédiation : identifier l'interface et l'implémentation dans un code de File donné, puis écrire une seconde implémentation.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

- Critère de réussite : les deux implémentations passent la même suite de tests.
- Critère de validation : l'interface est décrite indépendamment de l'implémentation.
- Observable : l'élève distingue méthode publique et détail interne.


## Séance(s) correspondante(s)

Séance dédiée.

## Tests attendus

Vérifier le résultat avec les jeux de tests fournis.

## Exemple d’exécution

Exécuter les tests communs sur les deux implémentations et vérifier qu'ils passent tous.

## Livrable vérifiable

Deux fichiers Python implémentant la même interface de pile, avec un fichier de tests commun.

## Consigne technique détaillée

Implémenter chaque méthode de l'interface en respectant exactement la signature donnée.


### Exemple d'exécution 1
Exécuter PileListe : empiler(3), empiler(7), depiler() → 7.

### Exemple d'exécution 2
Exécuter PileChainee : empiler(3), empiler(7), depiler() → 7 (même résultat, implémentation différente).


### Exercice 1 — Implémenter PileListe
Compléter la classe PileListe avec les méthodes empiler, depiler, est_vide.

### Exercice 2 — Implémenter PileChainee
Compléter la classe PileChainee avec les mêmes méthodes.

### Exercice 3 — Tests communs
Écrire une suite de tests validant les deux implémentations.


## Starter code

```python
# Compléter les fonctions ci-dessous
```

