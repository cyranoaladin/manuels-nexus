---
title: "TD - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "td"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "conversions, complément à deux, booléens, encodage, structures Python"
duration: "2 h"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données"
  content: "Exercices progressifs"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Changer de base."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-BASE-02B"
      label: "Utiliser le complément à deux."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-BASE-04"
      label: "Dresser une table de vérité."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-BASE-05A"
      label: "Identifier les encodages."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-CONSTR-01"
      label: "Utiliser les tuples."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-CONSTR-02A"
      label: "Utiliser les listes."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-DATA-CONSTR-03A"
      label: "Utiliser les dictionnaires."
      evidence: [{section: "Exercices", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#exercices", type: "td"}]
    - id: "P-LANG-04"
      label: "Utiliser des jeux de tests."
      evidence: [{section: "Analyse de code", file: "premiere/sequences/s01_representation_donnees/td.md", anchor: "#analyse-de-code", type: "td"}]
prerequisites: ["Cours et trace écrite S01"]
learning_objectives: ["S'entraîner progressivement et justifier les choix."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "26 juin 2026 - revue de substance", science: "", technical: ""}
---

# TD - S01 Représentation des données

## Situation-problème

Un système d'inscription stocke des identifiants, des droits d'accès, des textes et des réponses à un questionnaire.
Chaque information doit être représentée sans ambiguïté.
Le TD entraîne à choisir et manipuler ces représentations.

## Objectifs

- Convertir sans ambiguïté entre bases.
- Décoder un complément à deux.
- Construire une table de vérité.
- Choisir une structure Python.
- Analyser du code et proposer des tests.

## Exercices

### Exercice 1 - Socle - Bases

Convertir `18₁₀`, `31₁₀`, `42₁₀` en base 2.
Convertir `1010₂`, `1111₂`, `100000₂` en base 10.
Convertir `2A₁₆` et `FF₁₆` en base 10.
Justifier chaque conversion avec les puissances utilisées.

### Exercice 2 - Socle - Octets

Donner la plus petite et la plus grande valeur représentable par un entier positif sur 8 bits.
Dire si `255`, `256`, `128`, `0` peuvent être représentés sur 8 bits sans signe.
Ecrire `255` en base 2 et en base 16.
Expliquer pourquoi deux chiffres hexadécimaux suffisent pour un octet.

### Exercice 3 - Standard - Complément à deux

Sur 8 bits, encoder `5`, `-1`, `-7`, `-128`.
Sur 8 bits, décoder `00000101`, `11111111`, `11111001`, `10000000`.
Donner l'intervalle représentable sur 4 bits.
Dire pourquoi `-9` ne se code pas sur 4 bits.

### Exercice 4 - Socle - Booléens

Dresser la table de vérité de `a and b`.
Dresser la table de vérité de `a or b`.
Dresser la table de vérité de `a and not b`.
Comparer `or` inclusif et xor.

### Exercice 5 - Standard - Texte

Avec Python, on obtient `ord("A") = 65` et `ord("é") = 233`.
Expliquer ce que représente ce nombre.
Comparer `"A".encode("utf-8")` et `"é".encode("utf-8")`.
Dire pourquoi compter les caractères ne suffit pas toujours pour connaître le nombre d'octets.

### Exercice 6 - Socle - Tuples et listes

On représente un point par `(x, y)`.
Ecrire une fonction `milieu(p1, p2)` qui renvoie le point milieu.
On représente des températures par une liste.
Ecrire une compréhension qui ajoute `1` à chaque température.
Justifier pourquoi le point est mieux représenté par un tuple que par deux variables isolées.

### Exercice 7 - Standard - Dictionnaires

On dispose de `votes = ["A", "B", "A", "C", "A", "B"]`.
Construire le dictionnaire des effectifs.
Identifier la clé de plus grand effectif.
Expliquer pourquoi un dictionnaire est adapté à cette tâche.
Donner un cas où une liste serait suffisante.

### Exercice 8 - Expert - Choix de représentation

Pour chaque situation, choisir liste, tuple ou dictionnaire.
Situation A : positions successives d'un robot.
Situation B : coordonnées fixes d'un point.
Situation C : stock par référence produit.
Situation D : table de pixels ligne par ligne.
Situation E : fiche courte avec champs nommés.
Justifier chaque choix par les opérations prévues.

### Exercice 9 - Analyse de code

Lire la fonction suivante.
Elle doit convertir un entier positif en base 2.
```python
def mystere(n):
    bits = ""
    while n > 0:
        bits = str(n % 2) + bits
        n = n // 2
    return bits
```
Tester mentalement `mystere(6)`.
Identifier le cas limite non géré.
Proposer une correction.
Proposer trois tests.

### Exercice 10 - Expert - Justification

Un camarade stocke des utilisateurs sous forme de liste de tuples `(identifiant, nom)`.
Le programme cherche très souvent un nom à partir d'un identifiant.
Expliquer le problème.
Proposer une représentation plus adaptée.
Donner un exemple de transformation vers cette représentation.
Donner un test qui vérifie la transformation.

## Aides progressives

- Niveau 1 : écrire d'abord les puissances de la base.
- Niveau 2 : pour le complément à deux, noter le nombre de bits avant de calculer.
- Niveau 3 : pour les structures Python, écrire l'opération la plus fréquente.

## Erreurs fréquentes

- Lire `11111111` sans préciser la convention.
- Confondre `or` et xor.
- Oublier le cas `n = 0` dans une conversion.
- Choisir une liste alors qu'une clé est utilisée partout.

## Auto-évaluation

- Je sais convertir dans les deux sens.
- Je sais produire une table de vérité.
- Je sais expliquer un choix de structure.
- Je sais proposer des tests pertinents.

## Corrigé associé

Les réponses détaillées sont dans `corrige.md`, sections `TD`.

## Écriture de code

Les exercices 6, 7 et 9 demandent une écriture de code Python.

Le code attendu doit être court, testé sur un cas normal et testé sur un cas limite.

La correction associée précise les variantes acceptables.
