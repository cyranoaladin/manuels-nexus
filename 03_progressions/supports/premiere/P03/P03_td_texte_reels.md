---
title: "P03 - Td - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Données textuelles et approximation"
notion: "Unicode, UTF-8, octet, flottant"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-05A"
    - "P-DATA-BASE-03"
---

# P03 - TD - Texte Unicode et nombres réels

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05A
- P-DATA-BASE-03

## Prérequis
- Reconnaître une consigne liée à Unicode.
- Distinguer donnée, méthode et conclusion dans le thème Données textuelles et approximation.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P03-S1 à P03-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un formulaire international mélange accents, symboles monétaires et mesures décimales calculées par programme.

## Activité d’entrée
1. Comparer `A`, `é` et `€` selon caractères et octets.
2. Encoder `Aé` en UTF-8.
3. Observer `0.1 + 0.2` dans Python.
4. Décider quand utiliser une tolérance.

## Exemples corrigés précis
### Exemple corrigé 1 - ASCII simple
- Donnée étudiée : `A`.
- Méthode : lire le point de code U+0041 puis son octet UTF-8.
- Résultat obtenu : `41` en hexadécimal.
- Contrôle : le cas limite « caractère dans l’ASCII » est vérifié séparément.
### Exemple corrigé 2 - accent UTF-8
- Donnée étudiée : `é`.
- Méthode : distinguer un caractère et deux octets.
- Résultat obtenu : `c3 a9`.
- Contrôle : le cas limite « longueur en octets différente de la longueur en caractères » est vérifié séparément.
### Exemple corrigé 3 - chaîne mixte
- Donnée étudiée : `Aé`.
- Méthode : additionner les tailles UTF-8 de chaque caractère.
- Résultat obtenu : 2 caractères et 3 octets.
- Contrôle : le cas limite « chaîne vide » est vérifié séparément.
### Exemple corrigé 4 - flottant
- Donnée étudiée : `0.1 + 0.2`.
- Méthode : comparer avec une tolérance au lieu de `==`.
- Résultat obtenu : valeur proche de `0.3`.
- Contrôle : le cas limite « arrondi binaire » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : résoudre ASCII simple avec `A`.
- Production attendue : `41` en hexadécimal.
- Contrainte de contrôle : faire apparaître le contrôle « caractère dans l’ASCII ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : expliquer accent UTF-8 à partir de `é`.
- Production attendue : `c3 a9`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : comparer chaîne mixte avec `Aé`.
- Production attendue : 2 caractères et 3 octets.
- Contrainte de contrôle : comparer avec le cas « chaîne vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-05A, P-DATA-BASE-03.
- Énoncé disciplinaire : corriger flottant pour `0.1 + 0.2`.
- Production attendue : valeur proche de `0.3`.
- Contrainte de contrôle : corriger l’erreur « Confondre point de code et représentation binaire. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : tester un cas limite lié à caractère dans l’ASCII.
- Production attendue : le comportement de ASCII simple est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : classer deux méthodes possibles pour accent UTF-8.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Croire que tout caractère occupe un octet. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : justifier un transfert qui utilise chaîne mixte avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-BASE-05A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur flottant.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Séparer nom du caractère et encodage effectif. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 9
- Objectif travaillé : O1, O2, O3, O4.
- Capacité officielle : P-DATA-BASE-03.
- Énoncé disciplinaire : calculer la représentation en binaire de nombres réels simples par la méthode des multiplications successives. (9a) Convertir 0.75 en binaire. La représentation est-elle exacte ? (9b) Convertir 0.1 en binaire (5 premières étapes). Le développement est-il fini ? Quel est le résultat de `0.1 + 0.2` en Python ? (9c) Convertir 5.625 en binaire (partie entière + partie fractionnaire). (9d) Expliquer pourquoi `0.1 + 0.2 == 0.3` renvoie `False` en Python. Proposer une méthode correcte pour comparer deux flottants.
- Production attendue : 0.75₁₀ = 0.11₂ (exacte), 0.1₁₀ périodique infinie, 5.625₁₀ = 101.101₂ (exacte), comparaison par tolérance.
- Contrainte de contrôle : vérifier chaque conversion par recomposition (somme de puissances de 2).
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : `41` en hexadécimal.
- Contrôle : faire apparaître le contrôle « caractère dans l’ASCII ».
- Erreur traitée : EF1 - Compter les caractères au lieu des octets en UTF-8.
- Donnée utilisée alpha dans P03 td texte reels : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P03 td texte reels : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P03 td texte reels : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `c3 a9`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Croire que tout caractère occupe un octet.
- Donnée utilisée beta dans P03 td texte reels : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P03 td texte reels : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P03 td texte reels : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : 2 caractères et 3 octets.
- Contrôle : comparer avec le cas « chaîne vide ».
- Erreur traitée : EF3 - Comparer deux flottants avec égalité stricte après calcul.
- Donnée utilisée gamma dans P03 td texte reels : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P03 td texte reels : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P03 td texte reels : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : valeur proche de `0.3`.
- Contrôle : corriger l’erreur « Confondre point de code et représentation binaire. ».
- Erreur traitée : EF4 - Confondre point de code et représentation binaire.
- Donnée utilisée delta dans P03 td texte reels : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P03 td texte reels : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P03 td texte reels : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de ASCII simple est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Compter les caractères au lieu des octets en UTF-8.
- Donnée utilisée epsilon dans P03 td texte reels : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P03 td texte reels : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P03 td texte reels : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Croire que tout caractère occupe un octet. » est une erreur.
- Erreur traitée : EF2 - Croire que tout caractère occupe un octet.
- Donnée utilisée zeta dans P03 td texte reels : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P03 td texte reels : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P03 td texte reels : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Comparer deux flottants avec égalité stricte après calcul.
- Donnée utilisée eta dans P03 td texte reels : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P03 td texte reels : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P03 td texte reels : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Séparer nom du caractère et encodage effectif. ».
- Erreur traitée : EF4 - Confondre point de code et représentation binaire.
- Donnée utilisée theta dans P03 td texte reels : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P03 td texte reels : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P03 td texte reels : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P03 td texte reels : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 9
- Résultat : (9a) 0.75 × 2 = 1.5 → 1, reste 0.5 ; 0.5 × 2 = 1.0 → 1, reste 0. Donc 0.75₁₀ = 0.11₂. Exacte car 0.75 = 1/2 + 1/4. (9b) 0.1 × 2 = 0.2 → 0 ; 0.2 × 2 = 0.4 → 0 ; 0.4 × 2 = 0.8 → 0 ; 0.8 × 2 = 1.6 → 1, reste 0.6 ; 0.6 × 2 = 1.2 → 1, reste 0.2. Cycle infini : 0.1₁₀ = 0.00011…₂. En Python `0.1 + 0.2` donne `0.30000000000000004`. (9c) 5 = 101₂ ; 0.625 → 1, 0, 1 ; donc 5.625₁₀ = 101.101₂. Exacte. (9d) 0.1 et 0.2 sont arrondis en machine. Méthode correcte : `abs(a - b) < 1e-9`.
- Contrôle : chaque conversion vérifiée par recomposition (0.11₂ = 1/2 + 1/4 = 0.75).
- Erreur traitée : EF3 - Utiliser `==` au lieu d'une tolérance pour comparer des flottants issus de calculs binaires.

## Erreurs fréquentes
- Erreur fréquente EF1 - Compter les caractères au lieu des octets en UTF-8.
- Erreur fréquente EF2 - Croire que tout caractère occupe un octet.
- Erreur fréquente EF3 - Comparer deux flottants avec égalité stricte après calcul.
- Erreur fréquente EF4 - Confondre point de code et représentation binaire.

## Remédiation ciblée
- Activité corrective EF1 : Afficher la liste des octets avec `encode("utf-8")`.
- Activité corrective EF2 : Construire un tableau caractère, point de code, octets.
- Activité corrective EF3 : Utiliser une tolérance absolue et justifier son ordre de grandeur.
- Activité corrective EF4 : Séparer nom du caractère et encodage effectif.

## Différenciation
- Socle : traiter `A` avec une fiche méthode fournie.
- Standard : traiter `é` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « chaîne vide » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
