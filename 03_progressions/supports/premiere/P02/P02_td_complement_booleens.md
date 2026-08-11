---
title: "P02 - Td - Complément à deux et booléens"
level: "premiere"
sequence_id: "P02"
document_type: "td"
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

# P02 - TD - Complément à deux et booléens

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
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : résoudre décodage signé avec `11110110` sur 8 bits.
- Production attendue : `-10`.
- Contrainte de contrôle : faire apparaître le contrôle « bit de poids fort à 1 ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : expliquer bornes sur n bits à partir de `n = 4` bits signés.
- Production attendue : `[-8 ; 7]`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-02A, P-DATA-BASE-02B.
- Énoncé disciplinaire : comparer encodage négatif avec `-6` sur 8 bits.
- Production attendue : `11111010`.
- Contrainte de contrôle : comparer avec le cas « retenue finale ignorée sur la largeur fixée ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : corriger simplification booléenne pour `(a and b) or (a and not b)`.
- Production attendue : `a`.
- Contrainte de contrôle : corriger l’erreur « Simplifier une expression booléenne avec un seul exemple. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : tester un cas limite lié à bit de poids fort à 1.
- Production attendue : le comportement de décodage signé est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : classer deux méthodes possibles pour bornes sur n bits.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Oublier de tester les bornes avant l’encodage. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : justifier un transfert qui utilise encodage négatif avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur simplification booléenne.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Remplir les quatre lignes de la table avant de conclure. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : `-10`.
- Contrôle : faire apparaître le contrôle « bit de poids fort à 1 ».
- Erreur traitée : EF1 - Lire un mot binaire signé comme un entier naturel.
- Donnée utilisée alpha dans P02 td complement booleens : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P02 td complement booleens : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P02 td complement booleens : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `[-8 ; 7]`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Oublier de tester les bornes avant l’encodage.
- Donnée utilisée beta dans P02 td complement booleens : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P02 td complement booleens : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P02 td complement booleens : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `11111010`.
- Contrôle : comparer avec le cas « retenue finale ignorée sur la largeur fixée ».
- Erreur traitée : EF3 - Inverser les bits sans ajouter 1.
- Donnée utilisée gamma dans P02 td complement booleens : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P02 td complement booleens : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P02 td complement booleens : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : `a`.
- Contrôle : corriger l’erreur « Simplifier une expression booléenne avec un seul exemple. ».
- Erreur traitée : EF4 - Simplifier une expression booléenne avec un seul exemple.
- Donnée utilisée delta dans P02 td complement booleens : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P02 td complement booleens : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P02 td complement booleens : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de décodage signé est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Lire un mot binaire signé comme un entier naturel.
- Donnée utilisée epsilon dans P02 td complement booleens : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P02 td complement booleens : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P02 td complement booleens : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Oublier de tester les bornes avant l’encodage. » est une erreur.
- Erreur traitée : EF2 - Oublier de tester les bornes avant l’encodage.
- Donnée utilisée zeta dans P02 td complement booleens : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P02 td complement booleens : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P02 td complement booleens : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Inverser les bits sans ajouter 1.
- Donnée utilisée eta dans P02 td complement booleens : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P02 td complement booleens : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P02 td complement booleens : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Remplir les quatre lignes de la table avant de conclure. ».
- Erreur traitée : EF4 - Simplifier une expression booléenne avec un seul exemple.
- Donnée utilisée theta dans P02 td complement booleens : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P02 td complement booleens : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P02 td complement booleens : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P02 td complement booleens : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

### Exercice 9
- Objectif travaillé : O1, O2, O3, O4.
- Capacité officielle : P-DATA-BASE-02A.
- Énoncé disciplinaire : évaluer le nombre de bits nécessaires à l’écriture en base 2 d’un entier, d’une somme et d’un produit. On travaille avec des entiers naturels (non signés). (9a) Combien de bits sont nécessaires pour écrire 200 en base 2 ? Justifier par la méthode des divisions successives. (9b) Un capteur renvoie des valeurs entre 0 et 1023. Combien de bits faut-il pour coder chaque mesure ? (9c) Deux mesures valent respectivement 500 et 600. Combien de bits faut-il pour coder leur somme ? Leur produit ? (9d) On stocke un pixel en niveaux de gris sur 8 bits (0 à 255). Est-il possible de stocker la somme de deux pixels sur 8 bits ?
- Production attendue : 8 bits (200), 10 bits (1023), 11 bits (somme), 19 bits (produit), débordement (pixel).
- Contrainte de contrôle : vérifier chaque résultat par encadrement entre deux puissances de 2 consécutives.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.

### Corrigé exercice 9
- Résultat : (9a) 200 nécessite 8 bits (8 divisions par 2 ; 2⁷ = 128 ≤ 200 < 256 = 2⁸). (9b) 1023 nécessite 10 bits (2⁹ = 512 ≤ 1023 < 1024 = 2¹⁰). (9c) 500 sur 9 bits, 600 sur 10 bits ; somme 1100 sur 11 bits (2¹⁰ ≤ 1100 < 2¹¹) ; produit 300 000 sur 19 bits (2¹⁸ ≤ 300 000 < 2¹⁹ ; borne p+q = 9+10 = 19 atteinte). (9d) Non : 255+255 = 510 nécessite 9 bits, débordement sur 8 bits.
- Contrôle : chaque réponse vérifiée par encadrement 2^(k-1) ≤ n < 2^k.
- Erreur traitée : confondre le nombre de bits d’un entier avec sa valeur, ou oublier qu’une somme peut nécessiter un bit supplémentaire.

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
