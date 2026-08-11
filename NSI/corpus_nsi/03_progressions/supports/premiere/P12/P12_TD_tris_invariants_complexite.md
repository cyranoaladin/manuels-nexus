---
title: "P12 - td - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "td"
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

# P12 - TD - tris, invariants et complexité

## Objectifs

- Distinguer les mécanismes du tri par insertion et du tri par sélection sur des listes manipulées à la main.
- Formuler et utiliser un invariant de boucle pour justifier un algorithme de tri.
- Relier une trace concrète, la stabilité et le nombre de comparaisons à une analyse de coût prudente.

## Consigne commune

Travaillez sur papier ou dans un tableau. Une trace doit faire apparaître la liste avant et après chaque action importante ; une réponse uniquement finale ne suffit pas. Les corrections détaillées sont réservées aux repères enseignant.

## Progression socle / standard / approfondissement

- Socle : exercices 1 et 2, pour lire les deux mécanismes de tri.
- Standard : exercices 3 à 6, pour justifier invariants, stabilité et cas limites.
- Approfondissement : exercices 7 et 8, pour comparer les coûts et déboguer un pseudo-code.

## Exercices

### Exercice 1

- **Trace d'une insertion.**
- Type : trace/table.
- Capacité officielle : P-ALGO-02A.
- Données : `temps = [42, 17, 23, 17, 9]`.
- Consigne : pour les passages `i = 1`, `i = 2` puis `i = 3` du tri par insertion, dessinez la séparation entre préfixe trié et suffixe non traité. Écrivez les décalages effectués avant de placer chaque clé.
- Indice socle : après le passage `i = 1`, une seule valeur a quitté le préfixe initial ; vérifiez sa nouvelle position en montrant le décalage.
- Critère de réussite : chaque ligne de la trace indique la clé, les éléments décalés et l'état obtenu ; les deux valeurs `17` ne sont pas confondues.

#### Repères enseignant — continuité de preuve

- Consigne : insérer la clé dans la partie gauche triée ; traiter aussi `liste vide` si nécessaire.

### Exercice 2

- **Trace d'une sélection.**
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-02B.
- Données : `stocks = [31, 8, 26, 14, 19]`.
- Consigne : exécutez les deux premiers tours d'un tri par sélection. Pour chaque tour, annotez le suffixe exploré, le minimum retenu, l'indice de cet élément et l'échange éventuel. Expliquez pourquoi le premier tour n'est pas une insertion.
- Critère de réussite : le minimum est cherché dans tout le suffixe restant et la liste après chaque échange est fournie.

#### Repères enseignant — continuité de preuve

- Consigne : chercher le minimum du suffixe ; traiter aussi `liste déjà triée` si nécessaire.

### Exercice 3

- **Invariant du tri par insertion.**
- Type : justification.
- Capacité officielle : P-ALGO-02C.
- Données : boucle externe d'un tri par insertion, avec l'indice `i` allant de `1` à `n - 1`.
- Consigne : formulez précisément l'invariant « invariant : indices < i triés ». Justifiez son initialisation, sa conservation après insertion de la clé, puis ce que l'on peut conclure à la terminaison. Distinguez l'invariant d'une simple description du résultat final.
- Critère de réussite : les trois moments de la preuve sont reliés à la partie gauche de la liste et à la clé courante.

#### Repères enseignant — continuité de preuve

- Consigne : écrire invariant gauche triée ; traiter aussi `doublons 17` si nécessaire.

### Exercice 4

- **Invariant du tri par sélection.**
- Type : production/écriture.
- Capacité officielle : P-ALGO-02C.
- Données : `notes = [12, 5, 16, 9, 7]` et un indice de tour `i`.
- Consigne : écrivez un invariant adapté au tri par sélection : que garantit le préfixe avant le tour `i` et quel est le rôle du minimum du suffixe ? Montrez, sur le passage de `i = 1` à `i = 2`, comment l'échange conserve cette propriété.
- Critère de réussite : l'explication porte sur les plus petites valeurs déjà placées, pas seulement sur le fait que « la liste avance ».

#### Repères enseignant — continuité de preuve

- Capacité officielle : P-ALGO-02D.
- Données : `temps=[42,17,23,17,9]`. ; jeu_exercice=delta
- Consigne : compter comparaisons intuitives ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : pire cas quadratique.

### Exercice 5

