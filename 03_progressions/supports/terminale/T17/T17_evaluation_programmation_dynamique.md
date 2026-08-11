---
title: "T17 - Évaluation - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Rendu de monnaie par programmation dynamique"
bareme: "T17_bareme_programmation_dynamique.md"
corrige: "T17_corrige_programmation_dynamique.md"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Évaluation - Programmation dynamique

## Cadre

- Durée : 45 minutes.
- Total : 20 points.
- Matériel : aucun.
- Capacité évaluée : `T-ALGO-04` — utiliser la programmation dynamique pour écrire un algorithme.

Toutes les questions portent sur un jeu inédit :

```python
pieces = [1, 4, 6]
montant = 8
```

On cherche le nombre minimal de pièces permettant d'obtenir exactement le montant.

## Question 1 — Modéliser les sous-problèmes (4 points)

1. Définir précisément l'état `dp[m]`.
2. Donner l'initialisation de `dp[0]` et des autres cases avant calcul.
3. Écrire la relation de récurrence en précisant quelles pièces sont admissibles.
4. Justifier l'ordre croissant des montants.

## Question 2 — Calculer et reconstruire (6 points)

1. Compléter la table suivante de `m = 0` à `m = 8`.

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` |  |  |  |  |  |  |  |  |  |

2. Pour `m = 8`, écrire les trois candidats correspondant aux pièces 1, 4 et 6.
3. Donner une décomposition optimale de 8 et expliquer comment une table `choix` permet de la reconstruire.

## Question 3 — Écrire l'algorithme (6 points)

Écrire l'algorithme itératif `minimum_pieces(montant, pieces)` qui renvoie le minimum ou `None` lorsque le montant est impossible. La réponse doit faire apparaître : initialisation, deux boucles, garde sur la pièce, mise à jour du minimum et décision finale.

## Question 4 — Cas impossible et coût (4 points)

On remplace les données par `pieces = [4, 6]` et `montant = 7`.

1. Donner la table de 0 à 7 en utilisant `∞` pour un montant impossible.
2. Expliquer pourquoi renvoyer la valeur numérique utilisée pour coder l'infini serait faux.
3. Pour un montant `M` et `k` pièces, donner les complexités en temps et en mémoire de la tabulation.

## Repères enseignant — à masquer dans la projection élève

| Question | Preuve attendue | Résultat exact | Erreur structurante | Critère décisif |
|---|---|---|---|---|
| 1 | état, base, infini, récurrence, ordre | dépendances `m-p < m` | formule sans signification de `dp` | modèle cohérent avant calcul |
| 2 | table et candidats pour 8 | `[0,1,2,3,1,2,1,2,2]`, solution `[4,4]` | remplir par choix glouton | calcul des états et reconstruction |
| 3 | algorithme complet | `None` si état final infini | initialiser toutes les cases à 0 | algorithme exécutable sur les deux cas |
| 4 | table avec impossibles, `O(Mk)`, `O(M)` | `[0,∞,∞,∞,1,∞,1,∞]` | confondre sentinelle et solution | cas impossible explicitement décidé |

## Critères, cas limites et erreurs fréquentes — repères enseignant

- **Critère de réussite observable 1.** La phrase définissant `dp[m]` précise l'indice, la valeur optimisée et le sens de l'impossible.
- **Critère de réussite observable 2.** Chaque mise à jour de la table peut être reliée à un candidat `dp[m-p] + 1` déjà calculé.
- **Cas limite 1 — montant nul.** L'algorithme doit renvoyer zéro et une décomposition vide sans entrer dans la boucle de reconstruction.
- **Cas limite 2 — montant impossible.** Avec `[4, 6]` et 7, la sentinelle finale est convertie en `None` ; elle n'est jamais annoncée comme un minimum numérique.
- **Erreur fréquente 1 — initialiser tout à zéro.** Les états inconnus deviennent de faux optima. Antidote : zéro seulement pour `dp[0]`, sentinelle ailleurs.
- **Erreur fréquente 2 — appliquer le glouton.** Choisir d'abord la plus grande pièce ne calcule pas les trois candidats demandés pour 8. Antidote : écrire la ligne des prédécesseurs avant le minimum.

Le résultat attendu de la question 2 est la table complète `[0,1,2,3,1,2,1,2,2]` accompagnée d'une reconstruction ; le corrigé vérifie les deux productions séparément.

## Aménagement

La version `T17_version_amenagee_programmation_dynamique.md` segmente la construction de la table sans fournir ses valeurs finales.
