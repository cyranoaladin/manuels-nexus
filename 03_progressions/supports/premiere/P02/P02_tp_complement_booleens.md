---
title: "P02 - Tp - Complément à deux et booléens"
level: "premiere"
sequence_id: "P02"
document_type: "tp"
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


# P02 - TP - Complément à deux et booléens

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

## Consigne technique détaillée
- Problème à programmer : Implémenter encodage, décodage et détection de débordement sur une largeur fixée.
- Starter code : `code/P02_starter_complement_booleens.py`.
- Tests attendus : `code/P02_tests_attendus_complement_booleens.py`.
- Corrigé professeur séparé : `code/P02_corrige_professeur_complement_booleens.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : bit de poids fort à 1.
## Étapes de réalisation
- Étape 1 : coder ou tester décodage signé à partir de `11110110` sur 8 bits, puis contrôler bit de poids fort à 1.
- Étape 2 : coder ou tester bornes sur n bits à partir de `n = 4` bits signés, puis contrôler asymétrie entre minimum et maximum.
- Étape 3 : coder ou tester encodage négatif à partir de `-6` sur 8 bits, puis contrôler retenue finale ignorée sur la largeur fixée.
- Étape 4 : coder ou tester simplification booléenne à partir de `(a and b) or (a and not b)`, puis contrôler un exemple ne prouve pas une identité.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
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

## Validation opérationnelle du TP
- Vérification P02-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification P02-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification P02-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification P02-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification P02-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification P02-6 : comparer l’algorithme écrit avec la capacité officielle citée.