- **Stabilité et doublons.**
- Type : justification.
- Capacité officielle : P-ALGO-02B.
- Données : `[(17, "A"), (12, "B"), (17, "C"), (9, "D")]`, où la lettre repère l'ordre initial des doublons 17.
- Consigne : appliquez le tri par insertion puis le tri par sélection classique à cette liste en comparant seulement la première composante. Relevez l'ordre final des étiquettes `A` et `C`. Lequel des deux algorithmes est stable dans cette version ? Justifiez à partir d'un décalage ou d'un échange précis.
- Critère de réussite : la réponse s'appuie sur une trace portant sur les étiquettes et non sur l'affirmation générale « les doublons restent ensemble ».

### Exercice 6

- **Cas limites et coût qualitatif.**
- Type : cas limite.
- Capacité officielle : P-ALGO-02A.
- Données : `[]`, `[6]`, `[1, 3, 5, 8]` et `[8, 5, 3, 1]`.
- Consigne : pour chacun de ces quatre cas, indiquez si les boucles externes de l'insertion et de la sélection s'exécutent, puis comparez qualitativement le travail réalisé. Pour la liste déjà triée et la liste inversée, donnez une estimation du nombre de comparaisons de valeurs pour l'insertion ; expliquez pourquoi la sélection compare encore tous les candidats de son suffixe.
- Critère de réussite : liste vide et liste à un élément sont distinguées des deux listes de quatre éléments ; aucune complexité exacte n'est inventée lorsque la convention de comptage n'est pas fixée.

### Exercice 7

- **Comparer les coûts sans surpromettre.**
- Type : lecture/analyse.
- Capacité officielle : P-ALGO-02D.
- Données : une liste de taille `n`, dans les cas déjà trié, ordre quelconque et ordre inverse.
- Consigne : complétez un tableau « meilleur / moyen / pire » pour le tri par insertion et le tri par sélection. Précisez ce qui est compté (comparaisons de valeurs, décalages ou échanges) et expliquez la formule qualitative `pire cas quadratique`. Terminez par une phrase qui empêche de conclure que la sélection est linéaire sur une liste déjà triée.
- Critère de réussite : insertion est distingué de sélection ; le cas moyen est présenté comme une estimation en ordre de grandeur, sans fausse précision.

### Exercice 8

- **Débogage d'un tri par insertion.**
- Type : débogage.
- Capacité officielle : P-ALGO-02D.
- Données :

```text
pour i de 1 à n - 1 :
    cle = tab[i]
    j = i - 1
    tant que j > 0 et tab[j] > cle :
        tab[j + 1] = tab[j]
        j = j - 1
    tab[j] = cle
```

- Consigne : identifiez l'erreur d'indice qui laisse échapper la position `0`. Proposez la condition corrigée, puis montrez sur `[4, 2]` pourquoi la version donnée ne trie pas la liste. Ajoutez une vérification sur `[]` : faut-il entrer dans la boucle externe ?
- Production attendue : un pseudo-code annoté qui localise l'indice fautif et explique la trace de `[4, 2]`.
- Critère de réussite : la correction modifie l'indice de destination et la condition de boucle, puis relie cette correction à une trace courte.

## Erreurs fréquentes

- Confondre l'invariant avec la propriété finale, sans dire ce qui est garanti avant le prochain tour.
- Oublier de décaler l'élément à l'indice `0` lors d'une insertion.
- Annoncer un coût linéaire pour la sélection parce que la liste est déjà triée.
- Déclarer qu'un algorithme est stable sans suivre l'identité des doublons.

## Différenciation et aides graduées

- Aide socle : dessiner deux zones, « triée » et « à traiter », et barrer chaque élément déjà comparé.
- Aide standard : utiliser un tableau à trois colonnes `avant / action / après` pour les exercices 1 et 2.
- Approfondissement : pour l'exercice 5, modifier le test de comparaison et discuter l'effet sur la stabilité ; pour l'exercice 7, distinguer comparaisons et écritures.

## Cas limites travaillés

- liste vide ;
- liste à un élément ;
- liste déjà triée ;
- liste triée à l'envers ;
- doublons 17 repérés par une étiquette.

## Corrigé — repères enseignant

### Corrigé exercice 1

