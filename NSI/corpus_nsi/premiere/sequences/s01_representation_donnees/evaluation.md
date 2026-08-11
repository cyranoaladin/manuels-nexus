---
title: "Évaluation - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "evaluation"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "évaluation sommative"
duration: "50 min"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données"
  content: "Evaluation"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Changer de base."
      evidence: [{section: "Questions progressives", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#questions-progressives", type: "evaluation"}]
    - id: "P-DATA-BASE-02B"
      label: "Complément à deux."
      evidence: [{section: "Questions progressives", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#questions-progressives", type: "evaluation"}]
    - id: "P-DATA-BASE-04"
      label: "Booléens."
      evidence: [{section: "Questions progressives", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#questions-progressives", type: "evaluation"}]
    - id: "P-DATA-BASE-05A"
      label: "Texte."
      evidence: [{section: "Questions progressives", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#questions-progressives", type: "evaluation"}]
    - id: "P-DATA-CONSTR-01"
      label: "Tuples."
      evidence: [{section: "Programmation", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#programmation", type: "evaluation"}]
    - id: "P-DATA-CONSTR-02A"
      label: "Listes."
      evidence: [{section: "Programmation", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#programmation", type: "evaluation"}]
    - id: "P-DATA-CONSTR-03A"
      label: "Dictionnaires."
      evidence: [{section: "Programmation", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#programmation", type: "evaluation"}]
    - id: "P-LANG-04"
      label: "Tests."
      evidence: [{section: "Analyse de code", file: "premiere/sequences/s01_representation_donnees/evaluation.md", anchor: "#analyse-de-code", type: "evaluation"}]
prerequisites: ["Cours, TD, TP S01"]
learning_objectives: ["Vérifier les acquis principaux de la séquence."]
assessment: {formative: false, summative: true}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Évaluation - S01

## Durée

50 minutes.

## Matériel autorisé

Aucun ordinateur.
Calculatrice simple autorisée.
Trace écrite non autorisée.

## Compétences évaluées

- Convertir entre bases.
- Interpréter un complément à deux.
- Construire une table de vérité.
- Identifier un encodage de texte.
- Choisir une structure Python.
- Proposer un test.

## Barème

Total : 20 points.
Conversions : 4 points.
Complément à deux : 4 points.
Booléens et texte : 4 points.
Structures Python : 5 points.
Tests et justification : 3 points.

## Questions progressives

Question 1 : convertir `29₁₀` en base 2.
Question 2 : convertir `101101₂` en base 10.
Question 3 : convertir `3F₁₆` en base 10.
Question 4 : donner l'intervalle des entiers relatifs sur 8 bits.
Question 5 : décoder `11111110` comme complément à deux sur 8 bits.
Question 6 : coder `-6` en complément à deux sur 8 bits.
Question 7 : dresser la table de vérité de `a or not b`.
Question 8 : expliquer pourquoi un caractère Unicode peut occuper plusieurs octets.

## Programmation

Question 9 : écrire une fonction `point(x, y)` qui renvoie un tuple.
Question 10 : écrire une expression qui transforme `[1, 2, 3]` en `[2, 3, 4]`.
Question 11 : construire un dictionnaire qui associe `"rouge"` à `3` et `"bleu"` à `2`.
Question 12 : choisir une représentation pour un stock par référence et justifier.

## Justification

Chaque conversion doit afficher une méthode.
Chaque choix de structure doit citer une opération.
Chaque test doit indiquer entrée et résultat attendu.

## Analyse de code

On donne :
```python
def premier(liste):
    return liste[0]
```
Question 13 : donner un cas qui fonctionne.
Question 14 : donner un cas limite qui provoque une erreur.
Question 15 : proposer un test pour ce cas limite.

## Corrigé lié

Le corrigé détaillé est dans `corrige.md`.

## Erreurs fréquentes

- Oublier la base.
- Oublier le nombre de bits.
- Donner une table de vérité incomplète.
- Proposer un test sans résultat attendu.

## Auto-évaluation

- J'ai justifié mes conversions.
- J'ai précisé la convention de signe.
- J'ai écrit tous les cas booléens.
- J'ai relié chaque structure à une opération.

## Extension

Question bonus non comptée dans le barème : expliquer pourquoi les flottants nécessitent une séquence dédiée.
