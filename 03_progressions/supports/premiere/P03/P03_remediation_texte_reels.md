---
title: "P03 - Remediation - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "remediation"
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
---


# P03 - Remédiation - Texte Unicode et nombres réels

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05A

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

### Remédiation EF1
- Erreur fréquente EF1 - Compter les caractères au lieu des octets en UTF-8.
- Diagnostic : refaire ASCII simple avec `A` et repérer l’étape fautive.
- Activité corrective EF1 : Afficher la liste des octets avec `encode("utf-8")`.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « caractère dans l’ASCII ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF2
- Erreur fréquente EF2 - Croire que tout caractère occupe un octet.
- Diagnostic : refaire accent UTF-8 avec `é` et repérer l’étape fautive.
- Activité corrective EF2 : Construire un tableau caractère, point de code, octets.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « longueur en octets différente de la longueur en caractères ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF3
- Erreur fréquente EF3 - Comparer deux flottants avec égalité stricte après calcul.
- Diagnostic : refaire chaîne mixte avec `Aé` et repérer l’étape fautive.
- Activité corrective EF3 : Utiliser une tolérance absolue et justifier son ordre de grandeur.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « chaîne vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF4
- Erreur fréquente EF4 - Confondre point de code et représentation binaire.
- Diagnostic : refaire flottant avec `0.1 + 0.2` et repérer l’étape fautive.
- Activité corrective EF4 : Séparer nom du caractère et encodage effectif.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « arrondi binaire ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
## Exercices numérotés
- Exercice 1 : résoudre ASCII simple avec `A` ; attendu : `41` en hexadécimal.
- Exercice 2 : expliquer accent UTF-8 à partir de `é` ; attendu : `c3 a9`.
- Exercice 3 : comparer chaîne mixte avec `Aé` ; attendu : 2 caractères et 3 octets.
- Exercice 4 : corriger flottant pour `0.1 + 0.2` ; attendu : valeur proche de `0.3`.
- Exercice 5 : tester un cas limite lié à caractère dans l’ASCII ; attendu : le comportement de ASCII simple est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour accent UTF-8 ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise chaîne mixte avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur flottant ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `A`, appliquer la méthode « lire le point de code U+0041 puis son octet UTF-8 », puis écrire `41` en hexadécimal ; résultat : `41` en hexadécimal ; contrôle : faire apparaître le contrôle « caractère dans l’ASCII ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de distinguer un caractère et deux octets avant de conclure par `c3 a9` ; résultat : `c3 a9` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « chaîne vide » et valider 2 caractères et 3 octets ; résultat : 2 caractères et 3 octets ; contrôle : comparer avec le cas « chaîne vide ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Confondre point de code et représentation binaire. » puis reprendre la procédure correcte ; résultat : valeur proche de `0.3` ; contrôle : corriger l’erreur « Confondre point de code et représentation binaire. ».
- Corrigé exercice 5 : méthode : identifier `A`, appliquer la méthode « lire le point de code U+0041 puis son octet UTF-8 », puis écrire `41` en hexadécimal ; résultat : le comportement de ASCII simple est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de distinguer un caractère et deux octets avant de conclure par `c3 a9` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Croire que tout caractère occupe un octet. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « chaîne vide » et valider 2 caractères et 3 octets ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Confondre point de code et représentation binaire. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Séparer nom du caractère et encodage effectif. ».

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
