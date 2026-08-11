---
title: "Trace écrite - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "trace"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°1 du 22 janvier 2019"
theme: "Représentation des données"
notion: "bits, bases, complément à deux, booléens, texte, listes, tuples, dictionnaires"
duration: "30 min"
difficulty: "standard"
private_data: false
official_program:
  level: "premiere"
  rubrique: "Représentation des données"
  content: "Synthèse des représentations de base et types construits"
  capacities:
    - id: "P-DATA-BASE-01"
      label: "Passer de la représentation d'une base dans une autre."
      evidence: [{section: "Notions essentielles", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#notions-essentielles", type: "trace"}]
    - id: "P-DATA-BASE-02B"
      label: "Utiliser le complément à deux."
      evidence: [{section: "Définitions", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#définitions", type: "trace"}]
    - id: "P-DATA-BASE-04"
      label: "Dresser une table de vérité."
      evidence: [{section: "Méthodes", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#méthodes", type: "trace"}]
    - id: "P-DATA-BASE-05A"
      label: "Identifier l'intérêt des encodages."
      evidence: [{section: "Points de vigilance", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#points-de-vigilance", type: "trace"}]
    - id: "P-DATA-CONSTR-01"
      label: "Renvoyer un p-uplet."
      evidence: [{section: "Exemples minimaux", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#exemples-minimaux", type: "trace"}]
    - id: "P-DATA-CONSTR-02A"
      label: "Lire, modifier et parcourir un tableau."
      evidence: [{section: "À savoir refaire", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#à-savoir-refaire", type: "trace"}]
    - id: "P-DATA-CONSTR-03A"
      label: "Construire et parcourir un dictionnaire."
      evidence: [{section: "À savoir refaire", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#à-savoir-refaire", type: "trace"}]
    - id: "P-LANG-04"
      label: "Utiliser des jeux de tests."
      evidence: [{section: "Auto-positionnement", file: "premiere/sequences/s01_representation_donnees/trace_ecrite.md", anchor: "#auto-positionnement", type: "trace"}]
prerequisites: ["Cours élève S01"]
learning_objectives: ["Mémoriser les méthodes centrales de la séquence."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Trace écrite - S01

## Notions essentielles

- Une donnée est une valeur accompagnée d'une convention de représentation.
- Le bit est l'unité minimale : `0` ou `1`.
- La base 2 utilise deux chiffres, la base 10 dix chiffres, la base 16 seize chiffres.
- Un octet contient 8 bits.
- Deux chiffres hexadécimaux représentent un octet.
- Un entier positif sur `n` bits va de `0` à `2^n - 1`.
- Un entier relatif en complément à deux sur `n` bits va de `-2^(n-1)` à `2^(n-1)-1`.
- Un booléen vaut `True` ou `False`.
- Une table de vérité énumère tous les cas d'une expression booléenne.
- Un texte nécessite un encodage.
- ASCII est limité ; Unicode vise une représentation beaucoup plus large.
- Une liste est ordonnée et modifiable.
- Un tuple regroupe un nombre fixé de valeurs.
- Un dictionnaire associe clés et valeurs.

## Définitions

- Bit : unité d'information binaire.
- Base : système positionnel déterminé par un nombre de chiffres.
- Complément à deux : codage des entiers relatifs sur un nombre fixé de bits.
- Booléen : valeur logique vraie ou fausse.
- Encodage : règle qui transforme un caractère en octets.
- Liste : collection indexée et modifiable.
- Tuple : p-uplet ordonné.
- Dictionnaire : association clé-valeur.

## Méthodes

- Pour convertir une base vers 10, développer avec les puissances de la base.
- Pour convertir de 10 vers une base, diviser successivement par la base.
- Pour lire un complément à deux, regarder le bit de gauche.
- Si le bit de gauche vaut `1`, soustraire `2^n` à la valeur non signée.
- Pour construire une table de vérité, lister tous les couples ou triplets de booléens.
- Pour choisir une structure, identifier l'opération principale.
- Accès par position : liste ou tuple.
- Accès par nom ou identifiant : dictionnaire.
- Données fixes et groupées : tuple.
- Données modifiables et ordonnées : liste.

## Exemples minimaux

- `1011₂ = 11₁₀`.
- `2A₁₆ = 42₁₀`.
- Sur 8 bits, `11111111` vaut `-1` en complément à deux.
- `True and False` vaut `False`.
- `ord("A")` vaut `65`.
- `(3, 4)` peut représenter un point.
- `[3, 4]` peut représenter une liste modifiable.
- `{"A": 3}` associe la clé `"A"` à la valeur `3`.

## Points de vigilance

- Ne pas lire une écriture sans connaître sa base.
- Ne pas lire un complément à deux comme un entier positif.
- Ne pas confondre caractère et octet.
- Ne pas commencer les index Python à `1`.
- Ne pas utiliser une liste quand l'accès par clé domine.
- Ne pas croire qu'un jeu de tests prouve tous les cas.

## À savoir refaire

- Convertir un entier positif entre bases 2, 10 et 16.
- Trouver l'intervalle des relatifs sur `n` bits.
- Encoder et décoder un petit relatif sur 8 bits.
- Construire la table de vérité d'une expression à deux variables.
- Donner les points de code d'une chaîne courte avec `ord`.
- Lire et modifier un élément de liste.
- Ecrire une fonction qui renvoie un tuple.
- Parcourir les couples `clé, valeur` d'un dictionnaire.
- Proposer des tests ordinaires et des cas limites.

## Auto-positionnement

- Je convertis `19₁₀` en base 2 sans aide.
- Je convertis `1F₁₆` en base 10 sans aide.
- J'explique pourquoi `11111110` peut valoir `254` ou `-2`.
- Je dresse une table de vérité à deux variables.
- Je donne un exemple où un dictionnaire est préférable à une liste.
- Je propose un test pour `to_base(0, 2)`.
