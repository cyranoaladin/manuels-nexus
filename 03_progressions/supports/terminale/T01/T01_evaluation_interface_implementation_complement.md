---
title: "T01 - Évaluation - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "evaluation"
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

# T01 - Évaluation - Interface et implémentation complément

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

## Durée : 15 minutes — Documents non autorisés

---

### Question 1 — Distinguer interface et implémentation (5 points)

On donne la classe suivante :

```python
class Pile:
    def __init__(self):
        self._data = []

    def empiler(self, valeur):
        self._data.append(valeur)

    def depiler(self):
        if self.est_vide():
            raise IndexError("pile vide")
        return self._data.pop()

    def est_vide(self):
        return len(self._data) == 0
```

**a)** (2 pts) Identifier les éléments qui relèvent de l'**interface** et ceux qui relèvent de l'**implémentation**. Justifier chaque classement.

**b)** (1,5 pt) Un développeur écrit le code client suivant :

```python
p = Pile()
p.empiler(5)
print(p._data[0])   # affiche 5
```

Ce code fonctionne. Expliquer pourquoi il pose néanmoins un problème du point de vue de la séparation interface/implémentation.

**c)** (1,5 pt) Proposer une réécriture correcte de la dernière ligne qui ne dépend que de l'interface.

---

### Question 2 — Écrire une implémentation alternative (5 points)

On souhaite réécrire la classe `Pile` en utilisant une **liste chaînée** au lieu d’une liste Python.

On donne la classe `Maillon` :

```python
class Maillon:
    def __init__(self, valeur, suivant=None):
        self.valeur = valeur
        self.suivant = suivant
```

**a)** (3 pts) Écrire la classe `PileChainee` avec les méthodes `empiler`, `depiler` et `est_vide`, en utilisant des maillons chaînés. Le comportement doit être identique à celui de la classe `Pile` donnée en question 1.

**b)** (2 pts) Écrire un test (avec `assert`) qui vérifie le comportement LIFO sur les deux implémentations. Le test doit empiler les valeurs 1, 2 et 3, puis vérifier que les dépilements renvoient 3, 2 et 1 dans cet ordre.

---

### Question 3 — Tests communs et cas limite (5 points)

On dispose de deux classes `FileListe` et `FileChainee` qui implémentent la même interface de file : `enfiler(val)`, `defiler()`, `est_vide()`.

**a)** (2 pts) Écrire une fonction `test_fifo(classe_file)` qui vérifie l'ordre FIFO : enfiler "X" puis "Y", défiler doit renvoyer "X" d'abord.

**b)** (1,5 pt) Ajouter à cette fonction un test du cas limite : appeler `defiler()` sur une file vide doit lever `IndexError`.

**c)** (1,5 pt) Expliquer en deux phrases pourquoi la même fonction `test_fifo` peut valider les deux implémentations sans modification.

---

### Question 4 -- Choisir et justifier une implementation (5 points)

On dispose de deux implementations d'un ensemble (sans doublons) :

- `EnsembleListe` : stocke les elements dans une liste Python. L'operation `contient(element)` parcourt la liste (complexite O(n)).
- `EnsembleDict` : stocke les elements comme cles d'un dictionnaire Python. L'operation `contient(element)` utilise le hachage (complexite O(1) amortie).

Les deux classes ont la meme interface : `ajouter(element)`, `contient(element)`, `supprimer(element)`, `est_vide()`.

**a)** (2 pts) On doit gerer un repertoire de 50 000 adresses email et verifier frequemment si une adresse donnee est deja enregistree. Quelle implementation choisir ? Justifier en comparant les complexites.

**b)** (1,5 pt) Ecrire une suite de tests (avec `assert`) qui valide le comportement des deux implementations de maniere identique. La suite doit contenir au moins :
- un test d'ajout et de presence,
- un test de suppression,
- un test de cas limite (supprimer un element absent).

**c)** (1,5 pt) Un collegue propose de modifier le code client pour utiliser directement `element in obj._table` au lieu de `obj.contient(element)`. Expliquer pourquoi cette modification est une mauvaise pratique et quel probleme elle pose si on change d'implementation.

---

*Bareme total : 20 points*


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

Distinction interface/implémentation justifiée par un exemple. Deux implémentations passant les mêmes tests.

## Séance(s) correspondante(s)

Séance dédiée.

## Barème

| Question | Points |
|---|---|
| Question 1 | 5 |
| Question 2 | 5 |
| Question 3 | 5 |
| Question 4 | 5 |
| **Total** | **20** |

Critère de validation : chaque question est répondue avec justification.
Observable : l'élève distingue correctement interface et implémentation.

