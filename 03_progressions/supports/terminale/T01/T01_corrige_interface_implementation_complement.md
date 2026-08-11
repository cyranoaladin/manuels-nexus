---
title: "T01 - Corrigé - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "corrige"
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

# T01 - Corrigé - Interface et implémentation complément

## Capacités officielles atomiques
- T-STRUCT-01B : Distinguer interface et implémentation.
- T-STRUCT-01C : Écrire plusieurs implémentations d’une même structure de données.

---

## Corrigé de l'évaluation

### Question 1 — Distinguer interface et implémentation (5 points)

Exercice fondamental sur la séparation interface/implémentation.

**a)** (2 pts)

Éléments relevant de l'**interface** :
- `empiler(valeur)` : opération publique, contrat = ajoute un élément au sommet.
- `depiler()` : opération publique, contrat = retire et renvoie le sommet, lève `IndexError` si vide.
- `est_vide()` : opération publique, contrat = renvoie `True` si la pile ne contient aucun élément.

Éléments relevant de l'**implémentation** :
- `self._data = []` : choix de stockage interne par liste Python.
- `self._data.append(valeur)` : mécanisme concret d'ajout.
- `self._data.pop()` : mécanisme concret de retrait.
- `len(self._data) == 0` : test de vacuité lié à la structure choisie.

**Justification** : l'interface est ce que le code client peut appeler (méthodes publiques et leur contrat). L'implémentation est la manière dont ces opérations sont réalisées en interne, à l'aide d’une structure de données concrète.

**b)** (1,5 pt)

Le code `p._data[0]` accède directement à l'attribut privé `_data`, qui est un détail d'implémentation. Ce code :
- Viole le principe de séparation interface/implémentation.
- Cessera de fonctionner si on remplace l'implémentation par une liste chaînée (car `_data` n'existera plus).
- Rend le code client fragile et dépendant du choix de stockage interne.

**c)** (1,5 pt)

Pour accéder au dernier élément empilé sans dépendre de l'implémentation, on utilise uniquement les opérations de l'interface :

```python
p = Pile()
p.empiler(5)
valeur = p.depiler()  # utilise l'interface
print(valeur)         # affiche 5
```

Si on veut consulter sans retirer, il faudrait ajouter une méthode `sommet()` à l'interface.

---

### Question 2 — Écrire une implémentation alternative (5 points)

Exercice de programmation sur l'implémentation par liste chaînée.

**a)** (3 pts)

```python
class PileChainee:
    def __init__(self):
        self._sommet = None

    def empiler(self, valeur):
        self._sommet = Maillon(valeur, self._sommet)

    def depiler(self):
        if self.est_vide():
            raise IndexError("pile vide")
        valeur = self._sommet.valeur
        self._sommet = self._sommet.suivant
        return valeur

    def est_vide(self):
        return self._sommet is None
```

**Explication** :
- `empiler` crée un nouveau maillon dont le `suivant` pointe vers l'ancien sommet.
- `depiler` sauvegarde la valeur du sommet, puis avance le pointeur au maillon suivant.
- `est_vide` vérifie si le sommet est `None` (aucun maillon).

**b)** (2 pts)

```python
def test_lifo(classe_pile):
    p = classe_pile()
    p.empiler(1)
    p.empiler(2)
    p.empiler(3)
    assert p.depiler() == 3, "LIFO : 3 attendu"
    assert p.depiler() == 2, "LIFO : 2 attendu"
    assert p.depiler() == 1, "LIFO : 1 attendu"
    assert p.est_vide() == True

# Validation sur les deux implémentations
test_lifo(Pile)
test_lifo(PileChainee)
```

---

### Question 3 — Tests communs et cas limite (5 points)

Exercice sur les tests indépendants de l'implémentation.

**a)** (2 pts)

