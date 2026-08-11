---
title: "TP - S01 Fonctions de représentation"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "tp"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "conversions, complément à deux, tests"
duration: "2 h"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données"
  content: "Mise en œuvre Python"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Changer de base."
      evidence: [{section: "Étapes", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "P-DATA-BASE-02B"
      label: "Utiliser le complément à deux."
      evidence: [{section: "Étapes", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "P-DATA-BASE-04"
      label: "Dresser une table de vérité."
      evidence: [{section: "Étapes", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "P-DATA-BASE-05A"
      label: "Identifier les encodages."
      evidence: [{section: "Étapes", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "P-DATA-CONSTR-01"
      label: "Utiliser les tuples."
      evidence: [{section: "Travail demandé", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#travail-demandé", type: "tp"}]
    - id: "P-DATA-CONSTR-02A"
      label: "Utiliser les listes."
      evidence: [{section: "Travail demandé", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#travail-demandé", type: "tp"}]
    - id: "P-DATA-CONSTR-03A"
      label: "Utiliser les dictionnaires."
      evidence: [{section: "Travail demandé", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#travail-demandé", type: "tp"}]
    - id: "P-LANG-04"
      label: "Utiliser des jeux de tests."
      evidence: [{section: "Tests", file: "premiere/sequences/s01_representation_donnees/tp.md", anchor: "#tests", type: "tp"}]
prerequisites: ["Cours S01", "TD exercices 1 à 5"]
learning_objectives: ["Implémenter et tester des fonctions de représentation."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# TP - Fonctions de représentation

## Contexte

Le cours a posé les conventions.
Le TP transforme ces conventions en fonctions testables.
Le fichier support est `python/representation_tools.py`.
Les tests de référence sont dans `tests/test_representation_tools.py`.

## Objectif

Implémenter, lire et tester des fonctions qui convertissent des entiers, manipulent le complément à deux et choisissent une structure Python.

## Fichiers fournis

- `python/representation_tools.py`
- `tests/test_representation_tools.py`

## Travail demandé

Lire chaque fonction avant de l'exécuter.
Associer chaque fonction à une capacité du cours.
Compléter le tableau de suivi sur papier ou cahier.
Tester `to_base` avec `0`, `1`, `42`, `255`.
Tester `from_base` avec `"0"`, `"101010"`, `"FF"`.
Tester `encode_twos_complement` avec `-1`, `-5`, `127`.
Tester `decode_twos_complement` avec `11111111`, `11111011`, `01111111`.
Tester `unicode_codepoints` avec `"A"` et `"Aé"`.
Tester `choose_container` avec trois scénarios.
Rédiger une phrase de justification pour chaque structure choisie.

## Étapes

Étape 1 : ouvrir le fichier Python.
Étape 2 : repérer les préconditions de `to_base`.
Étape 3 : exécuter les tests existants.
Étape 4 : ajouter sur brouillon un test pour une base invalide.
Étape 5 : expliquer pourquoi `0` doit être traité à part.
Étape 6 : lire le codage de `-5` en complément à deux.
Étape 7 : vérifier l'intervalle représentable sur 8 bits.
Étape 8 : construire une table de vérité xor avec la fonction fournie.
Étape 9 : comparer les points de code de `"A"` et `"é"`.
Étape 10 : choisir une structure pour un stock par référence.
Étape 11 : choisir une structure pour une couleur RGB.
Étape 12 : choisir une structure pour une suite de mesures.

## Tests

Commande de référence : `python scripts/run_python_tests.py`.
Un test doit contenir une entrée.
Un test doit contenir un résultat attendu.
Un test doit expliquer ce que l'on cherche à sécuriser.
Test ordinaire : `to_base(42, 2) == "101010"`.
Test limite : `to_base(0, 2) == "0"`.
Test d'erreur : une base `1` doit provoquer une erreur.
Test de signe : `decode_twos_complement("11111111") == -1`.
Test Unicode : `unicode_codepoints("Aé") == [65, 233]`.

## Livrable

Rendre un court fichier ou cahier contenant :
- les résultats des tests ;
- trois explications de choix de structure ;
- un exemple de cas limite ;
- une remarque sur une erreur évitée.

## Critères de réussite

- Les tests fournis s'exécutent.
- Les conversions sont justifiées.
- Les bornes du complément à deux sont respectées.
- Les choix liste, tuple, dictionnaire sont argumentés.
- Les erreurs sont reliées à des cas limites.

## Aides progressives

- Niveau 1 : lire la docstring avant le code.
- Niveau 2 : tester une seule fonction à la fois.
- Niveau 3 : écrire l'entrée, la sortie attendue et la raison du test.

## Erreurs fréquentes

- Modifier le code avant d'avoir exécuté les tests.
- Confondre valeur Python et représentation textuelle.
- Tester seulement des cas ordinaires.
- Oublier les erreurs attendues.

## Auto-évaluation

- Je sais relier une fonction à une capacité.
- Je sais exécuter les tests.
- Je sais expliquer un cas limite.
- Je sais proposer un test d'erreur.

## Extension experte

Ajouter une fonction `intervalle_complement(bits)` qui renvoie le plus petit et le plus grand entier relatif représentable.
Ajouter les tests pour `bits = 4` et `bits = 8`.
