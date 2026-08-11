---
title: "T05 - Évaluation - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Arbres et algorithmes"
notion: "arbre binaire, taille, hauteur, feuilles, parcours en largeur, file"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-04B"
    - "T-ALGO-01A"
    - "T-ALGO-01B"
    - "T-ALGO-01D"
---

# T05 - Évaluation - Mesures et parcours d'arbres complément

**Durée : 20 minutes — Sans document — Sans calculatrice**

## Capacités officielles atomiques

- T-STRUCT-04B : Évaluer quelques mesures des arbres binaires (taille, hauteur, feuilles). « Taille, hauteur et feuilles. »
- T-ALGO-01A : Calculer la taille d’un arbre. « Structure récursive adaptée. »
- T-ALGO-01B : Calculer la hauteur d’un arbre. « Cas arbre vide : hauteur conventionnelle -1 (ou 0 selon la convention). »
- T-ALGO-01D : Parcourir un arbre en largeur d'abord. « Lien avec file. »

## Arbre de référence (rappel)

```
        8
       / \
      3   10
     / \    \
    1   6    14
       / \   /
      4   7 13
```

---

Soit l'arbre binaire B suivant :

```
        50
       /  \
      30    70
     / \      \
    20  40     80
   /   /  \
  10  35  45
```

---

## Question 1 — Mesures sur papier (T-STRUCT-04B) — 5 points

**1.a)** (2 pts) Déterminer la taille et la hauteur de l'arbre B. Préciser le plus long chemin pour la hauteur.

**1.b)** (2 pts) Lister toutes les feuilles de l'arbre B.

**1.c)** (1 pt) Donner la taille, la hauteur et les feuilles d’un arbre réduit au seul noeud 99.

---

## Question 2 — Calcul récursif de la taille (T-ALGO-01A) — 5 points

On rappelle la formule récursive :

```
taille(A) = 0                                       si A est vide
taille(A) = 1 + taille(A.gauche) + taille(A.droite) sinon
```

**2.a)** (3 pts) Dérouler `taille(50)` sur l'arbre B. Montrer au moins les 3 premiers niveaux d'appels récursifs et le résultat final.

**2.b)** (2 pts) Énoncer le variant de terminaison et justifier en une phrase que l'algorithme termine toujours.

---

## Question 3 — Calcul récursif de la hauteur (T-ALGO-01B) — 5 points

On rappelle la formule récursive (convention : hauteur de l'arbre vide = -1) :

```
hauteur(A) = -1                                              si A est vide
hauteur(A) = 1 + max(hauteur(A.gauche), hauteur(A.droite))  sinon
```

**3.a)** (3 pts) Dérouler `hauteur(50)` sur l'arbre B. Détailler les appels pour le sous-arbre gauche.

**3.b)** (2 pts) Un élève propose la convention hauteur de l'arbre vide = 0 au lieu de -1. Quelle serait alors la hauteur d’une feuille ? Expliquer pourquoi la convention -1 est préférable.

---

## Question 4 — Parcours en largeur (T-ALGO-01D) — 5 points

**4.a)** (3 pts) Dérouler le parcours BFS de l'arbre B en complétant le tableau :

| Étape | File (avant défilement) | Noeud traité | Résultat partiel |
|-------|------------------------|--------------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| ... | | | |

**4.b)** (1 pt) Quelle structure de données est utilisée pour le BFS ? Pourquoi ne peut-on pas utiliser une pile ?

**4.c)** (1 pt) Quel serait le résultat du parcours BFS d’un arbre vide ?


## Objectifs


## Prérequis


## Situation-problème

Un biologiste modélise un arbre phylogénétique et doit calculer le nombre d'espèces (taille), la profondeur maximale (hauteur) et lister les espèces terminales (feuilles). Comment parcourir l'arbre ?

## Activité d’entrée

Dessiner un arbre binaire de 7 noeuds, compter ses feuilles et mesurer sa hauteur à la main avant de programmer.

## Exemple

Construction collective d'un arbre binaire de 5 noeuds et calcul de sa taille, hauteur et parcours en largeur.

## Exercices

Exercices de calcul de mesures et de parcours sur des arbres binaires variés.

## Corrigé

Les corrigés détaillés sont dans T05_corrige_arbres_mesures_parcours_complement.md.

## Erreurs fréquentes

- EF1 : oublier le cas de l'arbre vide dans la fonction récursive (retourner 0 ou -1).
- EF2 : confondre hauteur et profondeur d'un noeud dans l'arbre.
- EF3 : utiliser une liste au lieu d'une file (deque) pour le parcours en largeur.


## Remédiation

Exercice de remédiation : tracer l'exécution de taille() sur un arbre de 3 noeuds en notant chaque appel récursif.

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

Taille et hauteur calculées correctement par récursion. Parcours en largeur produit le bon ordre avec une file.

## Séance(s) correspondante(s)

Séance dédiée.

Critère de validation : chaque réponse est vérifiable par un contrôle sur l'arbre.
Observable : le parcours en largeur produit les noeuds dans l'ordre attendu.