```python
def test_fifo(classe_file):
    f = classe_file()
    f.enfiler("X")
    f.enfiler("Y")
    assert f.defiler() == "X", "FIFO : X attendu en premier"
    assert f.defiler() == "Y", "FIFO : Y attendu en second"
    assert f.est_vide() == True
```

**b)** (1,5 pt)

Ajout du test de cas limite :

```python
def test_fifo(classe_file):
    # Test FIFO
    f = classe_file()
    f.enfiler("X")
    f.enfiler("Y")
    assert f.defiler() == "X", "FIFO : X attendu en premier"
    assert f.defiler() == "Y", "FIFO : Y attendu en second"
    assert f.est_vide() == True

    # Cas limite : defiler sur file vide
    f2 = classe_file()
    try:
        f2.defiler()
        assert False, "Aurait dû lever IndexError"
    except IndexError:
        pass  # comportement attendu

# Validation
test_fifo(FileListe)
test_fifo(FileChainee)
```

**c)** (1,5 pt)

La même fonction `test_fifo` peut valider les deux implémentations car elle n'utilise que les opérations de l'interface (`enfiler`, `defiler`, `est_vide`). Elle ne fait aucune hypothèse sur la représentation interne des données. Toute classe respectant le contrat de l'interface (ordre FIFO, erreur sur file vide) passera ces tests, quelle que soit la manière dont elle stocke les éléments en interne.

---

### Question 4 -- Choisir et justifier une implementation (5 points)

Exercice de raisonnement sur le choix d'implémentation selon les contraintes.

**a)** (2 pts)

Il faut choisir `EnsembleDict`. Avec 50 000 adresses email et des verifications frequentes, l'operation `contient` est critique. Avec `EnsembleListe`, chaque verification parcourt jusqu'a 50 000 elements (O(n)), soit en moyenne 25 000 comparaisons. Avec `EnsembleDict`, chaque verification se fait par hachage en O(1) amorti, soit un acces quasi-direct. La difference de performance est considerable a cette echelle.

**b)** (1,5 pt)

```python
def tests_ensemble(classe_ensemble):
    # Test ajout et presence
    e = classe_ensemble()
    e.ajouter("alice@mail.fr")
    e.ajouter("bob@mail.fr")
    assert e.contient("alice@mail.fr") == True
    assert e.contient("bob@mail.fr") == True
    assert e.contient("charlie@mail.fr") == False

    # Test pas de doublons
    e.ajouter("alice@mail.fr")
    assert e.contient("alice@mail.fr") == True

    # Test suppression
    e.supprimer("alice@mail.fr")
    assert e.contient("alice@mail.fr") == False
    assert e.contient("bob@mail.fr") == True

    # Cas limite : supprimer un element absent
    try:
        e.supprimer("inconnu@mail.fr")
        assert False, "Aurait du lever ValueError"
    except ValueError:
        pass

# Validation sur les deux implementations
tests_ensemble(EnsembleListe)
tests_ensemble(EnsembleDict)
```

**c)** (1,5 pt)

