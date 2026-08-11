---
title: "P03 - Corrige - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "corrige"
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


# P03 - Corrigé professeur - Texte Unicode et nombres réels

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

## Méthode générale de correction
- Point 1 : pour ASCII simple, exiger la donnée `A`, la méthode « lire le point de code U+0041 puis son octet UTF-8 » et le contrôle « caractère dans l’ASCII ».
- Point 2 : pour accent UTF-8, exiger la donnée `é`, la méthode « distinguer un caractère et deux octets » et le contrôle « longueur en octets différente de la longueur en caractères ».
- Point 3 : pour chaîne mixte, exiger la donnée `Aé`, la méthode « additionner les tailles UTF-8 de chaque caractère » et le contrôle « chaîne vide ».
- Point 4 : pour flottant, exiger la donnée `0.1 + 0.2`, la méthode « comparer avec une tolérance au lieu de `==` » et le contrôle « arrondi binaire ».
## Exercices numérotés
- Exercice 1 : résoudre ASCII simple avec `A` ; attendu : `41` en hexadécimal.
- Exercice 2 : expliquer accent UTF-8 à partir de `é` ; attendu : `c3 a9`.
- Exercice 3 : comparer chaîne mixte avec `Aé` ; attendu : 2 caractères et 3 octets.
- Exercice 4 : corriger flottant pour `0.1 + 0.2` ; attendu : valeur proche de `0.3`.
- Exercice 5 : tester un cas limite lié à caractère dans l’ASCII ; attendu : le comportement de ASCII simple est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour accent UTF-8 ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise chaîne mixte avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur flottant ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `A`, appliquer la méthode « lire le point de code U+0041 puis son octet UTF-8 », puis écrire `41` en hexadécimal.
- Résultat : `41` en hexadécimal.
- Contrôle : faire apparaître le contrôle « caractère dans l’ASCII ».
- Erreur traitée : EF1 - Compter les caractères au lieu des octets en UTF-8.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de distinguer un caractère et deux octets avant de conclure par `c3 a9`.
- Résultat : `c3 a9`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Croire que tout caractère occupe un octet.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « chaîne vide » et valider 2 caractères et 3 octets.
- Résultat : 2 caractères et 3 octets.
- Contrôle : comparer avec le cas « chaîne vide ».
- Erreur traitée : EF3 - Comparer deux flottants avec égalité stricte après calcul.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Confondre point de code et représentation binaire. » puis reprendre la procédure correcte.
- Résultat : valeur proche de `0.3`.
- Contrôle : corriger l’erreur « Confondre point de code et représentation binaire. ».
- Erreur traitée : EF4 - Confondre point de code et représentation binaire.
### Corrigé exercice 5
- Méthode : identifier `A`, appliquer la méthode « lire le point de code U+0041 puis son octet UTF-8 », puis écrire `41` en hexadécimal.
- Résultat : le comportement de ASCII simple est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Compter les caractères au lieu des octets en UTF-8.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de distinguer un caractère et deux octets avant de conclure par `c3 a9`.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Croire que tout caractère occupe un octet. » est une erreur.
- Erreur traitée : EF2 - Croire que tout caractère occupe un octet.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « chaîne vide » et valider 2 caractères et 3 octets.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Comparer deux flottants avec égalité stricte après calcul.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Confondre point de code et représentation binaire. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Séparer nom du caractère et encodage effectif. ».
- Erreur traitée : EF4 - Confondre point de code et représentation binaire.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « caractère dans l’ASCII » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « chaîne vide » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Confondre point de code et représentation binaire. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Croire que tout caractère occupe un octet. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Séparer nom du caractère et encodage effectif. » ».
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
