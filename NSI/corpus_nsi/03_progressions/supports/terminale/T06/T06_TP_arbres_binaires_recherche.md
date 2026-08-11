---
title: "T06 - tp - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01A"
    - "T-ALGO-01B"
    - "T-ALGO-01C"
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - TP - arbres binaires de recherche

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (T06_starter_arbres_binaires_recherche.py, T06_tests_attendus_arbres_binaires_recherche.py, T06_corrige_professeur_arbres_binaires_recherche.py).

## Objectif opérationnel
Construire un ABR à partir d'insertions successives, vérifier son invariant et produire une trace de recherche lisible.

L'élève doit distinguer trois décisions :
- comparer la valeur cherchée à la racine courante ;
- descendre à gauche si la valeur est plus petite ;
- descendre à droite si la valeur est plus grande.

La règle de doublon retenue dans ce TP est explicite : une valeur déjà présente n'est pas insérée une seconde fois.

## Donnée fournie
`ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : comparer à la racine.
3. Réaliser : descendre gauche ou droite.
4. Tester le cas limite `arbre vide`.
5. Produire le livrable : chercher 6 : 8 -> 3 -> 6.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `chercher 6 : 8 -> 3 -> 6`.
- 2 points : cas limite `arbre vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
### Corrigé question 2
Résultat attendu : chercher 6 : 8 -> 3 -> 6.
### Corrigé question 3
Résultat attendu : insérer 7 : 8 -> 3 -> 6 -> droite.
### Corrigé question 4
Résultat attendu : `arbre vide` traité sans ambiguïté.

## Exercice complémentaire — Taille et hauteur d'un arbre (T-ALGO-01A, T-ALGO-01B)

On reprend l'ABR construit précédemment à partir de la séquence `[8, 3, 10, 1, 6, 14]`.

**6a.** Écrire une fonction `taille(noeud)` qui renvoie le nombre de nœuds de l'arbre. Tester sur l'ABR donné (résultat attendu : 6).

```python
def taille(noeud):
    if noeud is None:
        return 0
    return 1 + taille(noeud["gauche"]) + taille(noeud["droite"])
```

**6b.** Écrire une fonction `hauteur(noeud)` qui renvoie la hauteur de l'arbre (nombre de niveaux - 1, un arbre réduit à sa racine a une hauteur 0). Tester sur l'ABR donné (résultat attendu : 2).

```python
def hauteur(noeud):
    if noeud is None:
        return -1
    return 1 + max(hauteur(noeud["gauche"]), hauteur(noeud["droite"]))
```

**6c.** Insérer les valeurs `[2, 5, 7, 9, 11, 13, 15]` dans l'ABR. Recalculer la taille (résultat attendu : 13) et la hauteur (résultat attendu : 4). Comparer avec un arbre dégénéré obtenu en insérant `[1, 2, 3, 4, 5, 6]` dans un arbre vide : quelle hauteur obtient-on ? (résultat attendu : 5).

## Liens
- TD lié : `T06_TD_arbres_binaires_recherche.md`.
- Évaluation liée : `T06_evaluation_arbres_binaires_recherche.md`.

## Cas limites travaillés
- arbre vide.
- doublon 6.
- arbre dégénéré.

## Erreurs fréquentes
- gauche et droite inversées.
- logarithmique sans équilibre.
- racine vide oubliée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `chercher 6 : 8 -> 3 -> 6`.
- Au moins un cas limite de la section précédente est décidé.

## Trace attendue détaillée
Insertion de la séquence `[8, 3, 10, 1, 6, 14]` :
1. `8` devient racine.
2. `3 < 8`, donc `3` devient fils gauche de `8`.
3. `10 > 8`, donc `10` devient fils droit de `8`.
4. `1 < 8` puis `1 < 3`, donc `1` devient fils gauche de `3`.
5. `6 < 8` puis `6 > 3`, donc `6` devient fils droit de `3`.
6. `14 > 8` puis `14 > 10`, donc `14` devient fils droit de `10`.

Parcours infixe attendu (T-ALGO-01C) : `[1, 3, 6, 8, 10, 14]`.

Recherche de `6` :
1. comparer `6` à `8` : descendre à gauche ;
2. comparer `6` à `3` : descendre à droite ;
3. comparer `6` à `6` : valeur trouvée.

Recherche de `7` :
1. comparer `7` à `8` : descendre à gauche ;
2. comparer `7` à `3` : descendre à droite ;
3. comparer `7` à `6` : descendre à droite ;
4. le sous-arbre droit de `6` est vide, donc `7` est absent.

## Exigences sur le code
- La fonction d'insertion ne doit jamais trier une liste à la place de construire l'arbre.
- La recherche doit suivre les pointeurs gauche/droite et ne pas parcourir tous les noeuds.
- Le parcours infixe doit visiter gauche, racine, droite.
- Une insertion de doublon `6` doit laisser le parcours infixe inchangé.
- Une recherche dans un arbre vide doit retourner `False` ou une trace vide documentée dans le code.

## Vérifications manuelles avant tests
- `contient(racine, 6)` vaut `True`.
- `contient(racine, 7)` vaut `False`.
- `infixe(racine)` donne `[1, 3, 6, 8, 10, 14]`.
- Après tentative de réinsertion de `6`, `infixe(racine)` reste `[1, 3, 6, 8, 10, 14]`.
- La hauteur n'est pas présentée comme logarithmique si l'arbre n'est pas équilibré.



## Protocole de validation complémentaire
1. Préparer un jeu nominal propre à T06 et noter la sortie attendue avant exécution.
2. Préparer un cas limite distinct et expliquer pourquoi il doit être accepté ou refusé.
3. Exécuter le starter : il doit échouer sur au moins un test complet, ce qui confirme que le travail élève reste à produire.
4. Exécuter le corrigé professeur : il doit produire exactement les valeurs attendues dans les tests.
5. Comparer la trace obtenue avec la consigne : chaque étape doit être justifiée par une donnée du sujet.
6. Noter l'erreur fréquente observée et choisir la remédiation ciblée dans le support associé.

## Livrable vérifiable complémentaire
- Fichier élève complété avec les fonctions demandées dans le TP.
- Trace courte indiquant entrée, traitement, sortie et cas limite.
- Capture textuelle des tests attendus : nominal OK, cas limite OK, entrée invalide traitée.
- Commentaire final indiquant la capacité officielle réellement travaillée.


## Assets Python
- Starter élève : `code/T06_starter_arbres_binaires_recherche.py`.
- Tests attendus : `code/T06_tests_attendus_arbres_binaires_recherche.py`.
- Corrigé professeur : `code/T06_corrige_professeur_arbres_binaires_recherche.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