Ecrire `element in obj._table` au lieu de `obj.contient(element)` est une mauvaise pratique car :
- `_table` est un attribut interne (prefixe underscore) qui fait partie de l'implementation de `EnsembleDict`. Le code client ne doit pas y acceder directement.
- Si on remplace `EnsembleDict` par `EnsembleListe`, l'attribut `_table` n'existe plus (il s'appelle `_elements`). Le code client qui utilise `_table` directement cessera de fonctionner.
- En utilisant uniquement `obj.contient(element)` (l'interface), le code client reste independant de l'implementation choisie et fonctionne avec les deux classes sans modification.

---

## Corrigé du TD

### Exercice 1 (corrigé)

**Méthode** : On distingue les méthodes publiques (interface) des attributs internes (implémentation) en vérifiant ce que le code client peut appeler sans connaître la structure interne.

**1.** Interface de `Compteur` : `incrementer()`, `valeur()`, `reinitialiser()`.

**2.** Détail d'implémentation : l'attribut `self._n` (un entier) qui stocke la valeur du compteur.

**3.** Implémentation alternative :

```python
class CompteurListe:
    def __init__(self):
        self._liste = []

    def incrementer(self):
        self._liste.append(None)

    def valeur(self):
        return len(self._liste)

    def reinitialiser(self):
        self._liste = []
```

**4.** Le code client fonctionne avec les deux implémentations car il n'utilise que les méthodes de l'interface (`incrementer`, `valeur`, `reinitialiser`). Il ne dépend ni de `_n` ni de `_liste`.

**Résultat** : L'interface est composée de `incrementer()`, `valeur()`, `reinitialiser()`. L'implémentation alternative utilise une liste de longueur variable au lieu d'un entier.

### Corrigé exercice 1

**Méthode** : on identifie l'interface (méthodes publiques) et l'implémentation (structure interne) dans le code donné.
L'interface de la pile est `{empiler, depiler, est_vide}`. L'implémentation utilise une liste Python `self._donnees`. Le résultat vaut `True` pour `est_vide()` sur une pile fraîchement créée, et `depiler()` renvoie `7` après `empiler(7)`.



### Corrigé exercice 2

**Méthode** : On identifie l'interface commune en listant les méthodes publiques partagées, puis on compare les représentations internes en simulant les appels pas à pas.
L'interface commune donne `{enfiler, defiler, est_vide}`. Après `enfiler(3)` puis `enfiler(7)`, `defiler()` renvoie `3` (FIFO). Les deux implémentations produisent le même résultat.

**1.** Interface commune : `enfiler(val)`, `defiler()`, `est_vide()`.

**2.** Représentation interne :
- `FileA` : une seule liste `_data`. Les éléments entrent en fin (`append`) et sortent en début (`pop(0)`).
- `FileB` : deux listes `_entree` et `_sortie`. Les éléments entrent dans `_entree` et sont transférés vers `_sortie` (inversés) quand on défile.

**3.** Simulation :

Pour `FileA` :
| Opération | `_data` | Résultat |
|-----------|---------|----------|
| `enfiler("A")` | `["A"]` | |
| `enfiler("B")` | `["A", "B"]` | |
| `enfiler("C")` | `["A", "B", "C"]` | |
| `defiler()` | `["B", "C"]` | `"A"` |
| `defiler()` | `["C"]` | `"B"` |

Pour `FileB` :
| Opération | `_entree` | `_sortie` | Résultat |
|-----------|-----------|-----------|----------|
| `enfiler("A")` | `["A"]` | `[]` | |
| `enfiler("B")` | `["A", "B"]` | `[]` | |
| `enfiler("C")` | `["A", "B", "C"]` | `[]` | |
| `defiler()` | `[]` | `["C", "B"]` (transfert) | `"A"` |
| `defiler()` | `[]` | `["C"]` | `"B"` |

Résultats identiques : `"A"` puis `"B"`.

**4.** `FileA.defiler()` a une complexité O(n) car `pop(0)` décale tous les éléments. `FileB.defiler()` a une complexité amortie O(1) car le transfert ne se fait que quand `_sortie` est vide.

**Résultat** : Les deux implémentations produisent les mêmes résultats (`"A"` puis `"B"`) car elles respectent la même interface FIFO, mais `FileB` est plus performante pour `defiler`.



### Corrigé exercice 3

**Méthode** : On définit l'interface en listant les opérations nécessaires avec leurs signatures et cas limites, puis on propose deux stratégies d'implémentation distinctes (liste et dictionnaire).

**1.** Interface du Sac :
- `ajouter(element)` : ajoute un élément dans le sac.
- `compter(element)` : renvoie le nombre d'occurrences de l'élément.
- `retirer(element)` : retire une occurrence. Lève `ValueError` si absent.
- `est_vide()` : renvoie `True` si le sac est vide.

**2.** Cas limites :
- `retirer` un élément absent : lever `ValueError`.
- `compter` un élément absent : renvoyer 0 (pas d'erreur).
- `est_vide` sur sac neuf : renvoyer `True`.

**3.** Deux stratégies :
- **Liste** : `self._elements = []`. `ajouter` fait `append`. `compter` fait `count`. `retirer` fait `remove`.
- **Dictionnaire** : `self._compteurs = {}`. Clé = élément, valeur = nombre d'occurrences.

**4.** Suite de tests :

```python
def tests_sac(classe_sac):
    s = classe_sac()
    assert s.est_vide() == True

    s.ajouter(5)
    s.ajouter(3)
    s.ajouter(5)
    assert s.compter(5) == 2
    assert s.compter(3) == 1
    assert s.compter(99) == 0
    assert s.est_vide() == False

    s.retirer(5)
    assert s.compter(5) == 1

    s.retirer(5)
    s.retirer(3)
    assert s.est_vide() == True

    # Cas limite : retirer un élément absent
    try:
        classe_sac().retirer(42)
        assert False
    except ValueError:
        pass
```

**Résultat** : L'interface du Sac comprend `ajouter`, `compter`, `retirer`, `est_vide`. Les deux stratégies (liste et dictionnaire) respectent cette interface avec des performances différentes.

### Corrigé exercice 4

**Méthode** : On déduit l'interface en analysant les appels de méthodes présents dans la suite de tests, puis on vérifie la couverture des cas limites.

**1.** Interface déduite : `ajouter(element)`, `compter(element)`, `retirer(element)`, `est_vide()`. C'est un Sac (multiset).

**2.** Oui, le test du cas limite est : `s.retirer(99)` doit lever `ValueError` (retirer un élément absent).

**3.** Test supplémentaire :

```python
s2 = classe()
s2.ajouter(7)
s2.ajouter(7)
s2.retirer(7)
s2.retirer(7)
assert s2.est_vide() == True, "Le sac devrait être vide"
```

**4.** La suite de tests est indépendante de l'implémentation car elle n'utilise que les méthodes de l'interface publique (`ajouter`, `compter`, `retirer`, `est_vide`). Elle ne fait aucune référence à des attributs internes ni à la manière dont les données sont stockées.

**Résultat** : L'interface déduite est celle d'un Sac (multiset). Le test de cas limite vérifie que `retirer(99)` lève `ValueError`. La suite est indépendante de l'implémentation.

---



### Corrigé exercice 5

**Méthode** : On analyse la complexité temporelle de chaque opération dans le pire cas pour les deux implémentations, en distinguant parcours linéaire (liste) et accès par hachage (dictionnaire).
`empiler` vaut `O(1)` pour les deux implémentations. `depiler` vaut `O(1)` pour la liste (via `pop()`) et `O(1)` pour la liste chaînée. La complexité spatiale donne `O(n)` dans les deux cas.

**1.** Complexites dans le pire cas :

| Operation | EnsembleListe | EnsembleDict |
|-----------|---------------|--------------|
| `ajouter(element)` | O(n) (parcours pour verifier l’absence) | O(1) amorti (hachage) |
| `contient(element)` | O(n) (parcours lineaire) | O(1) amorti (hachage) |
| `supprimer(element)` | O(n) (parcours + decalage) | O(1) amorti (hachage) |

**2.** Tableau ci-dessus.

**3.** Avec 10 000 elements et de nombreuses recherches, il faut choisir `EnsembleDict`. Chaque recherche (`contient`) est en O(1) amorti avec le dictionnaire, contre O(n) avec la liste. Pour 10 000 elements, la difference est significative : une recherche dans la liste parcourt en moyenne 5 000 elements, contre un acces quasi-direct par hachage.

**4.** `EnsembleListe` peut etre preferable quand :
- Le nombre d’elements est tres petit (moins de 10), car le surcoût du hachage n’est pas justifie.
- On a besoin de conserver l’ordre d’insertion des elements (bien que `dict` preserve l’ordre depuis Python 3.7, ce n’est pas garanti par la specification de l’interface Ensemble).
- Les elements ne sont pas hachables (par exemple des listes Python), ce qui interdit l’utilisation d’un dictionnaire comme conteneur de cles.

**Résultat** : `EnsembleDict` est preferable pour 10 000 elements avec de nombreuses recherches (O(1) vs O(n)). `EnsembleListe` peut convenir pour de tres petits ensembles ou des elements non hachables.



### Corrigé exercice 6

**Méthode** : On évalue les contraintes de chaque cas d'usage (volume, performance, mémoire) et on choisit l'implémentation dont les complexités sont les mieux adaptées.

**1.**
- **Cas A** (imprimante, quelques dizaines de documents) : `FileListe` suffit. Le nombre d’elements est faible, donc la complexite O(n) de `defiler` est negligeable. La simplicite du code est un avantage.
- **Cas B** (serveur web, milliers de requetes/seconde) : `FileDeuxPiles` est indispensable. La complexite amortie O(1) de `defiler` est necessaire pour tenir la charge. Avec `FileListe`, chaque `defiler` decalerait potentiellement des milliers d’elements.
- **Cas C** (systeme embarque, peu de memoire) : `FileListe` est preferable. Elle utilise une seule liste, donc moins de memoire que `FileDeuxPiles` qui en utilise deux (au moment du transfert, les deux listes peuvent coexister).

**2.** Le code client n’utilise que les operations de l’interface (`enfiler`, `defiler`, `est_vide`). Il ne fait aucune reference aux attributs internes (`_data`, `_entree`, `_sortie`). On peut donc remplacer une implementation par l’autre en changeant uniquement la ligne de creation de l’objet.

**3.** Critere general : choisir l’implementation dont les complexites temporelle et spatiale sont les mieux adaptees au volume de donnees et au profil d’utilisation (frequence de chaque operation, contraintes memoire).

**Résultat** : Cas A -> `FileListe` (simplicite suffisante), Cas B -> `FileDeuxPiles` (performance critique), Cas C -> `FileListe` (memoire limitee). Le code client reste inchange grace a l’interface commune.

### Corrigé exercice 7

**Méthode** : On exécute mentalement le code en suivant l'état de la liste interne à chaque opération, puis on identifie l'incohérence entre `insert(0, ...)` et `pop()` qui opèrent sur des côtés opposés de la liste.

**1.** Execution de `PileBuggee` :
- `push(1)` : `insert(0, 1)` place la valeur en tete, ce qui donne `_elements = [1]`
- `push(2)` : `insert(0, 2)` insère avant le premier element, ce qui donne `_elements = [2, 1]`
- `push(3)` : `insert(0, 3)` ajoute encore en debut de liste, ce qui donne `_elements = [3, 2, 1]`
- `pop()` : `_elements.pop()` retire le **dernier** element, soit `1`.

Le resultat est `1`, mais pour une pile LIFO, on attend `3` (le dernier empile). Le comportement est incorrect : `push` insere au debut et `pop` retire a la fin, ce qui donne un comportement FIFO au lieu de LIFO.

**2.** Bug dans `is_empty` : le test `self._elements == None` est toujours `False` car `self._elements` est une liste (jamais `None`). Le test correct est :

```python
def is_empty(self):
    return len(self._elements) == 0
```

**3.** L’incoherence vient du fait que `push` utilise `insert(0, ...)` qui place l’element en debut de liste, tandis que `pop()` retire l’element en fin de liste. Pour un comportement LIFO coherent, il faut que `push` et `pop` operent du meme cote : soit les deux en fin de liste (`append` + `pop()`), soit les deux en debut (`insert(0, ...)` + `pop(0)`).

**4.** Classe corrigee :

```python
class PileCorrigee:
    def __init__(self):
        self._elements = []

    def push(self, valeur):
        self._elements.append(valeur)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop sur une pile vide")
        return self._elements.pop()

    def is_empty(self):
        return len(self._elements) == 0
```

Verification :

```python
p = PileCorrigee()
p.push(10)
p.push(20)
assert p.pop() == 20   # OK : LIFO
assert p.pop() == 10   # OK : LIFO
assert p.is_empty() == True  # OK
```

**Résultat** : Le bug vient de l'incohérence entre `insert(0, ...)` et `pop()`. La version corrigée utilise `append` + `pop()` du même côté, rétablissant le comportement LIFO.

### Corrigé exercice 8

**Méthode** : On identifie chaque accès direct à l'attribut interne `notes` dans le code client, puis on propose des méthodes d'interface qui encapsulent ces accès et permettent de changer la représentation interne sans modifier le code client.

**1.** Lignes violant la separation interface/implementation :
- `print(g.notes[0])` : acces direct a l’attribut interne `notes` et indexation.
- `g.notes.sort()` : modification directe de la structure interne.
- `print(g.notes[-1])` : acces direct a l’attribut interne par indexation.
- `print(len(g.notes))` : acces direct a la taille de la structure interne.

**2.** Methodes d’interface proposees :
- `note_a_indice(i)` : renvoie la note a l’indice `i`. Remplace `g.notes[0]`.
- `trier()` : trie les notes. Remplace `g.notes.sort()`.
- `meilleure_note()` : renvoie la note la plus elevee. Remplace `g.notes[-1]` (apres tri).
- `nombre_notes()` : renvoie le nombre de notes. Remplace `len(g.notes)`.

**3.** Classe refactorisee :

```python
class GestionNotes:
    def __init__(self):
        self._notes = []

    def ajouter_note(self, note):
        """Ajoute une note."""
        self._notes.append(note)

    def moyenne(self):
        """Renvoie la moyenne des notes."""
        if len(self._notes) == 0:
            raise ValueError("aucune note")
        return sum(self._notes) / len(self._notes)

    def note_a_indice(self, i):
        """Renvoie la note a l’indice i."""
        if i < 0 or i >= len(self._notes):
            raise IndexError("indice invalide")
        return self._notes[i]

    def trier(self):
        """Trie les notes par ordre croissant."""
        self._notes.sort()

    def meilleure_note(self):
        """Renvoie la note la plus elevee."""
        if len(self._notes) == 0:
            raise ValueError("aucune note")
        return max(self._notes)

    def nombre_notes(self):
        """Renvoie le nombre de notes."""
        return len(self._notes)
```

**4.** Code client refactorise :

```python
g = GestionNotes()
g.ajouter_note(15)
g.ajouter_note(12)
g.ajouter_note(18)

print(g.note_a_indice(0))    # premiere note
g.trier()                     # tri via l’interface
print(g.meilleure_note())     # meilleure note
print(g.nombre_notes())       # nombre de notes
```

**5.** Cette refactorisation permet de changer la representation interne car le code client n’accede plus jamais a `_notes` directement. Par exemple, si on remplace `self._notes = []` par `self._notes = {}` (dictionnaire `{indice: note}`), il suffit d’adapter le code interne des methodes. Le code client, qui appelle uniquement `ajouter_note`, `moyenne`, `note_a_indice`, `trier`, `meilleure_note` et `nombre_notes`, reste inchange.

**Résultat** : Le code refactorisé encapsule l’attribut `_notes` derrière des méthodes d’interface, permettant de changer la représentation interne (liste vers dictionnaire) sans modifier le code client.


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


## Barème

| Exercice | Points |
|---|---|
| Exercices 1-4 | 2 pts chacun |
| Exercices 5-8 | 3 pts chacun |
| **Total** | **20** |