- Donnée utilisée : `temps = [42, 17, 23, 17, 9]`, avec la clé `17` au premier passage.
- Méthode : la trace d'insertion décale `42`, puis place la clé ; les passages `i = 2` et `i = 3` donnent respectivement `[17, 23, 42, 17, 9]` et `[17, 17, 23, 42, 9]`.
- Résultat : `insertion après i=1 -> [17,42,23,17,9]`.
- Contrôle : avant chaque passage, le préfixe situé à gauche de `i` est trié ; les décalages ouvrent une place sans perdre les valeurs.

### Corrigé exercice 2

- Donnée utilisée : `stocks = [31, 8, 26, 14, 19]`.
- Méthode : au tour `i = 0`, chercher le minimum du suffixe donne `8` à l'indice 1 ; au tour suivant, le suffixe restant fournit `14` à l'indice 3.
- Résultat : les deux échanges donnent `[8, 31, 26, 14, 19]`, puis `[8, 14, 26, 31, 19]`.
- Contrôle : la sélection parcourt le suffixe entier avant un seul échange éventuel ; elle ne décale pas une clé dans un préfixe.

### Corrigé exercice 3

- Donnée utilisée : l'indice externe `i` et le préfixe `tab[0:i]`.
- Méthode : l'initialisation à `i = 1` donne un préfixe à un élément ; l'insertion de la clé assure la conservation de l'invariant dans `tab[0:i+1]`.
- Résultat : pour `i = n`, tout le tableau est le préfixe trié.
- Contrôle : l'invariant est une propriété maintenue pendant la boucle, pas une simple annonce de l'état final.

### Corrigé exercice 4

- Donnée utilisée : `notes = [12, 5, 16, 9, 7]` et le tour `i` du tri par sélection.
- Méthode : le préfixe `notes[0:i]` contient les plus petites notes rangées ; rechercher le minimum du suffixe puis échanger étend ce préfixe.
- Résultat : placer `5` puis `7` produit `[5, 12, 16, 9, 7]`, puis `[5, 7, 16, 9, 12]`.
- Contrôle : l'invariant porte sur les valeurs déjà choisies et sur le suffixe restant, pas sur l'idée vague que la liste avance.

### Corrigé exercice 5

- Donnée utilisée : `[(17, "A"), (12, "B"), (17, "C"), (9, "D")]`.
- Méthode : l'insertion utilise le test strict `tab[j] > cle`, tandis que la sélection classique échange le minimum trouvé avec le début du suffixe.
- Résultat : l'insertion conserve l'ordre `A` puis `C` ; la sélection peut donner `C` puis `A` après le premier échange qui place `(9, D)`.
- Contrôle : la stabilité se vérifie dans une trace d'étiquettes et dépend des décalages ou échanges effectifs, pas de la seule égalité des valeurs.

### Corrigé exercice 6

- Donnée utilisée : les listes `[]`, `[6]`, `[1, 3, 5, 8]` et `[8, 5, 3, 1]`.
- Méthode : comparer les itérations externes, les décalages de l'insertion et l'exploration des suffixes par la sélection.
- Résultat : les deux premières listes n'entraînent aucune comparaison utile ; l'insertion déjà triée effectue environ trois comparaisons, tandis que la liste inverse conduit à environ `1 + 2 + 3` décalages-comparaisons.
- Contrôle : la sélection examine encore `3 + 2 + 1` candidats sur les deux listes de quatre éléments ; la convention de comptage est annoncée avant toute valeur exacte.

### Corrigé exercice 7

- Donnée utilisée : une liste de taille `n` dans les cas déjà trié, ordre quelconque et ordre inverse.
- Méthode : séparer comparaisons, décalages et échanges avant de comparer les complexités des deux algorithmes.
- Résultat : l'insertion est en `O(n)` dans le meilleur cas et d'ordre quadratique en moyenne et au pire ; la sélection reste d'ordre quadratique en comparaisons dans les trois cas.
- Contrôle : un faible nombre d'échanges dans la sélection ne transforme pas la recherche répétée du minimum du suffixe en coût linéaire.

### Corrigé exercice 8

- Donnée utilisée : le pseudo-code d'insertion et la liste témoin `[4, 2]`.
- Méthode : corriger la condition en `tant que j >= 0 et tab[j] > cle`, puis placer la clé dans `tab[j + 1]` après les décalages.
- Résultat : la version corrigée décale `4` vers l'indice 1 et place `2` à l'indice 0 ; la version initiale laisse la case 0 sans comparaison et perd `4`.
- Contrôle : sur `[]`, la boucle externe n'est pas atteinte, ce qui traite le cas limite sans accès à un indice inexistant.
