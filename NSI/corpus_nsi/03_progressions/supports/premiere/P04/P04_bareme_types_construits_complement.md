---
title: "P04 - barème - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "bareme"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Tuples, listes, dictionnaires"
notion: "p-uplet, compréhension, matrice, dictionnaire, itération"
private_data: false
official_program:
  capacities:
    - "P-DATA-CONSTR-01"
    - "P-DATA-CONSTR-02B"
    - "P-DATA-CONSTR-02C"
    - "P-DATA-CONSTR-03A"
    - "P-DATA-CONSTR-03B"
    - "P-DATA-CONSTR-03C"
---

# P04 - Barème - Types construits complément

## Objectifs

- Vérifier la maîtrise des p-uplets (tuples) et de leur immutabilité.
- Évaluer la capacité à utiliser les listes en compréhension et les matrices.
- Contrôler la construction et l'itération sur les dictionnaires.

## Capacités officielles

- P-DATA-CONSTR-01 : Utiliser les p-uplets (tuples) pour représenter des données composites.
- P-DATA-CONSTR-02B : Construire une liste par compréhension.
- P-DATA-CONSTR-02C : Utiliser des listes de listes pour représenter des matrices.
- P-DATA-CONSTR-03A : Construire un dictionnaire par ajout de clés-valeurs.
- P-DATA-CONSTR-03B : Itérer sur les clés, les valeurs ou les items d'un dictionnaire.
- P-DATA-CONSTR-03C : Utiliser des dictionnaires pour structurer des données hétérogènes.

## Prérequis

- Connaître la syntaxe des tuples, listes et dictionnaires en Python.
- Savoir utiliser les boucles for et les indices.
- Comprendre la différence entre type mutable et immutable.

## Situation-problème

Un enseignant gère les résultats d'une classe sous forme de structures Python. Il utilise des tuples pour les coordonnées d'élèves, des listes en compréhension pour filtrer les notes, des matrices pour les emplois du temps et des dictionnaires pour associer noms et moyennes. Le barème guide l'évaluation de ces compétences.

## Activité d’entrée

Créer un tuple contenant le nom, le prénom et la moyenne d'un élève, puis tenter de modifier la moyenne pour constater l'erreur TypeError.

## Exemple

Tuple : eleve = ("Dupont", "Alice", 15.5). Liste en compréhension : [n for n in notes if n >= 10]. Matrice 2×3 : [[1, 2, 3], [4, 5, 6]]. Dictionnaire : {"Alice": 15.5, "Bob": 12.0}.

## Barème question par question

### Barème question 1 — Tuples (P-DATA-CONSTR-01) — 4 points
- 1.a) Création de tuples : 1 point (syntaxe correcte avec parenthèses ou sans, éléments hétérogènes acceptés).
- 1.b) Accès par index : 1 point (accès correct aux éléments par indice, y compris indices négatifs).
- 1.c) Immutabilité : 1 point (explication que l'affectation t[i] = v lève TypeError, avec justification).
- 1.d) Déballage (unpacking) : 1 point (affectation multiple nom, prenom, moy = eleve correcte et expliquée).

### Barème question 2 — Listes et compréhension (P-DATA-CONSTR-02B) — 4 points
- 2.a) Liste en compréhension simple : 1 point (syntaxe [expr for x in iterable] correcte avec résultat exact).
- 2.b) Compréhension avec filtre : 1 point (syntaxe [expr for x in iterable if cond] correcte).
- 2.c) Compréhension imbriquée : 1 point (double boucle for correcte avec résultat attendu).
- 2.d) Équivalence boucle / compréhension : 1 point (réécriture correcte d'une boucle for classique en compréhension).

### Barème question 3 — Matrices (P-DATA-CONSTR-02C) — 4 points
- 3.a) Création d'une matrice : 1 point (liste de listes avec dimensions correctes, initialisation cohérente).
- 3.b) Accès à un élément : 1 point (syntaxe matrice[i][j] correcte, indices ligne puis colonne).
- 3.c) Parcours d'une matrice : 1 point (double boucle for pour parcourir toutes les cellules sans erreur d'indice).
- 3.d) Piège de la copie : 1 point (explication que [[0]*3]*2 crée des références partagées, avec alternative correcte).

### Barème question 4 — Dictionnaires construction (P-DATA-CONSTR-03A) — 4 points
- 4.a) Création par accolades : 1 point (syntaxe {"cle": valeur} correcte avec au moins 3 entrées).
- 4.b) Ajout de clés : 1 point (ajout par affectation d[cle] = valeur, y compris clé déjà existante pour mise à jour).
- 4.c) Compréhension de dictionnaire : 1 point (syntaxe {k: v for k, v in ...} correcte avec résultat attendu).
- 4.d) Clés valides : 1 point (explication que les clés doivent être hashables : str, int, tuple mais pas list).

### Barème question 5 — Dictionnaires itération (P-DATA-CONSTR-03B, P-DATA-CONSTR-03C) — 4 points
- 5.a) Itération sur les clés : 1 point (boucle for k in d ou for k in d.keys() correcte).
- 5.b) Itération sur les valeurs : 1 point (boucle for v in d.values() correcte avec résultat attendu).
- 5.c) Itération sur les items : 1 point (boucle for k, v in d.items() correcte avec utilisation des deux variables).
- 5.d) Structure hétérogène : 1 point (dictionnaire imbriqué ou mixte tuple/dictionnaire utilisé pour modéliser un enregistrement complexe).

## Total : 20 points

## Critères de réussite observables
- La syntaxe Python est correcte et exécutable pour chaque réponse.
- Les types choisis sont justifiés (tuple pour l'immutabilité, dictionnaire pour l'accès par clé).
- Au moins un piège classique (copie de matrice, clé non hashable) est identifié.

## Erreurs fréquentes
- Confondre tuple et liste (utiliser des crochets au lieu de parenthèses ou inversement).
- Oublier la condition if dans une compréhension avec filtre.
- Accéder à une matrice avec matrice[j][i] au lieu de matrice[i][j] (inversion ligne/colonne).
- Utiliser une liste comme clé de dictionnaire (TypeError: unhashable type).
- Confondre d.keys(), d.values() et d.items().

## Exercices

Les exercices évalués sont les questions 1 à 5 de l'évaluation types construits complément P04.

## Corrigé

Les réponses détaillées se trouvent dans P04_corrige_types_construits_complement.md.

## Remédiation

En cas de score inférieur à 10/20, reprendre les exercices sur un seul type construit (tuple ou liste) avant de combiner plusieurs structures.

## Différenciation

- Socle : questions 1 et 2a-2b (tuples et compréhensions simples).
- Standard : questions 3 et 4 (matrices et construction de dictionnaires).
- Expert : questions 2c, 3d et 5d (compréhension imbriquée, piège copie, structure hétérogène).

## Séance(s) correspondante(s)

Séance dédiée aux types construits : tuples, listes, dictionnaires (complément).
