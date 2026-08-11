---
title: "P02 - Corrige - Complément à deux et booléens"
level: "premiere"
sequence_id: "P02"
document_type: "corrige"
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


# P02 - Corrigé professeur - Complément à deux et booléens

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

## Méthode générale de correction
- Point 1 : pour décodage signé, exiger la donnée `11110110` sur 8 bits, la méthode « lire le bit de signe puis soustraire `2^8` à la valeur naturelle » et le contrôle « bit de poids fort à 1 ».
- Point 2 : pour bornes sur n bits, exiger la donnée `n = 4` bits signés, la méthode « calculer `-2^(n-1)` et `2^(n-1)-1` » et le contrôle « asymétrie entre minimum et maximum ».
- Point 3 : pour encodage négatif, exiger la donnée `-6` sur 8 bits, la méthode « partir de 6, inverser les bits puis ajouter 1 » et le contrôle « retenue finale ignorée sur la largeur fixée ».
- Point 4 : pour simplification booléenne, exiger la donnée `(a and b) or (a and not b)`, la méthode « dresser les quatre lignes de vérité » et le contrôle « un exemple ne prouve pas une identité ».
## Exercices numérotés
- Exercice 1 : résoudre décodage signé avec `11110110` sur 8 bits ; attendu : `-10`.
- Exercice 2 : expliquer bornes sur n bits à partir de `n = 4` bits signés ; attendu : `[-8 ; 7]`.
- Exercice 3 : comparer encodage négatif avec `-6` sur 8 bits ; attendu : `11111010`.
- Exercice 4 : corriger simplification booléenne pour `(a and b) or (a and not b)` ; attendu : `a`.
- Exercice 5 : tester un cas limite lié à bit de poids fort à 1 ; attendu : le comportement de décodage signé est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour bornes sur n bits ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise encodage négatif avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur simplification booléenne ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `11110110` sur 8 bits, appliquer la méthode « lire le bit de signe puis soustraire `2^8` à la valeur naturelle », puis écrire `-10`.
- Résultat : `-10`.
- Contrôle : faire apparaître le contrôle « bit de poids fort à 1 ».
- Erreur traitée : EF1 - Lire un mot binaire signé comme un entier naturel.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de calculer `-2^(n-1)` et `2^(n-1)-1` avant de conclure par `[-8 ; 7]`.
- Résultat : `[-8 ; 7]`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Oublier de tester les bornes avant l’encodage.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « retenue finale ignorée sur la largeur fixée » et valider `11111010`.
- Résultat : `11111010`.
- Contrôle : comparer avec le cas « retenue finale ignorée sur la largeur fixée ».
- Erreur traitée : EF3 - Inverser les bits sans ajouter 1.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Simplifier une expression booléenne avec un seul exemple. » puis reprendre la procédure correcte.
- Résultat : `a`.
- Contrôle : corriger l’erreur « Simplifier une expression booléenne avec un seul exemple. ».
- Erreur traitée : EF4 - Simplifier une expression booléenne avec un seul exemple.
### Corrigé exercice 5
- Méthode : identifier `11110110` sur 8 bits, appliquer la méthode « lire le bit de signe puis soustraire `2^8` à la valeur naturelle », puis écrire `-10`.
- Résultat : le comportement de décodage signé est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Lire un mot binaire signé comme un entier naturel.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de calculer `-2^(n-1)` et `2^(n-1)-1` avant de conclure par `[-8 ; 7]`.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Oublier de tester les bornes avant l’encodage. » est une erreur.
- Erreur traitée : EF2 - Oublier de tester les bornes avant l’encodage.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « retenue finale ignorée sur la largeur fixée » et valider `11111010`.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Inverser les bits sans ajouter 1.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Simplifier une expression booléenne avec un seul exemple. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Remplir les quatre lignes de la table avant de conclure. ».
- Erreur traitée : EF4 - Simplifier une expression booléenne avec un seul exemple.

### Corrigé exercice 9 — Évaluer le nombre de bits nécessaires (P-DATA-BASE-02A)
- **9a.** 200 nécessite **8 bits**. Méthode : 8 divisions successives par 2. Vérification : 2⁷ = 128 ≤ 200 < 256 = 2⁸.
- **9b.** Valeur maximale 1023. 2⁹ = 512 ≤ 1023 < 1024 = 2¹⁰. Il faut **10 bits**.
- **9c.** 500 nécessite **9 bits** (2⁸ = 256 ≤ 500 < 512 = 2⁹, donc ⌊log₂(500)⌋+1 = 9). 600 nécessite **10 bits** (2⁹ = 512 ≤ 600 < 1024 = 2¹⁰). Somme 1100 : **11 bits** (2¹⁰ = 1024 ≤ 1100 < 2048 = 2¹¹). Produit 300 000 : **19 bits** (2¹⁸ = 262 144 ≤ 300 000 < 524 288 = 2¹⁹). Règle : produit sur au plus 9 + 10 = 19 bits (borne atteinte).
- **9d.** Non : 255 + 255 = 510 nécessite 9 bits. Débordement sur 8 bits. Il faut au moins 9 bits.
- Contrôle : la règle « somme sur k+1 bits, produit sur p+q bits » est vérifiée sur chaque réponse.
- Erreur traitée : confondre le nombre de bits d'un entier avec sa valeur.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « bit de poids fort à 1 » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « retenue finale ignorée sur la largeur fixée » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Simplifier une expression booléenne avec un seul exemple. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Oublier de tester les bornes avant l’encodage. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Remplir les quatre lignes de la table avant de conclure. » ».
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
