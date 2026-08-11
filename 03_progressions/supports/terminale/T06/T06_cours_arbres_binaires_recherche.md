---
title: "T06 - cours - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01C"
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - Cours - arbres binaires de recherche

## Objectifs spécifiques
- Identifier les données utiles de la situation : ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14.
- Employer le vocabulaire : invariant ABR, recherche, insertion, parcours infixe, arbre vide, doublon.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-ALGO-01C.
- T-ALGO-01E.
- T-ALGO-01F.

## Situation-problème
ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14

## À savoir
- invariant ABR.
- recherche.
- insertion.
- parcours infixe.
- arbre vide.
- doublon.
- complexité hauteur.

## Méthodes
- comparer à la racine.
- descendre gauche ou droite.
- insérer une feuille.
- parcours infixe pour clés triées.

### Méthode — parcours en profondeur d'un arbre (T-ALGO-01C)

Sur l'ABR `[8, 3, 10, 1, 6, 14]`, les trois ordres de parcours en profondeur donnent :

- **Parcours infixe** (gauche, racine, droite) : `[1, 3, 6, 8, 10, 14]` — produit les clés dans l'ordre croissant pour un ABR.
- **Parcours préfixe** (racine, gauche, droite) : `[8, 3, 1, 6, 10, 14]` — la racine apparaît en premier, utile pour reconstruire l'arbre.
- **Parcours suffixe** (gauche, droite, racine) : `[1, 6, 3, 14, 10, 8]` — la racine apparaît en dernier, utile pour libérer la mémoire.

Chacun est récursif : on applique le même parcours aux sous-arbres gauche et droit, puis on traite la racine à la position définie par l'ordre.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Méthode : comparer à la racine.
- Résultat attendu : chercher 6 : 8 -> 3 -> 6.
- Contrôle : capacité T-ALGO-01E et cas limite `arbre vide`.
### Exemple corrigé 2
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Méthode : descendre gauche ou droite.
- Résultat attendu : insérer 7 : 8 -> 3 -> 6 -> droite.
- Contrôle : capacité T-ALGO-01F et cas limite `doublon 6`.
### Exemple corrigé 3
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Méthode : insérer une feuille.
- Résultat attendu : infixe -> 1,3,6,8,10,14.
- Contrôle : capacité T-ALGO-01E et cas limite `arbre dégénéré`.
### Exemple corrigé 4
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Méthode : parcours infixe pour clés triées.
- Résultat attendu : arbre vide -> nouvelle racine.
- Contrôle : capacité T-ALGO-01F et cas limite `arbre vide`.

## Cas limites
- arbre vide.
- doublon 6.
- arbre dégénéré.

## Erreurs fréquentes
- gauche et droite inversées.
- logarithmique sans équilibre.
- racine vide oubliée.

## Exercices intégrés
1. Identifier les données utiles dans `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
2. Appliquer : comparer à la racine.
3. Appliquer : descendre gauche ou droite.
4. Décider le cas limite `arbre vide`.

## Critères de réussite observables
- Une capacité parmi T-ALGO-01E, T-ALGO-01F est citée et utilisée.
- Le résultat attendu est explicite : chercher 6 : 8 -> 3 -> 6.
- Le cas limite `doublon 6` est tranché.

## Lien avec la progression
- Séance : T06-S1 à T06-S4.
- TD : `T06_TD_arbres_binaires_recherche.md`.
- TP : `T06_tp_arbres_binaires_recherche.md`.
- Évaluation : `T06_evaluation_arbres_binaires_recherche.md`.

## Parcours d'un arbre en trois ordres

La capacité T-ALGO-01C demande de parcourir un arbre en ordres infixe, préfixe et suffixe (postfixe).

### Définitions

Pour chaque nœud, on visite son sous-arbre gauche (G), le nœud lui-même (N), et son sous-arbre droit (D) :

| Ordre | Séquence | Usage typique |
|-------|----------|---------------|
| **Préfixe** | N, G, D | Copie de l'arbre, notation polonaise |
| **Infixe** | G, N, D | Tri des clés d'un ABR (ordre croissant) |
| **Suffixe (postfixe)** | G, D, N | Libération mémoire, évaluation d'expressions |

### Exemple sur un ABR

```
        8
       / \
      3   10
     / \    \
    1   6   14
```

- **Préfixe** : 8, 3, 1, 6, 10, 14
- **Infixe** : 1, 3, 6, 8, 10, 14 (clés triées)
- **Suffixe** : 1, 6, 3, 14, 10, 8

### Implémentation récursive

```python
def prefixe(noeud):
    if noeud is None:
        return []
    return [noeud.valeur] + prefixe(noeud.gauche) + prefixe(noeud.droite)

def infixe(noeud):
    if noeud is None:
        return []
    return infixe(noeud.gauche) + [noeud.valeur] + infixe(noeud.droite)

def suffixe(noeud):
    if noeud is None:
        return []
    return suffixe(noeud.gauche) + suffixe(noeud.droite) + [noeud.valeur]
```

### Cas limites

- Arbre vide → les trois parcours renvoient `[]`.
- Arbre à un seul nœud → les trois parcours renvoient `[valeur]`.
- Arbre dégénéré (chaîne) → les trois ordres sont distincts mais linéaires.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur arbres binaires de recherche. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : racine, sous-arbre gauche, sous-arbre droit, invariant, parcours infixe, hauteur.
- Capacités reliées : T-ALGO-01E, T-ALGO-01F.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- comparer la clé cherchée à la racine puis descendre du bon côté.
- insérer une clé en préservant gauche < racine < droite.
- vérifier le parcours infixe trié.

### Erreurs fréquentes spécifiques
- Un élève peut placer un doublon sans règle explicite ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut confondre arbre binaire et ABR ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut oublier le cas arbre vide ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de arbres binaires de recherche.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
