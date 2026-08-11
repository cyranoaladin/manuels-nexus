---
title: "T04 - Td - Récursivité"
level: "terminale"
sequence_id: "T04"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Langage et preuve de terminaison"
notion: "appel récursif, cas de base, terminaison, pile d’appels"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-LANG-02A"
    - "T-LANG-02B"
    - "T-LANG-04A"
---

# T04 - TD - Récursivité

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-LANG-02A
- T-LANG-02B

## Prérequis
- Reconnaître une consigne liée à appel récursif.
- Distinguer donnée, méthode et conclusion dans le thème Langage et preuve de terminaison.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T04-S1 à T04-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un algorithme de parcours doit traiter une structure définie en se ramenant à un sous-problème plus petit.

## Activité d’entrée
1. Identifier le cas de base d’une factorielle.
2. Suivre les appels de `somme([4, 1, 3])`.
3. Comparer récursif et itératif.
4. Prévoir ce qui se passe sans décroissance.

## Exemples corrigés précis
### Exemple corrigé 1 - factorielle
- Donnée étudiée : `4!`.
- Méthode : appliquer `n * fact(n-1)` jusqu’au cas `0!`.
- Résultat obtenu : `24`.
- Contrôle : le cas limite « entier négatif refusé » est vérifié séparément.
### Exemple corrigé 2 - somme de liste
- Donnée étudiée : `[4, 1, 3]`.
- Méthode : séparer tête et reste.
- Résultat obtenu : `8`.
- Contrôle : le cas limite « liste vide » est vérifié séparément.
### Exemple corrigé 3 - longueur
- Donnée étudiée : `["a", "b"]`.
- Méthode : ajouter 1 à la longueur du reste.
- Résultat obtenu : `2`.
- Contrôle : le cas limite « reste vide » est vérifié séparément.
### Exemple corrigé 4 - terminaison
- Donnée étudiée : `n` décroît vers 0.
- Méthode : montrer une mesure entière strictement décroissante.
- Résultat obtenu : preuve de terminaison.
- Contrôle : le cas limite « appel avec même argument » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : résoudre factorielle avec `4!`.
- Production attendue : `24`.
- Contrainte de contrôle : faire apparaître le contrôle « entier négatif refusé ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : expliquer somme de liste à partir de `[4, 1, 3]`.
- Production attendue : `8`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : comparer longueur avec `["a", "b"]`.
- Production attendue : `2`.
- Contrainte de contrôle : comparer avec le cas « reste vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : T-LANG-02A, T-LANG-02B.
- Énoncé disciplinaire : soit la fonction `def decompte(n): print(n); return decompte(n - 1)`. (a) Tracer les 4 premiers appels pour `decompte(3)` en indiquant la valeur de `n` à chaque appel. (b) Identifier le problème de terminaison (cas de base manquant). (c) Corriger la fonction en ajoutant un cas de base pour `n == 0`. (d) Donner le variant de terminaison (mesure entière strictement décroissante).
- Production attendue : trace `decompte(3)→n=3, decompte(2)→n=2, decompte(1)→n=1, decompte(0)→n=0` ; variant = `n` ; fonction corrigée avec `if n <= 0: return`.
- Contrainte de contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. » ; vérifier que `decompte(-1)` ne boucle pas.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : tester un cas limite lié à entier négatif refusé.
- Production attendue : le comportement de factorielle est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : classer deux méthodes possibles pour somme de liste.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : justifier un transfert qui utilise longueur avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : T-LANG-02A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur terminaison.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 9
- Objectif travaillé : O1, O2.
- Capacité officielle : T-LANG-04A.
- Énoncé disciplinaire : on donne trois implémentations de la somme d'une liste — impérative (boucle for), fonctionnelle (récursion sans variable mutable) et objet (méthode d'une classe ListeNombres). (9a) Identifier le paradigme de chaque version. (9b) Citer un trait distinctif de chaque paradigme visible dans le code. (9c) Laquelle risque de déborder la pile pour une liste de 10 000 éléments, et pourquoi ?
- Production attendue : impératif/fonctionnel/objet identifiés, traits (état mutable / récursion / encapsulation), récursion = pile.
- Contrainte de contrôle : chaque réponse justifiée par une référence au code.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.

## Corrigé
### Corrigé exercice 1
- Résultat : `24`.
- Contrôle : faire apparaître le contrôle « entier négatif refusé ».
- Erreur traitée : EF1 - Oublier le cas de base.
- Donnée utilisée alpha dans T04 td recursivite : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T04 td recursivite : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T04 td recursivite : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `8`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
- Donnée utilisée beta dans T04 td recursivite : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T04 td recursivite : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T04 td recursivite : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `2`.
- Contrôle : comparer avec le cas « reste vide ».
- Erreur traitée : EF3 - Confondre valeur retournée et affichage des appels.
- Donnée utilisée gamma dans T04 td recursivite : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T04 td recursivite : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T04 td recursivite : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : preuve de terminaison.
- Contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. ».
- Erreur traitée : EF4 - Ne pas traiter l’entrée vide.
- Donnée utilisée delta dans T04 td recursivite : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T04 td recursivite : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T04 td recursivite : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de factorielle est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Oublier le cas de base.
- Donnée utilisée epsilon dans T04 td recursivite : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T04 td recursivite : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T04 td recursivite : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur.
- Erreur traitée : EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
- Donnée utilisée zeta dans T04 td recursivite : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T04 td recursivite : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T04 td recursivite : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Confondre valeur retournée et affichage des appels.
- Donnée utilisée eta dans T04 td recursivite : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T04 td recursivite : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T04 td recursivite : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. ».
- Erreur traitée : EF4 - Ne pas traiter l’entrée vide.
- Donnée utilisée theta dans T04 td recursivite : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T04 td recursivite : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T04 td recursivite : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T04 td recursivite : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

### Corrigé exercice 9
- Résultat : (9a) boucle for = impératif, récursion = fonctionnel, classe = objet. (9b) Impératif : variable `total` mutée dans la boucle. Fonctionnel : pas de variable mutable, résultat construit par retour récursif. Objet : données et méthode encapsulées dans `ListeNombres`. (9c) La version récursive (fonctionnelle) risque `RecursionError` car Python n'optimise pas la récursion terminale.
- Contrôle : chaque paradigme justifié par citation du code source.
- Erreur traitée : confondre récursion (paradigme fonctionnel) et itération (paradigme impératif).

## Erreurs fréquentes
- Erreur fréquente EF1 - Oublier le cas de base.
- Erreur fréquente EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
- Erreur fréquente EF3 - Confondre valeur retournée et affichage des appels.
- Erreur fréquente EF4 - Ne pas traiter l’entrée vide.

## Remédiation ciblée
- Activité corrective EF1 : Encadrer le cas de base avant d’écrire l’appel récursif.
- Activité corrective EF2 : Tracer la valeur de l’argument à chaque appel.
- Activité corrective EF3 : Dessiner la pile d’appels avec valeurs de retour.
- Activité corrective EF4 : Tester d’abord la liste vide ou `n = 0`.

## Différenciation
- Socle : traiter `4!` avec une fiche méthode fournie.
- Standard : traiter `[4, 1, 3]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « reste vide » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
