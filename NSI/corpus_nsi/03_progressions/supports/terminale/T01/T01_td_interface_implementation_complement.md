---
title: "T01 - TD - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "td"
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

# T01 - TD - Interface et implémentation complément

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

---

### Exercice 1 — Identifier interface et implémentation (O1)

Objectif travaillé : O1

On donne le code suivant :

```python
class Compteur:
    def __init__(self):
        self._n = 0

    def incrementer(self):
        self._n += 1

    def valeur(self):
        return self._n

    def reinitialiser(self):
        self._n = 0
```

**Questions :**

1. Lister les opérations qui forment l'**interface** de `Compteur`.
2. Quel est le détail d'**implémentation** dans cette classe ?
3. Proposer une implémentation alternative qui stocke la valeur dans une liste de longueur variable (la valeur du compteur est `len(self._liste)`). Écrire le code complet.
4. Expliquer pourquoi le code client suivant fonctionne sans modification avec les deux implémentations :

```python
c = Compteur()  # ou CompteurListe()
c.incrementer()
c.incrementer()
print(c.valeur())     # 2
c.reinitialiser()
print(c.valeur())     # 0
```

---

### Exercice 2 — Analyse d’un code existant (O1, O2)

Objectif travaillé : O2

On donne deux classes implémentant une file :

**Classe A :**
```python
class FileA:
    def __init__(self):
        self._data = []

    def enfiler(self, val):
        self._data.append(val)

    def defiler(self):
        if self.est_vide():
            raise IndexError("file vide")
        return self._data.pop(0)

    def est_vide(self):
        return len(self._data) == 0
```

**Classe B :**
```python
class FileB:
    def __init__(self):
        self._entree = []
        self._sortie = []

    def enfiler(self, val):
        self._entree.append(val)

    def defiler(self):
        if self.est_vide():
            raise IndexError("file vide")
        if len(self._sortie) == 0:
            while len(self._entree) > 0:
                self._sortie.append(self._entree.pop())
        return self._sortie.pop()

    def est_vide(self):
        return len(self._entree) == 0 and len(self._sortie) == 0
```

**Questions :**

1. Quelle est l'interface commune aux deux classes ?
2. Décrire la représentation interne de chaque classe (implémentation).
3. Simuler sur papier les appels suivants pour chaque classe et vérifier qu'on obtient le même résultat :
   ```
   f = FileA()  # puis FileB()
   f.enfiler("A")
   f.enfiler("B")
   f.enfiler("C")
   print(f.defiler())   # ?
   print(f.defiler())   # ?
   ```
4. Quel est l'avantage de `FileB` par rapport à `FileA` en termes de complexité de `defiler` ?

---

### Exercice 3 — Concevoir une interface (O2, O3)

Question préliminaire : quelles sont les opérations minimales qu'un Sac doit offrir pour être utilisable ?

Objectif travaillé : O3

On souhaite créer une structure de données **Sac** (bag/multiset) qui stocke des éléments avec répétition.

**Questions :**

1. Proposer l'interface du Sac : lister les opérations nécessaires avec leur signature et leur description. On attend au minimum :
   - Ajouter un élément
   - Compter le nombre d'occurrences d’un élément
   - Retirer une occurrence d’un élément
   - Savoir si le sac est vide

2. Pour chaque opération, préciser le cas limite à traiter.

3. Proposer deux stratégies d'implémentation différentes (sans coder) :
   - Une utilisant une liste Python.
   - Une utilisant un dictionnaire Python.

4. Écrire une suite de tests (au format `assert`) qui validerait toute implémentation conforme à l'interface, en incluant au moins un test de cas limite.

---

### Exercice 4 — Relier interface et tests communs (O3, O4)

Question préliminaire : pourquoi une suite de tests ne doit-elle pas faire référence aux attributs internes ?

Objectif travaillé : O4

On dispose de la suite de tests suivante :

```python
def tests_communs(classe):
    s = classe()
    assert s.est_vide() == True

    s.ajouter(5)
    s.ajouter(3)
    s.ajouter(5)
    assert s.est_vide() == False
    assert s.compter(5) == 2
    assert s.compter(3) == 1
    assert s.compter(99) == 0

    s.retirer(5)
    assert s.compter(5) == 1

    # Cas limite : retirer un élément absent
    try:
        s.retirer(99)
        assert False, "Aurait dû lever ValueError"
    except ValueError:
        pass
```

**Questions :**

1. Déduire l'interface de la structure de données testée à partir de ces tests.
2. Cette suite de tests contient-elle un test de cas limite ? Lequel ?
3. Ajouter un test supplémentaire qui vérifie que le sac est vide après avoir retiré tous les éléments.
4. Expliquer pourquoi cette suite de tests est indépendante de l'implémentation.


---

### Exercice 5 -- Comparer les complexites de deux implementations (O2)

Question préliminaire : rappeler la différence entre complexité au pire cas et complexité amortie.

Objectif travaillé : O2

On dispose de deux implementations d’un ensemble : `EnsembleListe` (stockage dans une liste Python) et `EnsembleDict` (stockage dans un dictionnaire Python).

**Questions :**

