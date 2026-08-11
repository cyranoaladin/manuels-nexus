---
title: "T01 - Cours - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "cours"
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

# T01 - Cours - Interface et implémentation complément

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

## Prérequis
- Connaître les notions d'interface et de structure de données.
- Savoir manipuler les listes Python (append, pop).
- Comprendre la notion de classe en Python (attributs, méthodes).

## Séance(s) correspondante(s)
- T01-S1 à T01-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une équipe de développement doit remplacer l'implémentation interne d’une pile (passage d’un tableau Python à une liste chaînée) sans modifier le code client qui l'utilise. Comment garantir que le remplacement fonctionne ?

## Activité d’entrée
1. Lister les opérations publiques d’une pile (push, pop, is_empty).
2. Proposer deux façons différentes de stocker les éléments en interne.
3. Vérifier que le code client ne change pas entre les deux versions.
4. Prévoir le comportement sur une pile vide pour chaque implémentation.

---

## Partie 1 — Distinguer interface et implémentation (T-STRUCT-01B)

### Définitions

- **Interface** (le QUOI) : ensemble des opérations publiques d’une structure de données, avec leurs signatures et leur contrat (préconditions, postconditions). L'interface ne dit rien sur la manière dont les données sont stockées.

- **Implémentation** (le COMMENT) : choix concret de représentation interne des données et code des opérations. Deux implémentations différentes peuvent respecter la même interface.

### Principe de séparation

| Aspect | Interface | Implémentation |
|--------|-----------|----------------|
| Question | QUOI faire ? | COMMENT le faire ? |
| Visibilité | Publique | Privée / interne |
| Stabilité | Stable (contrat) | Peut changer |
| Exemple pile | `push(x)`, `pop()`, `is_empty()` | Liste Python ou liste chaînée |

### Exemples contrastés obligatoires

### Exemple corrigé 1 - Pile avec liste Python

```python
class PileListe:
    """Implémentation d’une pile à l'aide d’une liste Python."""

    def __init__(self):
        self._elements = []

    def push(self, valeur):
        """Empile une valeur au sommet."""
        self._elements.append(valeur)

    def pop(self):
        """Dépile et renvoie le sommet. Lève IndexError si vide."""
        if self.is_empty():
            raise IndexError("pop sur une pile vide")
        return self._elements.pop()

    def is_empty(self):
        """Renvoie True si la pile est vide."""
        return len(self._elements) == 0
```

**Représentation interne** : un tableau dynamique Python (`list`). Le sommet est le dernier élément.

### Exemple corrigé 2 - Pile avec liste chaînée

```python
class Maillon:
    """Un maillon d’une liste chaînée."""

    def __init__(self, valeur, suivant=None):
        self.valeur = valeur
        self.suivant = suivant


class PileChainee:
    """Implémentation d’une pile à l'aide d’une liste chaînée."""

    def __init__(self):
        self._sommet = None

    def push(self, valeur):
        """Empile une valeur au sommet."""
        self._sommet = Maillon(valeur, self._sommet)

    def pop(self):
        """Dépile et renvoie le sommet. Lève IndexError si vide."""
        if self.is_empty():
            raise IndexError("pop sur une pile vide")
        valeur = self._sommet.valeur
        self._sommet = self._sommet.suivant
        return valeur

    def is_empty(self):
        """Renvoie True si la pile est vide."""
        return self._sommet is None
```

**Représentation interne** : des maillons chaînés. Le sommet est le premier maillon.

#### Contraste

| Critère | PileListe | PileChainee |
|---------|-----------|-------------|
| Stockage | `list` Python | Maillons chaînés |
| Accès sommet | `self._elements[-1]` | `self._sommet.valeur` |
| push | `append` O(1) amorti | Création maillon O(1) |
| pop | `list.pop()` O(1) amorti | Avance pointeur O(1) |
| Mémoire | Tableau contigu | Maillons dispersés |
| **Interface** | **Identique** : push, pop, is_empty | **Identique** : push, pop, is_empty |

Le code client ne voit aucune différence :

```python
# Ce code fonctionne avec PileListe OU PileChainee
p = PileListe()   # ou PileChainee()
p.push(10)
p.push(20)
print(p.pop())       # 20
print(p.is_empty())  # False
```

---

## Partie 1 bis — Deuxième exemple : la File (T-STRUCT-01B)

### Interface de la File (FIFO)

