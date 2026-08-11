---
title: "P13 - cours - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "dichotomie, glouton et k-NN"
notion: "dichotomie, glouton et k-NN"
private_data: false
official_program:
  capacities:
    - "P-ALGO-03"
    - "P-ALGO-04"
    - "P-ALGO-05"
---

# P13 - Cours - dichotomie, glouton et k-NN

## Objectifs spécifiques
- Identifier les données utiles de la situation : tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4].
- Employer le vocabulaire : dichotomie, variant V = droite − gauche + 1, glouton, choix local, k-NN, distance.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-ALGO-03.
- P-ALGO-04.
- P-ALGO-05.

## Situation-problème
tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]

## À savoir
- dichotomie.
- variant V = droite − gauche + 1 (nombre de candidats).
- glouton.
- choix local.
- k-NN.
- distance.
- vote majoritaire.

## Méthodes
- calculer milieu puis réduire intervalle.
- montrer que V = droite − gauche + 1 décroît strictement.
- prendre la plus grande pièce possible.
- voter parmi k=3 voisins.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
- Méthode : calculer milieu puis réduire intervalle.
- Résultat attendu : milieux 18 puis 37 -> trouvé indice 4.
- Contrôle : capacité P-ALGO-04 et cas limite `cible absente`.
### Exemple corrigé 2 - variant de dichotomie (P-ALGO-04)
- Donnée : `tableau=[4,9,18,23,37,41], cible=37`.
- Méthode : montrer que le variant V = droite − gauche + 1 (nombre de candidats) décroît strictement à chaque étape.
- Résultat attendu : étape 1 → g=0, d=5, V=6 ; étape 2 → g=3, d=5, V=3 → trouvé. V décroît de 6 à 3, prouvant la terminaison.
- Contrôle : capacité P-ALGO-04 et cas limite `cible absente (ex. 38) → V décroît 6→3→1→0, la boucle s'arrête sans trouver`.
### Exemple corrigé 3 - glouton (P-ALGO-05)
- Donnée : `pièces=[10,5,2,1], montant=28`.
- Méthode : prendre la plus grande pièce possible à chaque étape.
- Résultat attendu : 28 = 10 + 10 + 5 + 2 + 1 (5 pièces).
- Contrôle : capacité P-ALGO-05 et cas limite `pièce 1 absente → glouton peut échouer`.
### Exemple corrigé 4 - k-NN (P-ALGO-03)
- Donnée : `voisins=[rouge:1.2, bleu:2.0, rouge:2.4], k=3`.
- Méthode : voter parmi les k=3 plus proches voisins.
- Résultat attendu : rouge (2 voix) vs bleu (1 voix) → classe rouge.
- Contrôle : capacité P-ALGO-03 et cas limite `égalité de vote avec k pair`.

## Cas limites
- cible absente.
- pièce 1 absente.
- égalité de vote.

## Erreurs fréquentes
- dichotomie sur liste non triée.
- glouton supposé toujours optimal.
- égalité k-NN non décidée.

