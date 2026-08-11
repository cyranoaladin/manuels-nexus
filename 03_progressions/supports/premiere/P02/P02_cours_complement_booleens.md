---
title: "P02 - Cours - Complément à deux et booléens"
level: "premiere"
sequence_id: "P02"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation machine"
notion: "entier signé, complément à deux, débordement, expression booléenne"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-02A"
    - "P-DATA-BASE-02B"
---

# P02 - Cours - Complément à deux et booléens

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-02A
- P-DATA-BASE-02B

## Prérequis
- Reconnaître une consigne liée à entier signé.
- Distinguer donnée, méthode et conclusion dans le thème Représentation machine.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P02-S1 à P02-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un capteur transmet un octet qui peut représenter une température signée ou un ensemble d’indicateurs logiques.

## Activité d’entrée
1. Décoder `11110110` sur 8 bits signés.
2. Comparer l’intervalle représentable sur 4 bits et sur 8 bits.
3. Simplifier `(a and b) or (a and not b)` avec une table.
4. Repérer un débordement lors de l’encodage de 140 sur 8 bits signés.

## Définitions et formalisation
- Définition D1 : entier signé est utilisé dans Représentation machine avec une donnée, une règle et un contrôle.
- Définition D2 : complément à deux est utilisé dans Représentation machine avec une donnée, une règle et un contrôle.
- Définition D3 : débordement est utilisé dans Représentation machine avec une donnée, une règle et un contrôle.
- Définition D4 : expression booléenne est utilisé dans Représentation machine avec une donnée, une règle et un contrôle.
- Cas limite principal : bit de poids fort à 1.

## Exemples corrigés précis
### Exemple corrigé 1 - décodage signé
- Donnée étudiée : `11110110` sur 8 bits.
- Méthode : lire le bit de signe puis soustraire `2^8` à la valeur naturelle.
- Résultat obtenu : `-10`.
- Contrôle : le cas limite « bit de poids fort à 1 » est vérifié séparément.
### Exemple corrigé 2 - bornes sur n bits
- Donnée étudiée : `n = 4` bits signés.
- Méthode : calculer `-2^(n-1)` et `2^(n-1)-1`.
- Résultat obtenu : `[-8 ; 7]`.
- Contrôle : le cas limite « asymétrie entre minimum et maximum » est vérifié séparément.
### Exemple corrigé 3 - encodage négatif
- Donnée étudiée : `-6` sur 8 bits.
- Méthode : partir de 6, inverser les bits puis ajouter 1.
- Résultat obtenu : `11111010`.
- Contrôle : le cas limite « retenue finale ignorée sur la largeur fixée » est vérifié séparément.
### Exemple corrigé 4 - simplification booléenne
- Donnée étudiée : `(a and b) or (a and not b)`.
- Méthode : dresser les quatre lignes de vérité.
- Résultat obtenu : `a`.
- Contrôle : le cas limite « un exemple ne prouve pas une identité » est vérifié séparément.
## Évaluer le nombre de bits nécessaires en base 2

La capacité P-DATA-BASE-02A demande d'évaluer le nombre de bits nécessaires à l'écriture en base 2 d'un entier naturel, d'une somme ou d'un produit. Les tailles courantes sont 8, 16, 32 et 64 bits.

### Règle fondamentale

Un entier naturel `n` (n ≥ 1) s'écrit en base 2 avec exactement `⌊log₂(n)⌋ + 1` bits. En pratique, on cherche la plus petite puissance de 2 strictement supérieure à `n`.

| Entier `n` | Écriture binaire | Nombre de bits |
|-----------|-----------------|---------------|
| 0 | `0` | 1 |
| 1 | `1` | 1 |
| 7 | `111` | 3 |
| 8 | `1000` | 4 |
| 255 | `11111111` | 8 |
| 256 | `100000000` | 9 |
| 1000 | `1111101000` | 10 |

### Méthode par divisions successives

Pour trouver le nombre de bits de `n` sans logarithme, on divise `n` par 2 de façon répétée et on compte les divisions :

```
n = 200
200 ÷ 2 = 100   → bit 0
100 ÷ 2 = 50    → bit 1
50  ÷ 2 = 25    → bit 2
25  ÷ 2 = 12 r1 → bit 3
12  ÷ 2 = 6     → bit 4
6   ÷ 2 = 3     → bit 5
3   ÷ 2 = 1 r1  → bit 6
1   ÷ 2 = 0 r1  → bit 7
→ 200 nécessite 8 bits
```

### Évaluer les bits d'une somme

La somme de deux entiers peut nécessiter un bit de plus que le plus grand des deux. Exemples :

- `120 + 100 = 220` : les deux tiennent sur 7 bits, la somme tient sur 8 bits.
- `200 + 200 = 400` : chacun tient sur 8 bits, la somme nécessite 9 bits.

Règle : si `a` et `b` tiennent sur `k` bits, leur somme tient sur au plus `k + 1` bits.

### Évaluer les bits d'un produit

Le produit de deux entiers peut nécessiter la somme des nombres de bits. Exemples :

- `15 × 15 = 225` : chacun sur 4 bits, le produit tient sur 8 bits.
- `255 × 255 = 65025` : chacun sur 8 bits, le produit tient sur 16 bits.

Règle : si `a` tient sur `p` bits et `b` sur `q` bits, le produit `a × b` tient sur au plus `p + q` bits.

### Cas limites

- L'entier 0 ne nécessite qu'un bit (par convention).
- En Python les entiers sont de taille arbitraire ; la contrainte de taille fixe (8, 16, 32, 64 bits) est celle du matériel.
- Un débordement se produit quand le résultat dépasse la capacité du registre.

## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-DATA-BASE-02A.
- Point de départ : `11110110` sur 8 bits.
- Angle disciplinaire : repérage initial autour de décodage signé.
- Démarche attendue : lire le bit de signe puis soustraire `2^8` à la valeur naturelle.
- Exemple associé : `-10`.
- Point de vigilance : Lire un mot binaire signé comme un entier naturel.
- Activité de reprise associée : Regarder d’abord le bit de poids fort puis choisir naturel ou signé.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-DATA-BASE-02A.
- Point de départ : `n = 4` bits signés.
- Angle disciplinaire : méthode guidée autour de bornes sur n bits.
- Démarche attendue : calculer `-2^(n-1)` et `2^(n-1)-1`.
- Exemple associé : `[-8 ; 7]`.
- Point de vigilance : Oublier de tester les bornes avant l’encodage.
- Activité de reprise associée : Écrire explicitement l’intervalle avant chaque conversion.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-DATA-BASE-02A.
- Point de départ : `-6` sur 8 bits.
- Angle disciplinaire : transfert argumenté autour de encodage négatif.
- Démarche attendue : partir de 6, inverser les bits puis ajouter 1.
- Exemple associé : `11111010`.
- Point de vigilance : Inverser les bits sans ajouter 1.
- Activité de reprise associée : Séparer inversion et ajout de 1 dans deux lignes distinctes.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-DATA-BASE-02A.
- Point de départ : `(a and b) or (a and not b)`.
- Angle disciplinaire : vérification critique autour de simplification booléenne.
- Démarche attendue : dresser les quatre lignes de vérité.
- Exemple associé : `a`.
- Point de vigilance : Simplifier une expression booléenne avec un seul exemple.
- Activité de reprise associée : Remplir les quatre lignes de la table avant de conclure.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre décodage signé avec `11110110` sur 8 bits ; attendu : `-10`.
- Exercice 2 : expliquer bornes sur n bits à partir de `n = 4` bits signés ; attendu : `[-8 ; 7]`.
- Exercice 3 : comparer encodage négatif avec `-6` sur 8 bits ; attendu : `11111010`.
- Exercice 4 : corriger simplification booléenne pour `(a and b) or (a and not b)` ; attendu : `a`.
- Exercice 5 : tester un cas limite lié à bit de poids fort à 1 ; attendu : le comportement de décodage signé est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour bornes sur n bits ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise encodage négatif avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur simplification booléenne ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `11110110` sur 8 bits, appliquer la méthode « lire le bit de signe puis soustraire `2^8` à la valeur naturelle », puis écrire `-10` ; résultat : `-10` ; contrôle : faire apparaître le contrôle « bit de poids fort à 1 ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de calculer `-2^(n-1)` et `2^(n-1)-1` avant de conclure par `[-8 ; 7]` ; résultat : `[-8 ; 7]` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « retenue finale ignorée sur la largeur fixée » et valider `11111010` ; résultat : `11111010` ; contrôle : comparer avec le cas « retenue finale ignorée sur la largeur fixée ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Simplifier une expression booléenne avec un seul exemple. » puis reprendre la procédure correcte ; résultat : `a` ; contrôle : corriger l’erreur « Simplifier une expression booléenne avec un seul exemple. ».
- Corrigé exercice 5 : méthode : identifier `11110110` sur 8 bits, appliquer la méthode « lire le bit de signe puis soustraire `2^8` à la valeur naturelle », puis écrire `-10` ; résultat : le comportement de décodage signé est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de calculer `-2^(n-1)` et `2^(n-1)-1` avant de conclure par `[-8 ; 7]` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Oublier de tester les bornes avant l’encodage. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « retenue finale ignorée sur la largeur fixée » et valider `11111010` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Simplifier une expression booléenne avec un seul exemple. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Remplir les quatre lignes de la table avant de conclure. ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Lire un mot binaire signé comme un entier naturel.
- Erreur fréquente EF2 - Oublier de tester les bornes avant l’encodage.
- Erreur fréquente EF3 - Inverser les bits sans ajouter 1.
- Erreur fréquente EF4 - Simplifier une expression booléenne avec un seul exemple.

## Remédiation ciblée
- Activité corrective EF1 : Regarder d’abord le bit de poids fort puis choisir naturel ou signé.
- Activité corrective EF2 : Écrire explicitement l’intervalle avant chaque conversion.
- Activité corrective EF3 : Séparer inversion et ajout de 1 dans deux lignes distinctes.
- Activité corrective EF4 : Remplir les quatre lignes de la table avant de conclure.

## Différenciation
- Socle : traiter `11110110` sur 8 bits avec une fiche méthode fournie.
- Standard : traiter `n = 4` bits signés en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « retenue finale ignorée sur la largeur fixée » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre décodage signé avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « bit de poids fort à 1 » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre bornes sur n bits avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « asymétrie entre minimum et maximum » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre encodage négatif avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « retenue finale ignorée sur la largeur fixée » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre simplification booléenne avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « un exemple ne prouve pas une identité » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier décodage signé à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier bornes sur n bits à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier encodage négatif à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier simplification booléenne à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- entier signé : terme à employer dans une justification écrite de la séquence.
- complément à deux : terme à employer dans une justification écrite de la séquence.
- débordement : terme à employer dans une justification écrite de la séquence.
- expression booléenne : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P02-A : modifier la donnée du premier exemple de P02 - Cours - Complément à deux et booléens et conserver exactement la même méthode.
- Variante P02-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P02-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P02-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P02-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P02-F : construire une donnée minimale qui force une décision de méthode.
- Variante P02-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P02-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P02-I : relier une erreur fréquente à une activité corrective précise.
- Variante P02-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P02-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P02-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P02-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P02-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P02-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P02-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
