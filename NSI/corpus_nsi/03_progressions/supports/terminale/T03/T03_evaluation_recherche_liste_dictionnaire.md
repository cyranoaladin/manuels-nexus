---
title: "T03 - Évaluation - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "evaluation"
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

# Évaluation — Recherche dans une liste vs dans un dictionnaire

**Durée : 15 minutes — Sans document ni calculatrice**

## Capacité évaluée

> T-STRUCT-03C — Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

## Question 1 — Identification et complexité (5 points)

On donne les deux structures suivantes :

```python
villes_liste = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"]
villes_dico = {"Paris": 75, "Lyon": 69, "Marseille": 13, "Toulouse": 31, "Nice": 06}
```

**1.a)** On exécute `"Marseille" in villes_liste`. Décrire le mécanisme utilisé par Python pour effectuer cette recherche. Combien de comparaisons sont effectuées ? (2 pts)

**1.b)** On exécute `"Marseille" in villes_dico`. Décrire le mécanisme utilisé par Python pour effectuer cette recherche. Quelle est sa complexité en moyenne ? (2 pts)

**1.c)** Donner la complexité de chaque opération en notation O. Justifier la différence en une phrase. (1 pt)

---

## Question 2 — Analyse d’un programme (5 points)

Un programme doit vérifier si 10 000 mots appartiennent à un lexique de 300 000 mots. Un développeur propose deux solutions :

```python
# Solution A
lexique_A = ["mot1", "mot2", ..., "mot300000"]  # liste de 300 000 mots

def verifier_A(mots, lexique):
    resultats = []
    for m in mots:
        resultats.append(m in lexique)
    return resultats
```

```python
# Solution B
lexique_B = {"mot1": True, "mot2": True, ..., "mot300000": True}  # dictionnaire

def verifier_B(mots, lexique):
    resultats = []
    for m in mots:
        resultats.append(m in lexique)
    return resultats
```

**2.a)** Pour la solution A, donner l'ordre de grandeur du nombre total d'opérations élémentaires dans le pire cas. Détailler le calcul. (2 pts)

**2.b)** Pour la solution B, donner l'ordre de grandeur du nombre total d'opérations élémentaires. Détailler le calcul. (2 pts)

**2.c)** Quelle solution est la plus adaptée ? Justifier en utilisant les complexités calculées. (1 pt)

---

## Question 3 — Cas limite et erreur (5 points)

On considère le code suivant :

```python
inventaire = {"stylo": 50, "cahier": 30, "gomme": 15, "règle": 20}

# Test 1
print(50 in inventaire)

# Test 2
print("stylo" in inventaire)
```

**3.a)** Que renvoie le Test 1 ? Que renvoie le Test 2 ? Justifier chaque réponse. (2 pts)

**3.b)** Un élève affirme : « Le Test 1 cherche si la valeur 50 est dans le dictionnaire, donc il renvoie `True`. » Identifier et corriger l'erreur de raisonnement. (2 pts)

**3.c)** Écrire l'expression Python correcte pour vérifier si la valeur `50` est présente parmi les valeurs du dictionnaire. Quelle est la complexité de cette opération ? (1 pt)


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


## Barème

| Question | Points |
|---|---|
| Question 1 | 5 |
| Question 2 | 5 |
| Question 3 | 5 |
| **Total** | **15** |

## Critères de réussite

Complexité comparée liste/dictionnaire justifiée. Mesures de temps cohérentes avec la théorie.

## Séance(s) correspondante(s)

Séance dédiée.

Cas limite : recherche dans une liste vide (résultat False immédiat). Cas limite : clé absente du dictionnaire (KeyError ou False selon la méthode).


Critère de validation : chaque réponse est justifiée par la complexité algorithmique.
Observable : l'élève distingue correctement recherche séquentielle et accès par clé.

