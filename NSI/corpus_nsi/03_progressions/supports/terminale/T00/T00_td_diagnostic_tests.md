---
title: "T00 - Td - Diagnostic tests"
level: "terminale"
sequence_id: "T00"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Reprise Python et tests"
notion: "fonction, assertion, cas limite, spécification"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
---

# T00 - TD - Diagnostic tests

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-LANG-03A

## Prérequis
- Reconnaître une consigne liée à fonction.
- Distinguer donnée, méthode et conclusion dans le thème Reprise Python et tests.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T00-S1 à T00-S4 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une équipe reprend une bibliothèque Python de Première et doit écrire des tests avant de modifier le code.

## Activité d’entrée
1. Écrire le résultat attendu pour une fonction `maximum`.
2. Choisir un cas nominal, un cas limite et un cas invalide.
3. Distinguer spécification et implémentation.
4. Lire un message d’assertion échouée.

## Exemples corrigés précis
### Exemple corrigé 1 - maximum nominal
- Donnée étudiée : `[3, 7, 2]`.
- Méthode : parcourir la liste en conservant le meilleur élément.
- Résultat obtenu : `7`.
- Contrôle : le cas limite « liste d’un élément » est vérifié séparément.
### Exemple corrigé 2 - liste vide
- Donnée étudiée : `[]`.
- Méthode : refuser l’entrée avant le parcours.
- Résultat obtenu : exception documentée.
- Contrôle : le cas limite « aucune valeur initiale » est vérifié séparément.
### Exemple corrigé 3 - assertion
- Donnée étudiée : `assert maximum([1]) == 1`.
- Méthode : traduire une exigence en test exécutable.
- Résultat obtenu : test passant.
- Contrôle : le cas limite « message utile en cas d’échec » est vérifié séparément.
### Exemple corrigé 4 - entrée invalide
- Donnée étudiée : `[1, "x"]`.
- Méthode : définir si le mélange de types est autorisé.
- Résultat obtenu : erreur contrôlée.
- Contrôle : le cas limite « comparaison impossible » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : résoudre maximum nominal avec `[3, 7, 2]`.
- Production attendue : `7`.
- Contrainte de contrôle : faire apparaître le contrôle « liste d’un élément ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : expliquer liste vide à partir de `[]`.
- Production attendue : exception documentée.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : comparer assertion avec `assert maximum([1]) == 1`.
- Production attendue : test passant.
- Contrainte de contrôle : comparer avec le cas « message utile en cas d’échec ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : corriger entrée invalide pour `[1, "x"]`.
- Production attendue : erreur contrôlée.
- Contrainte de contrôle : corriger l’erreur « Ne pas lire le message d’échec. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : tester un cas limite lié à liste d’un élément.
- Production attendue : le comportement de maximum nominal est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : classer deux méthodes possibles pour liste vide.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : justifier un transfert qui utilise assertion avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur entrée invalide.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 9
- Objectif travaillé : O1, O2, O3, O4.
- Capacité officielle : T-LANG-03A.
- Énoncé disciplinaire : utiliser le module `json` pour lire et écrire des données structurées. (9a) Écrire un programme qui crée un dictionnaire `eleve = {"nom": "Alice", "notes": [15, 12, 18]}`, le sérialise en chaîne JSON avec `json.dumps`, puis le reconstitue avec `json.loads`. Vérifier que le dictionnaire reconstitué est identique à l'original. (9b) Écrire un programme qui lit un fichier `eleves.json` contenant une liste de dictionnaires et affiche le nom de chaque élève. Gérer le cas où le fichier n'existe pas (`FileNotFoundError`). (9c) Que se passe-t-il si on appelle `json.loads` sur une chaîne malformée `"{nom: Alice}"` ? Quelle exception est levée ?
- Production attendue : (9a) sérialisation/désérialisation vérifiée ; (9b) lecture fichier avec gestion d'erreur ; (9c) `json.JSONDecodeError`.
- Contrainte de contrôle : chaque appel d'API utilise les paramètres documentés ; cas d'erreur géré.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.

## Corrigé
### Corrigé exercice 1
- Résultat : `7`.
- Contrôle : faire apparaître le contrôle « liste d’un élément ».
- Erreur traitée : EF1 - Tester seulement le cas donné en exemple.
- Donnée utilisée alpha dans T00 td diagnostic tests : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T00 td diagnostic tests : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : exception documentée.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
- Donnée utilisée beta dans T00 td diagnostic tests : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T00 td diagnostic tests : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : test passant.
- Contrôle : comparer avec le cas « message utile en cas d’échec ».
- Erreur traitée : EF3 - Oublier le cas vide.
- Donnée utilisée gamma dans T00 td diagnostic tests : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T00 td diagnostic tests : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : erreur contrôlée.
- Contrôle : corriger l’erreur « Ne pas lire le message d’échec. ».
- Erreur traitée : EF4 - Ne pas lire le message d’échec.
- Donnée utilisée delta dans T00 td diagnostic tests : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T00 td diagnostic tests : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de maximum nominal est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Tester seulement le cas donné en exemple.
- Donnée utilisée epsilon dans T00 td diagnostic tests : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T00 td diagnostic tests : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur.
- Erreur traitée : EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
- Donnée utilisée zeta dans T00 td diagnostic tests : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T00 td diagnostic tests : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Oublier le cas vide.
- Donnée utilisée eta dans T00 td diagnostic tests : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T00 td diagnostic tests : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. ».
- Erreur traitée : EF4 - Ne pas lire le message d’échec.
- Donnée utilisée theta dans T00 td diagnostic tests : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T00 td diagnostic tests : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T00 td diagnostic tests : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T00 td diagnostic tests : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

### Corrigé exercice 9
- Résultat : (9a) `json.dumps(eleve)` → `'{"nom": "Alice", "notes": [15, 12, 18]}'` ; `json.loads(texte)` → dictionnaire identique. (9b) `with open("eleves.json") as f: data = json.load(f)` avec `except FileNotFoundError`. (9c) `json.loads('"{nom: Alice}"')` lève `json.JSONDecodeError` car la chaîne n'est pas du JSON valide (clés non entre guillemets).
- Contrôle : API documentée utilisée correctement, exception gérée.
- Erreur traitée : EF1 - Tester seulement le cas donné en exemple (ici : tester aussi le cas d'erreur).
- Donnée utilisée iota dans T00 td diagnostic tests : cas iota de l'exercice 9 avec le module json.
- Méthode iota dans T00 td diagnostic tests : import json, appel dumps/loads, gestion d'erreur try/except.
- Résultat iota dans T00 td diagnostic tests : sérialisation/désérialisation vérifiée, exception identifiée.
- Contrôle iota dans T00 td diagnostic tests : le cas limite « chaîne JSON malformée → JSONDecodeError » est vérifié.

## Erreurs fréquentes
- Erreur fréquente EF1 - Tester seulement le cas donné en exemple.
- Erreur fréquente EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
- Erreur fréquente EF3 - Oublier le cas vide.
- Erreur fréquente EF4 - Ne pas lire le message d’échec.

## Remédiation ciblée
- Activité corrective EF1 : Construire un tableau cas nominal, limite, invalide.
- Activité corrective EF2 : Formuler le résultat attendu en français avant le code du test.
- Activité corrective EF3 : Ajouter systématiquement une entrée minimale.
- Activité corrective EF4 : Réécrire le message d’échec comme diagnostic.

## Différenciation
- Socle : traiter `[3, 7, 2]` avec une fiche méthode fournie.
- Standard : traiter `[]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « message utile en cas d’échec » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
