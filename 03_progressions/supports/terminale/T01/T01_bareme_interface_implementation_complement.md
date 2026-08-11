---
title: "T01 - barème - Interface et implémentation complément"
level: "terminale"
sequence_id: "T01"
document_type: "bareme"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures de données abstraites"
notion: "interface, implémentation, pile, file, liste chaînée, tableau"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-01B"
    - "T-STRUCT-01C"
---

# T01 - Barème - Interface et implémentation complément

## Objectifs

- Vérifier la distinction entre interface (spécification) et implémentation (réalisation).
- Évaluer la capacité à implémenter une pile chaînée avec tests LIFO.
- Contrôler la compréhension des tests de file FIFO et des cas limites.
- Apprécier le choix raisonné d'une implémentation selon le contexte.

## Capacités officielles

- T-STRUCT-01B : Distinguer interface et implémentation, et implémenter une structure avec une interface donnée.
- T-STRUCT-01C : Écrire des tests pour vérifier qu'une implémentation respecte l'interface.

## Prérequis

- Connaître les notions de pile (LIFO) et file (FIFO).
- Maîtriser la programmation orientée objet en Python (class, __init__, méthodes).
- Savoir écrire des assertions ou des tests simples avec assert.
- Comprendre la notion de liste chaînée (maillon, pointeur suivant).

## Situation-problème

Un chef de projet demande à deux développeurs d'implémenter la même interface de pile : l'un utilise un tableau Python, l'autre une liste chaînée. Le chef doit vérifier que les deux implémentations respectent le même contrat (interface) en écrivant une batterie de tests commune. Le barème guide l'évaluation de cette compétence.

## Activité d’entrée

Lister les opérations de l'interface d'une pile (empiler, depiler, est_vide, sommet) et expliquer pourquoi deux implémentations différentes peuvent offrir le même comportement.

## Exemple

Interface Pile : empiler(x), depiler() → x, est_vide() → bool, sommet() → x. Implémentation par tableau : self.donnees = []. Implémentation chaînée : self.tete = None avec des maillons. Les deux passent le même test : empiler(1), empiler(2), assert depiler() == 2.

## Barème question par question

### Barème question 1 — Interface vs implémentation (T-STRUCT-01B) — 5 points
- 1.a) Définition interface : 2 points (1 pt l'interface décrit les opérations disponibles sans détail interne, 1 pt exemple concret avec signature des méthodes).
- 1.b) Définition implémentation : 2 points (1 pt l'implémentation est le code concret qui réalise l'interface, 1 pt mention de la structure de données interne choisie).
- 1.c) Intérêt de la séparation : 1 point (explication que l'on peut changer d'implémentation sans modifier le code utilisateur, avec exemple).

### Barème question 2 — PileChainee + test LIFO (T-STRUCT-01B, T-STRUCT-01C) — 5 points
- 2.a) Classe Maillon : 1 point (attributs valeur et suivant, __init__ correct).
- 2.b) Classe PileChainee : 2 points (1 pt empiler crée un maillon et met à jour la tête, 1 pt depiler retourne la valeur du sommet et avance la tête).
- 2.c) Test LIFO : 1 point (empiler 3 valeurs puis depiler dans l'ordre inverse vérifié par assert).
- 2.d) est_vide et sommet : 1 point (est_vide retourne self.tete is None, sommet retourne self.tete.valeur sans modifier la pile).

### Barème question 3 — Tests FIFO et cas limites (T-STRUCT-01C) — 5 points
- 3.a) Test FIFO : 2 points (1 pt enfiler 3 valeurs puis défiler dans le même ordre, 1 pt assertions correctes sur chaque valeur défilée).
- 3.b) Cas limite pile/file vide : 2 points (1 pt test que depiler/défiler sur structure vide lève une exception, 1 pt type d'exception approprié : IndexError ou ValueError).
- 3.c) Généricité des tests : 1 point (les tests fonctionnent indifféremment sur PileTableau ou PileChainee grâce à l'interface commune, avec démonstration).

### Barème question 4 — Choix d'implémentation (T-STRUCT-01B, T-STRUCT-01C) — 5 points
- 4.a) Critères de choix : 2 points (1 pt complexité temporelle des opérations, 1 pt consommation mémoire et contraintes du contexte).
- 4.b) Tests comparatifs : 2 points (1 pt même batterie de tests appliquée aux deux implémentations, 1 pt résultats identiques confirmant le respect de l'interface).
- 4.c) Mauvaise pratique : 1 point (identification d'une violation de l'interface : accès direct à self.donnees ou self.tete depuis le code utilisateur, avec explication du risque).

## Total : 20 points

## Critères de réussite observables
- Les classes Python sont syntaxiquement correctes et exécutables.
- Les tests utilisent uniquement les méthodes de l'interface, jamais les attributs internes.
- Au moins un cas limite (structure vide) est testé avec gestion d'exception.

## Erreurs fréquentes
- Confondre interface et implémentation (décrire le code interne comme interface).
- Oublier de mettre à jour le pointeur tête lors du depiler dans une pile chaînée.
- Ne pas tester le cas de la pile ou file vide (depiler/défiler sans vérification).
- Accéder directement aux attributs internes dans les tests au lieu d'utiliser les méthodes.
- Confondre LIFO (pile) et FIFO (file) dans les assertions.

## Exercices

Les exercices évalués sont les questions 1 à 4 de l'évaluation interface et implémentation complément T01.

## Corrigé

Les réponses détaillées se trouvent dans T01_corrige_interface_implementation_complement.md.

## Remédiation

En cas de score inférieur à 10/20, reprendre l'implémentation d'une pile par tableau avec des tests simples avant de passer à l'implémentation chaînée.

## Différenciation

- Socle : question 1 (distinction interface / implémentation avec définitions).
- Standard : questions 2 et 3 (implémentation chaînée et tests FIFO).
- Expert : question 4c (identification de mauvaises pratiques violant l'encapsulation).

## Séance(s) correspondante(s)

Séance dédiée aux structures de données abstraites : interface et implémentation (complément).
