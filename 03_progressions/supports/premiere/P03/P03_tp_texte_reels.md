---
title: "P03 - Tp - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "tp"
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


# P03 - TP - Texte Unicode et nombres réels

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

## Consigne technique détaillée
- Problème à programmer : Analyser une chaîne en code points, octets UTF-8 et comparaison numérique tolérante.
- Starter code : `code/P03_starter_texte_reels.py`.
- Tests attendus : `code/P03_tests_attendus_texte_reels.py`.
- Corrigé professeur séparé : `code/P03_corrige_professeur_texte_reels.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : caractère dans l’ASCII.
## Étapes de réalisation
- Étape 1 : coder ou tester ASCII simple à partir de `A`, puis contrôler caractère dans l’ASCII.
- Étape 2 : coder ou tester accent UTF-8 à partir de `é`, puis contrôler longueur en octets différente de la longueur en caractères.
- Étape 3 : coder ou tester chaîne mixte à partir de `Aé`, puis contrôler chaîne vide.
- Étape 4 : coder ou tester flottant à partir de `0.1 + 0.2`, puis contrôler arrondi binaire.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
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

## Validation opérationnelle du TP
- Vérification P03-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification P03-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification P03-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification P03-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification P03-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification P03-6 : comparer l’algorithme écrit avec la capacité officielle citée.
