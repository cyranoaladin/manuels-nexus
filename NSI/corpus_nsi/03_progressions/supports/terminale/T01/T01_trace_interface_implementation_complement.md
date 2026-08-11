---
title: "T01 - Trace - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "trace"
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

# T01 - Trace écrite - Interface et implémentation complément

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

---

## 1. Interface vs Implémentation — Tableau de synthèse

| | Interface (le QUOI) | Implémentation (le COMMENT) |
|---|---|---|
| Définition | Ensemble des opérations publiques et leur contrat | Code concret et structure interne des données |
| Visibilité | Publique, connue du code client | Privée, cachée au code client |
| Exemple (pile) | `push(x)`, `pop()`, `is_empty()` | Liste Python ou liste chaînée |
| Stabilité | Ne change pas (contrat fixe) | Peut être remplacée sans casser le code client |
| Analogie | Le menu du restaurant | La recette en cuisine |

**Règle fondamentale** : le code client ne dépend que de l'interface, jamais de l'implémentation.

---

## 2. Deux implémentations d’une pile — Code de référence

### Implémentation 1 : pile par liste Python

```python
class PileListe:
    def __init__(self):
        self._elements = []       # stockage interne : list

    def push(self, valeur):
        self._elements.append(valeur)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop sur pile vide")
        return self._elements.pop()

    def is_empty(self):
        return len(self._elements) == 0
```

### Implémentation 2 : pile par liste chaînée

```python
class Maillon:
    def __init__(self, valeur, suivant=None):
        self.valeur = valeur
        self.suivant = suivant

class PileChainee:
    def __init__(self):
        self._sommet = None       # stockage interne : maillons

    def push(self, valeur):
        self._sommet = Maillon(valeur, self._sommet)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop sur pile vide")
        valeur = self._sommet.valeur
        self._sommet = self._sommet.suivant
        return valeur

    def is_empty(self):
        return self._sommet is None
```

---

## 3. Tableau comparatif des deux implémentations

| Critère | PileListe | PileChainee |
|---------|-----------|-------------|
| Structure interne | `list` Python | Maillons chaînés |
| push | `append()` — O(1) amorti | Nouveau maillon — O(1) |
| pop | `list.pop()` — O(1) amorti | Avance du pointeur — O(1) |
| is_empty | `len() == 0` | `sommet is None` |
| Mémoire | Bloc contigu | Maillons dispersés |
| **Interface publique** | **Identique** | **Identique** |

---

## 4. Tests communs — Patron de validation

```python
def tests_communs_pile(classe_pile):
    p = classe_pile()
    assert p.is_empty() == True       # pile neuve vide

    p.push(42)
    assert p.is_empty() == False      # plus vide après push

    p.push(10)
    p.push(20)
    assert p.pop() == 20              # LIFO : dernier entré, premier sorti
    assert p.pop() == 10

    p2 = classe_pile()
    p2.push(1)
    p2.pop()
    assert p2.is_empty() == True      # vide après push + pop

    # Cas limite : pop sur pile vide
    try:
        classe_pile().pop()
        assert False
    except IndexError:
        pass

# Validation des DEUX implémentations
tests_communs_pile(PileListe)
tests_communs_pile(PileChainee)
```

---

## 5. Points clés à retenir

1. **Interface = contrat** : elle garantit quelles opérations existent et ce qu'elles font.
2. **Implémentation = choix technique** : elle peut changer sans affecter le code client.
3. **Exemples contrastés** : deux implémentations différentes de la même pile prouvent la séparation.
4. **Tests communs** : une même suite de tests valide toute implémentation conforme à l'interface.
5. **Cas limite** : toute implémentation doit gérer le cas de la structure vide (pile vide, file vide).


## Objectifs


## Prérequis


## Situation-problème

Deux équipes de développement utilisent la même interface de pile dans leur projet, mais l'une stocke les données dans un tableau et l'autre dans une liste chaînée. Les tests passent pour les deux. Pourquoi ?

## Activité d’entrée

Dessiner sur papier les opérations empiler(3), empiler(7), depiler(), empiler(1) sur une pile, puis réfléchir : le dessin changerait-il si la pile était implémentée différemment ?

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