## Exercices intégrés
1. Identifier les données utiles dans `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
2. Appliquer : calculer milieu puis réduire intervalle.
3. Appliquer : montrer que V = droite − gauche + 1 décroît strictement.
4. Décider le cas limite `cible absente`.

## Critères de réussite observables
- Une capacité parmi P-ALGO-03, P-ALGO-04, P-ALGO-05 est citée et utilisée.
- Le résultat attendu est explicite : milieux 18 puis 37 -> trouvé indice 4.
- Le cas limite `pièce 1 absente` est tranché.

## Lien avec la progression
- Séance : P13-S1 à P13-S4.
- TD : `P13_TD_dichotomie_glouton_knn.md`.
- TP : `P13_tp_dichotomie_glouton_knn.md`.
- Évaluation : `P13_evaluation_dichotomie_glouton_knn.md`.

## Algorithme des k plus proches voisins

La capacité P-ALGO-03 demande d'écrire un algorithme qui prédit la classe d'un élément à partir de la classe majoritaire de ses k plus proches voisins.

### Principe

Soit un ensemble de points étiquetés (chaque point a des coordonnées et une classe connue). Pour prédire la classe d'un nouveau point :

1. Calculer la **distance** entre le nouveau point et chaque point de l'ensemble.
2. Trier les points par distance croissante.
3. Sélectionner les **k plus proches** voisins.
4. La classe prédite est la **classe majoritaire** parmi ces k voisins.

### Exemple complet — classification de fleurs

Données d'entraînement (longueur de pétale, largeur de pétale, espèce) :

| Point | Longueur | Largeur | Espèce |
|-------|----------|---------|--------|
| A | 1.4 | 0.2 | setosa |
| B | 4.7 | 1.4 | versicolor |
| C | 1.3 | 0.3 | setosa |
| D | 4.5 | 1.5 | versicolor |
| E | 1.5 | 0.2 | setosa |

Nouveau point à classer : longueur = 1.6, largeur = 0.3, k = 3.

Distances (euclidiennes simplifiées) :
- d(A) = √((1.6−1.4)² + (0.3−0.2)²) = √(0.04 + 0.01) ≈ 0.22
- d(B) = √((1.6−4.7)² + (0.3−1.4)²) = √(9.61 + 1.21) ≈ 3.29
- d(C) = √((1.6−1.3)² + (0.3−0.3)²) = 0.30
- d(D) = √((1.6−4.5)² + (0.3−1.5)²) ≈ 3.14
- d(E) = √((1.6−1.5)² + (0.3−0.2)²) ≈ 0.14

Les 3 plus proches : E (0.14), A (0.22), C (0.30) — tous setosa.

**Prédiction : setosa** (vote unanime).

### Implémentation Python

```python
def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def knn(donnees, nouveau, k):
    """Prédit la classe du nouveau point par vote majoritaire des k plus proches voisins."""
    if not donnees or k <= 0:
        return None  # entrée dégénérée : pas de données ou k invalide
    distances = []
    for point in donnees:
        d = distance(nouveau, (point[0], point[1]))
        distances.append((d, point[2]))  # (distance, classe)
    distances.sort()  # tri par distance croissante
    voisins = distances[:k]
    # Vote majoritaire
    compteur = {}
    for _, classe in voisins:
        compteur[classe] = compteur.get(classe, 0) + 1
    return max(compteur, key=compteur.get)
```

### Cas limites

- **Entrée vide ou k invalide** : la fonction renvoie `None` si les données sont vides ou si `k ≤ 0`. Le comportement sur entrée dégénérée est une décision de spécification — il faut le documenter explicitement.
- **Égalité de vote** (k pair) : si deux classes ont le même nombre de voisins, le résultat dépend de l'ordre de tri. Solution : choisir k impair.
- **k = 1** : le voisin le plus proche décide seul — sensible au bruit.
- **k = n** (taille du dataset) : la classe majoritaire globale est toujours prédite — pas d'apprentissage local.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur dichotomie, glouton et k plus proches voisins. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : intervalle de recherche, milieu, choix glouton, contre-exemple, distance.
- Capacités reliées : P-ALGO-03, P-ALGO-04, P-ALGO-05.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- réduire l’intervalle de dichotomie après chaque comparaison.
- justifier un choix glouton local.
- calculer les distances avant de classer les voisins.

### Erreurs fréquentes spécifiques
- Un élève peut oublier que la dichotomie exige des données triées ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut confondre choix local et optimal global ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut ignorer une égalité de distance ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cible absente : la dichotomie s'arrête quand gauche > droite (V atteint 0).
- Pièce 1 absente : le glouton peut échouer si le reste n'est pas représentable.
- Égalité de vote : k pair dans k-NN → résultat indéterminé, choisir k impair.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de dichotomie, glouton et k plus proches voisins.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
