---
title: "P12 - corrige - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "corrige"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - Corrigé - tris, invariants et complexité

## Corrigé du TD

### Exercice 1

- Réponse attendue : insertion après i=1 -> [17,42,23,17,9].
- La clé `17` décale `42` ; les passages suivants donnent `[17, 23, 42, 17, 9]`, puis `[17, 17, 23, 42, 9]`. La zone gauche reste triée après chaque placement.

### Exercice 2

- Réponse attendue : le premier minimum est `8`, le deuxième est `14` et, après deux tours, `stocks` vaut `[8, 14, 26, 31, 19]`.
- Au premier tour, `8` est échangé avec `31`, puis `14` est échangé avec `31`. Chaque tour recherche le minimum du suffixe non trié : le préfixe devient trié et contient les plus petites valeurs déjà sélectionnées.

### Exercice 3

- Réponse attendue : invariant : indices < i triés.
- Avant `i = 1`, le préfixe à un élément est trié. L'insertion de la clé conserve le tri du préfixe élargi ; lorsque `i = n`, ce préfixe est toute la liste. Cette preuve ne se réduit pas à annoncer la liste finale.

### Exercice 4

- Invariant : après `k` tours, le préfixe contient les `k` plus petites valeurs, triées, et le suffixe contient les valeurs restantes.
- Initialisation : pour `k = 0`, le préfixe vide satisfait cette propriété. Conservation : rechercher le minimum du suffixe puis l'échanger avec sa première position étend le préfixe sans perdre de valeur. Terminaison : après le dernier tour, le préfixe est toute la liste triée.
- Sur `notes`, placer `5` puis `7` donne d'abord `[5, 12, 16, 9, 7]`, puis `[5, 7, 16, 9, 12]` : à chaque étape, le préfixe contient bien les plus petites valeurs sélectionnées.

### Exercice 5 — stabilité

L'insertion avec comparaison stricte conserve `A` avant `C` pour les deux valeurs 17. Un échange de sélection peut déplacer `A` derrière `C` : il faut donc suivre les étiquettes, et pas seulement les valeurs numériques.

### Exercice 6 — cas limites

Les listes vide et à un élément ne déclenchent aucune action utile. Sur la liste déjà triée, l'insertion n'effectue pas de décalage ; sur la liste inversée, elle multiplie les décalages. La sélection examine ses suffixes dans les deux situations.

### Exercice 7 — coûts

Insertion est en `O(n)` dans le meilleur cas et d'ordre quadratique en moyenne et au pire. Sélection reste d'ordre quadratique en comparaisons, y compris si la liste est déjà triée ; les échanges ne résument pas tout le coût.

### Exercice 8 — débogage

La condition correcte est `j >= 0` et la clé doit être posée dans `tab[j + 1]`. Avec `[4, 2]`, ces deux corrections permettent de décaler `4` puis de placer `2` au début ; aucune boucle externe n'est parcourue pour `[]`.

## Corrigé du TP

Le TP conserve la trace sur `temps=[42,17,23,17,9]` : après le premier passage d'insertion, `insertion après i=1 -> [17,42,23,17,9]`. La sélection traite au contraire le minimum du suffixe avant un échange unique. La trace et le code doivent expliciter l'invariant de leur boucle.

## Corrigé de l'évaluation

- Question 1 : une insertion justifiée montre la clé, le décalage et le préfixe trié.
- Question 2 : une sélection justifiée distingue recherche du minimum et échange.
- Question 3 : l'invariant précise initialisation, conservation et terminaison.
- Question 4 : le coût de la sélection ne devient pas linéaire avec une entrée déjà triée.
