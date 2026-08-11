---
title: "T17 - TP - Programmer un rendu de monnaie optimal"
level: "terminale"
sequence_id: "T17"
document_type: "tp"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Tabulation et reconstruction d'une solution optimale"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - TP - Programmer un rendu de monnaie optimal

## Cadre

- Durée : 75 minutes.
- Travail : binôme.
- Objectif : construire une table de minima, mémoriser les choix et reconstruire une solution.
- Fichiers fournis : `code/T17_starter_programmation_dynamique.py` et `code/T17_tests_attendus_programmation_dynamique.py`.
- Fichiers à rendre : starter complété renommé `T17_nom1_nom2.py` et compte rendu `T17_nom1_nom2.md`.

## Signatures imposées

```python
def construire_table(montant, pieces) -> tuple[list[int], list[int | None]]:
    ...

def rendu_monnaie_dp(montant, pieces) -> tuple[int, list[int]] | None:
    ...
```

La première fonction renvoie la table des minima et une table `choix`. La seconde renvoie le minimum avec une décomposition, ou `None` si le montant est impossible.

## Mise en route — 10 minutes

Exécuter depuis `code/` :

```bash
python T17_tests_attendus_programmation_dynamique.py
```

Le starter doit échouer sur `NotImplementedError`. Noter le premier cas testé et la sortie attendue.

## Étape 1 — Construire la table — 25 minutes

1. Appeler la validation fournie.
2. Initialiser `dp[0]` à 0 et les autres cases à `montant + 1`.
3. Initialiser `choix` avec `None`.
4. Parcourir les montants croissants puis les pièces.
5. Mettre à jour les deux tables seulement si le candidat est strictement meilleur.

Avant exécution, prévoir la table pour `(8, [1,4,5])`. Le test vérifie aussi les choix aux montants 4, 5 et 8.

## Étape 2 — Reconstruire — 20 minutes

Si l'état final est impossible, renvoyer `None`. Sinon, partir du montant, lire la dernière pièce, l'ajouter à la solution et la soustraire au reste jusqu'à zéro.

Dans le compte rendu, tracer :

- `8 → 4 → 0` pour `[1,4,5]` ;
- `6 → 3 → 0` pour `[1,3,4]`.

Expliquer pourquoi ces traces réfutent les décompositions gloutonnes `5+1+1+1` et `4+1+1`.

## Étape 3 — Cas limites et invalides — 15 minutes

Vérifier :

- montant nul : `(0, [])` ;
- montant 7 impossible avec `[4,6]` : `None` ;
- montant négatif, liste vide pour un montant positif, pièce nulle ou négative : `ValueError`.

## Validation finale — 5 minutes

```bash
TP_MODULE=T17_nom1_nom2 python T17_tests_attendus_programmation_dynamique.py
```

Le livrable est recevable si tous les tests passent et si le compte rendu contient état, initialisation, récurrence, deux reconstructions, cas impossible et complexités `O(Mk)` / `O(M)`.

## Exemples corrigés de validation — repères enseignant

### Exemple corrigé 1 — optimum non glouton

Pour `rendu_monnaie_dp(6, [1, 3, 4])`, la table des minima est `[0, 1, 2, 1, 1, 2, 2]`. La reconstruction suit `6 → 3 → 0` et produit deux pièces `[3, 3]`. Le résultat glouton `[4, 1, 1]` comporte trois pièces et doit donc être rejeté.

### Exemple corrigé 2 — état impossible

Pour `rendu_monnaie_dp(7, [4, 6])`, les prédécesseurs possibles de 7 sont 3 et 1, tous deux inatteignables. La fonction renvoie `None` et ne tente pas de lire une pièce dans `choix[7]`.

## Erreurs fréquentes et critères de réussite

- **Erreur fréquente 1 — mettre à jour `dp[m]` sans `choix[m]`.** La valeur minimale passe les premiers tests, mais la reconstruction échoue. Antidote : effectuer les deux affectations dans la même condition `candidat < dp[m]`.
- **Erreur fréquente 2 — accepter une pièce nulle.** La dépendance `m - 0 = m` ne progresse pas et invalide l'ordre de calcul. Antidote : valider toutes les pièces avant de construire la table.
- **Critère de réussite observable 1.** Les valeurs de `dp`, les choix mémorisés et la décomposition reconstruite sont cohérents sur les deux exemples corrigés.
- **Critère de réussite observable 2.** Les cas montant nul, impossible et données invalides produisent exactement les résultats ou exceptions annoncés.

## Prolongement

Ajouter un paramètre qui départage deux solutions minimales en préférant la plus grande dernière pièce. Écrire un test où plusieurs décompositions ont le même nombre de pièces et expliquer ce qui change dans la condition de mise à jour.

## Repères enseignant

- Corrigé : `code/T17_corrige_professeur_programmation_dynamique.py`.
- Commande de validation : `TP_MODULE=T17_corrige_professeur_programmation_dynamique python T17_tests_attendus_programmation_dynamique.py`.
- Le starter doit rester en échec avant travail.
- Une solution gloutonne qui passe seulement un cas nominal ne valide pas `T-ALGO-04`.