| Opération | Description |
|-----------|-------------|
| `enfiler(val)` | Ajoute un élément en queue |
| `defiler()` | Retire et renvoie l'élément en tete. Leve `IndexError` si vide |
| `est_vide()` | Renvoie `True` si la file est vide |

### Exemple corrigé 3 - File avec liste Python

```python
class FileListe:
    """Implementation d'une file a l'aide d'une liste Python."""

    def __init__(self):
        self._data = []

    def enfiler(self, val):
        """Ajoute un element en queue."""
        self._data.append(val)

    def defiler(self):
        """Retire et renvoie l'element en tete. Leve IndexError si vide."""
        if self.est_vide():
            raise IndexError("defiler sur une file vide")
        return self._data.pop(0)

    def est_vide(self):
        """Renvoie True si la file est vide."""
        return len(self._data) == 0
```

**Representation interne** : un tableau dynamique Python (`list`). La tete est l'element d'indice 0, la queue est le dernier element.

### Exemple corrigé 4 - File avec deux piles

```python
class FileDeuxPiles:
    """Implementation d'une file a l'aide de deux listes utilisees comme piles."""

    def __init__(self):
        self._entree = []
        self._sortie = []

    def enfiler(self, val):
        """Ajoute un element en queue."""
        self._entree.append(val)

    def defiler(self):
        """Retire et renvoie l'element en tete. Leve IndexError si vide."""
        if self.est_vide():
            raise IndexError("defiler sur une file vide")
        if len(self._sortie) == 0:
            while len(self._entree) > 0:
                self._sortie.append(self._entree.pop())
        return self._sortie.pop()

    def est_vide(self):
        """Renvoie True si la file est vide."""
        return len(self._entree) == 0 and len(self._sortie) == 0
```

**Representation interne** : deux listes jouant le role de piles. Les elements entrent dans `_entree` et sont transferes (inverses) vers `_sortie` quand on defile.

### Contraste File

| Critere | FileListe | FileDeuxPiles |
|---------|-----------|---------------|
| Stockage | Une seule `list` | Deux `list` |
| enfiler | `append` O(1) | `append` O(1) |
| defiler | `pop(0)` O(n) | Transfert amorti O(1) |
| Memoire | Un tableau | Deux tableaux |
| **Interface** | **Identique** : enfiler, defiler, est_vide | **Identique** : enfiler, defiler, est_vide |

```python
# Ce code fonctionne avec FileListe OU FileDeuxPiles
f = FileListe()   # ou FileDeuxPiles()
f.enfiler("A")
f.enfiler("B")
print(f.defiler())     # "A" (FIFO)
print(f.est_vide())    # False
```

---

## Partie 1 ter — Troisieme exemple : l'Ensemble (T-STRUCT-01B)

### Interface de l'Ensemble

| Operation | Description |
|-----------|-------------|
| `ajouter(element)` | Ajoute un element (sans doublon) |
| `contient(element)` | Renvoie `True` si l'element est present |
| `supprimer(element)` | Retire un element. Leve `ValueError` si absent |
| `est_vide()` | Renvoie `True` si l'ensemble est vide |

### Exemple corrigé 5 - Ensemble avec liste Python

```python
class EnsembleListe:
    """Implementation d'un ensemble a l'aide d'une liste Python (sans doublons)."""

    def __init__(self):
        self._elements = []

    def ajouter(self, element):
        """Ajoute un element s'il n'est pas deja present."""
        if element not in self._elements:
            self._elements.append(element)

    def contient(self, element):
        """Renvoie True si l'element est dans l'ensemble."""
        return element in self._elements

    def supprimer(self, element):
        """Retire un element. Leve ValueError si absent."""
        if element not in self._elements:
            raise ValueError(f"{element} absent de l'ensemble")
        self._elements.remove(element)

    def est_vide(self):
        """Renvoie True si l'ensemble est vide."""
        return len(self._elements) == 0
```

**Representation interne** : une liste Python sans doublons. La recherche se fait par parcours lineaire.

### Exemple corrigé 6 - Ensemble avec dictionnaire Python