1. Pour chaque implementation, donner la complexite temporelle dans le pire cas de chaque operation : `ajouter(element)`, `contient(element)`, `supprimer(element)`, ou n est le nombre d’elements dans l’ensemble.
2. Presenter les resultats dans un tableau comparatif.
3. Si on doit gerer un ensemble de 10 000 elements avec de nombreuses recherches, quelle implementation choisir ? Justifier.
4. Donner un scenario ou `EnsembleListe` pourrait etre preferable malgre sa complexite plus elevee.

---

### Exercice 6 -- Choisir une implementation selon le contexte (O3)

Question préliminaire : quels critères utiliser pour choisir entre deux implémentations d'une même interface ?

Objectif travaillé : O3

Un developpeur doit implementer une file d’attente pour trois cas d’usage differents :

- **Cas A** : une imprimante qui traite les documents dans l’ordre d’arrivee (quelques dizaines de documents par jour).
- **Cas B** : un serveur web qui traite des milliers de requetes par seconde.
- **Cas C** : un systeme embarque avec tres peu de memoire disponible.

On dispose de deux implementations : `FileListe` (une seule liste, `defiler` en O(n)) et `FileDeuxPiles` (deux listes, `defiler` amorti en O(1)).

**Questions :**

1. Pour chaque cas (A, B, C), indiquer quelle implementation est la plus adaptee. Justifier.
2. Expliquer pourquoi le code client (qui appelle `enfiler`, `defiler`, `est_vide`) n’a pas besoin d’etre modifie quand on change d’implementation.
3. Proposer un critere general pour choisir entre deux implementations d’une meme interface.

---

### Exercice 7 -- Detecter et corriger un bug d’implementation (O4)

Question préliminaire : comment identifier un bug d’implémentation quand l’interface semble correcte ?

Objectif travaillé : O4

Le code suivant est cense implementer une pile, mais il contient des bugs :

```python
class PileBuggee:
    def __init__(self):
        self._elements = []

    def push(self, valeur):
        self._elements.insert(0, valeur)

    def pop(self):
        return self._elements.pop()

    def is_empty(self):
        return self._elements == None
```

**Questions :**

1. Executer mentalement le code suivant et donner le resultat obtenu :
   ```python
   p = PileBuggee()
   p.push(1)
   p.push(2)
   p.push(3)
   print(p.pop())
   ```
   Le resultat est-il correct pour une pile (LIFO) ? Expliquer.

2. Identifier le bug dans la methode `is_empty`. Quel est le test correct ?

3. Identifier le bug dans la combinaison `push`/`pop`. Expliquer l’incoherence entre `insert(0, ...)` et `pop()`.

4. Reecrire la classe corrigee. Verifier avec le test suivant :
   ```python
   p = PileBuggee()  # version corrigee
   p.push(10)
   p.push(20)
   assert p.pop() == 20
   assert p.pop() == 10
   assert p.is_empty() == True
   ```

---

### Exercice 8 -- Refactoriser du code pour separer interface et implementation (O2, O4)

Question préliminaire : pourquoi est-il risqué d'accéder directement aux attributs internes d'un objet ?

Objectif travaillé : O1

Le code suivant melange interface et implementation dans le code client :

```python
class GestionNotes:
    def __init__(self):
        self.notes = []

    def ajouter_note(self, note):
        self.notes.append(note)

    def moyenne(self):
        return sum(self.notes) / len(self.notes)


# Code client
g = GestionNotes()
g.ajouter_note(15)
g.ajouter_note(12)
g.ajouter_note(18)

# Acces direct a l’implementation
print(g.notes[0])          # acces direct a la liste interne
g.notes.sort()             # tri direct de la liste interne
print(g.notes[-1])         # acces direct au dernier element
print(len(g.notes))        # acces direct a la taille interne
```

**Questions :**

1. Identifier toutes les lignes du code client qui violent la separation interface/implementation.
2. Pour chaque violation, proposer une methode d’interface qui remplacerait l’acces direct. Donner la signature et la description de chaque methode.
3. Reecrire la classe `GestionNotes` avec les nouvelles methodes d’interface et l’attribut `_notes` (prefixe underscore pour signaler qu’il est prive).
4. Reecrire le code client pour qu’il n’utilise que l’interface publique.
5. Expliquer pourquoi cette refactorisation permet de changer la representation interne (par exemple remplacer la liste par un dictionnaire `{indice: note}`) sans modifier le code client.


## Erreurs fréquentes

- EF1 : confondre l'interface (contrat public) et l'implémentation (détail interne).
- EF2 : oublier de tester les deux implémentations avec le même jeu de tests.
- EF3 : mélanger les méthodes spécifiques à une implémentation dans l'interface.


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


## Remédiation

Exercice de remédiation : identifier l'interface et l'implémentation dans un code de File donné, puis écrire une seconde implémentation.


## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d’approfondissement.


## Critères de réussite

- Critère de réussite : les deux implémentations passent la même suite de tests.
- Critère de validation : l'interface est décrite indépendamment de l'implémentation.
- Observable : l'élève distingue méthode publique et détail interne.


## Séance(s) correspondante(s)

Séance dédiée.


## Exercices numérotés

Voir les exercices 1 à 8 ci-dessus.

