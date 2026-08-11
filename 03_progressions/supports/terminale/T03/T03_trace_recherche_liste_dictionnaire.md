---
title: "T03 - Trace écrite - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "trace"
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

# Trace écrite — Recherche dans une liste vs dans un dictionnaire

## Capacité visée

> Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

## Tableau comparatif essentiel

| | **Liste** | **Dictionnaire** |
|---|-----------|-------------------|
| **Structure** | Séquence ordonnée | Table associative clé-valeur |
| **Repérage** | Par **index** (position entière) | Par **clé** (identifiant unique) |
| **Syntaxe de recherche** | `x in liste` | `cle in dico` |
| **Mécanisme interne** | Parcours séquentiel (élément par élément) | Hachage puis accès direct |
| **Complexité moyenne** | **O(n)** — linéaire | **O(1)** — constante |
| **Pire cas** | O(n) | O(n) (collisions, rare en pratique) |
| **Exemple de durée (n = 10^6)** | ~10 ms | ~0,001 ms |

---

## Formules clés

- **Liste** : temps de recherche proportionnel à `n` (taille de la liste).
- **Dictionnaire** : temps de recherche quasi constant, indépendant de `n`.

---

## Code de référence

```python
# Recherche dans une liste — O(n)
x in liste           # parcours séquentiel

# Recherche dans un dictionnaire — O(1)
cle in dico          # accès direct par clé
```

---

## Points de vigilance

1. **Ne pas confondre** accès par index (`liste[i]`, O(1)) et recherche de valeur (`x in liste`, O(n)).
2. **Ne pas confondre** recherche de clé (`cle in dico`, O(1)) et recherche de valeur dans les valeurs du dictionnaire (`val in dico.values()`, O(n)).
3. Le choix de la structure dépend de l'usage : si l'on effectue beaucoup de recherches, le dictionnaire est préférable.

---

## Mots-clés à retenir

**Recherche** — **parcours séquentiel** — **hachage** — **index** — **clé** — **O(n)** — **O(1)** — **complexité**


## Objectifs


## Capacités officielles


## Prérequis


## Situation-problème

Un programme de correcteur orthographique doit vérifier si un mot appartient au dictionnaire français (300 000 mots). La recherche séquentielle prend trop de temps. Comment accélérer ?

## Activité d’entrée

Mesurer le temps de recherche de 10 000 mots dans une liste de 100 000 éléments, puis dans un dictionnaire de 100 000 clés. Comparer.

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

Cas limite : recherche dans une liste vide. Cas limite : clé absente du dictionnaire. Cas limite : valeur None comme clé (invalide dans certains contextes).