```python
class EnsembleDict:
    """Implementation d'un ensemble a l'aide d'un dictionnaire Python."""

    def __init__(self):
        self._table = {}

    def ajouter(self, element):
        """Ajoute un element s'il n'est pas deja present."""
        self._table[element] = True

    def contient(self, element):
        """Renvoie True si l'element est dans l'ensemble."""
        return element in self._table

    def supprimer(self, element):
        """Retire un element. Leve ValueError si absent."""
        if element not in self._table:
            raise ValueError(f"{element} absent de l'ensemble")
        del self._table[element]

    def est_vide(self):
        """Renvoie True si l'ensemble est vide."""
        return len(self._table) == 0
```

**Representation interne** : un dictionnaire Python dont les cles sont les elements et les valeurs sont `True`. La recherche se fait par hachage.

### Contraste Ensemble

| Critere | EnsembleListe | EnsembleDict |
|---------|---------------|--------------|
| Stockage | `list` | `dict` |
| ajouter | Parcours O(n) + append | Hachage O(1) amorti |
| contient | Parcours O(n) | Hachage O(1) amorti |
| supprimer | Parcours O(n) + remove | Hachage O(1) amorti |
| Memoire | Tableau contigu | Table de hachage |
| **Interface** | **Identique** : ajouter, contient, supprimer | **Identique** : ajouter, contient, supprimer |

```python
# Ce code fonctionne avec EnsembleListe OU EnsembleDict
e = EnsembleListe()   # ou EnsembleDict()
e.ajouter(3)
e.ajouter(7)
e.ajouter(3)          # pas de doublon
print(e.contient(3))  # True
print(e.contient(5))  # False
e.supprimer(3)
print(e.contient(3))  # False
```

---

## Partie 2 — Écrire plusieurs implémentations, tests communs (T-STRUCT-01C)

### Principe : une suite de tests pour toutes les implémentations

La preuve qu'une interface est bien respectée : la même suite de tests passe sur chaque implémentation.

```python
def tests_communs_pile(classe_pile):
    """Suite de tests commune à toute implémentation de pile."""
    # Test 1 : une pile neuve est vide
    p = classe_pile()
    assert p.is_empty() == True

    # Test 2 : après push, la pile n'est plus vide
    p.push(42)
    assert p.is_empty() == False

    # Test 3 : pop renvoie le dernier élément empilé (LIFO)
    p.push(10)
    p.push(20)
    assert p.pop() == 20
    assert p.pop() == 10

    # Test 4 : pop vide toute la pile
    p2 = classe_pile()
    p2.push(1)
    p2.pop()
    assert p2.is_empty() == True

    # Test 5 : cas limite — pop sur pile vide lève une erreur
    p3 = classe_pile()
    try:
        p3.pop()
        assert False, "Aurait dû lever IndexError"
    except IndexError:
        pass

    print(f"Tous les tests passent pour {classe_pile.__name__}")


# Exécution sur les DEUX implémentations
tests_communs_pile(PileListe)
tests_communs_pile(PileChainee)
```

### Intérêt pédagogique

1. **Interchangeabilité** : le code client et les tests ne dépendent que de l'interface.
2. **Robustesse** : si on ajoute une troisième implémentation, on réutilise les mêmes tests.
3. **Séparation des responsabilités** : l'interface est un contrat, l'implémentation est un choix technique.

### Test du cas limite principal

Dépilement sur pile vide : les deux implémentations doivent lever `IndexError`. Empilements multiples suivis de dépilements : l'ordre LIFO doit être respecté dans les deux cas.

### Exemple corrigé 7 - Test d'interchangeabilité

On vérifie qu'un même code client fonctionne avec les deux implémentations sans modification, en remplaçant simplement le nom de la classe à l'instanciation.

---

## Synthèse

- **T-STRUCT-01B** : l'interface décrit le QUOI (opérations publiques), l'implémentation décrit le COMMENT (structure interne). Les deux sont indépendantes.
- **T-STRUCT-01C** : on peut écrire plusieurs implémentations d’une même interface. Une suite de tests commune valide la conformité de chaque implémentation au contrat.

## Vocabulaire essentiel
- Interface, implémentation, contrat, encapsulation.
- Pile (stack), LIFO, push, pop, is_empty.
- File (queue), FIFO, enfiler, defiler, est_vide.
- Ensemble (set), ajouter, contient, supprimer.
- Liste chaînée, maillon, tableau dynamique, table de hachage.


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

Distinction interface/implémentation justifiée par un exemple. Deux implémentations passant les mêmes tests.

Critère de validation : les deux implémentations passent les mêmes tests.
Observable : l'élève distingue interface publique et détail interne.

