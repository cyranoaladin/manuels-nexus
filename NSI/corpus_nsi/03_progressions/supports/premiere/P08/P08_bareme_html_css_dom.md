---
title: "P08 - Barème - HTML, CSS et DOM"
level: "premiere"
sequence_id: "P08"
document_type: "bareme"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "human_review_remediation"
theme: "Interactions dans une page Web"
notion: "Critères observables HTML, CSS et DOM"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
---

# P08 - Barème - HTML, CSS et DOM

## Principes

- Total : 20 points.
- Une erreur d'arbre ne retire pas les points d'analyse DOM d'une autre question.
- Une réponse de code syntaxiquement imparfaite conserve les points des objets et de la méthode si l'intention reste exécutable sans ambiguïté.
- Le résultat seul ne reçoit pas les points de trace.

### Barème question 1 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Place `header` et `main` comme enfants du document | 0,5 | aucun si l'un contient arbitrairement l'autre |
| Place `form` et `p` sous `main`, puis `label`, `select`, `button` sous `form` | 1 | 0,25 par relation correcte, plafond 1 |
| Explique les rôles de `header`, `main`, `form`, `label`, `button` | 1,5 | 0,3 par rôle relié au code |
| Justifie `for="projet"` ↔ `id="projet"` | 1 | 0,5 si l'association est vue sans citer les attributs |

### Barème question 2 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Écrit `#message` | 0,75 | 0,25 pour `.info`, qui cible bien l'élément mais pas par l'identifiant demandé |
| Écrit `#vote button` ou un sélecteur équivalent limité au formulaire | 1 | 0,5 pour `button` seul |
| Produit une règle applicable avec couleur bleu foncé et graisse | 1,5 | 0,5 pour le bon bloc ; 0,5 par propriété correcte |
| Explique que `p` cible tous les paragraphes | 0,75 | 0,25 pour « moins précis » sans ensemble ciblé |

### Barème question 3 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Associe les trois variables aux trois éléments | 1,5 | 0,5 par association |
| Identifie `click` et `traiterVote` | 1 | 0,5 par élément |
| Explique la soumission/rechargement par défaut | 0,75 | 0,25 pour « bloque le bouton » sans effet précis |
| Relie `preventDefault` à l'annulation de ce comportement | 0,75 | aucun si l'instruction est présentée comme une validation du champ |

### Barème question 4 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Trace le cas vide : valeur, test vrai, affectation, arrêt | 2 | 0,5 par état exact |
| Trace le cas `serre` : valeur, test faux, affectation, texte | 2 | 0,5 par état exact |

### Barème question 5 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Place l'ajout après la sortie de la branche vide | 1,5 | 0,75 si la branche valide est identifiée sans position précise |
| Écrit `bouton.disabled = true;` | 1,5 | 0,75 si la propriété `disabled` est citée sans affectation correcte |
| Explique qu'un placement avant `if` bloque la correction d'une saisie vide | 1 | 0,5 pour « trop tôt » sans conséquence utilisateur |

**Total : 4 + 4 + 4 + 4 + 4 = 20 points.**
