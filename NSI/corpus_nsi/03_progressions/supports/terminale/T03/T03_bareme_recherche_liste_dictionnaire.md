---
title: "T03 - barème - Recherche dans liste et dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "bareme"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "recherche, liste, dictionnaire, index, clé, complexité"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03C"
---

# T03 - Barème - Recherche dans liste et dictionnaire

## Objectifs

- Vérifier la compréhension des mécanismes de recherche dans une liste et un dictionnaire.
- Évaluer la maîtrise des ordres de grandeur de complexité pour chaque structure.
- Contrôler la capacité à choisir la structure adaptée et à tester la recherche.

## Capacités officielles

- T-STRUCT-03C : Rechercher un élément dans une liste ou un dictionnaire et analyser la complexité de l'opération.

## Prérequis

- Connaître le parcours séquentiel d'une liste (boucle for, index).
- Savoir accéder à une valeur par clé dans un dictionnaire (d[cle]).
- Comprendre la notion de complexité temporelle (O(1), O(n), O(n log n)).
- Maîtriser l'opérateur in pour les listes et les dictionnaires en Python.

## Situation-problème

Un administrateur système doit rechercher un utilisateur parmi 100 000 comptes. Il dispose des données soit sous forme de liste de tuples (nom, id), soit sous forme de dictionnaire {nom: id}. Il doit choisir la structure la plus adaptée et justifier son choix par la complexité de la recherche. Le barème guide l'évaluation de cette compétence.

## Activité d’entrée

Mesurer le temps de recherche d'un élément dans une liste de 10 000 éléments puis dans un dictionnaire de 10 000 clés, et comparer les résultats.

## Exemple

Liste : noms = ["Alice", "Bob", "Charlie"]. Recherche "Bob" par parcours séquentiel : 2 comparaisons, complexité O(n). Dictionnaire : comptes = {"Alice": 1, "Bob": 2, "Charlie": 3}. Recherche "Bob" par clé : accès direct, complexité O(1) en moyenne.

## Barème question par question

### Barème question 1 — Mécanismes de recherche et complexité (T-STRUCT-03C) — 5 points
- 1.a) Recherche dans une liste : 2 points (1 pt algorithme de parcours séquentiel correct avec boucle for et comparaison, 1 pt complexité O(n) dans le pire cas avec justification).
- 1.b) Recherche dans un dictionnaire : 2 points (1 pt accès par clé en O(1) amorti grâce à la table de hachage, 1 pt explication du mécanisme de hachage en une phrase).
- 1.c) Comparaison : 1 point (tableau comparatif liste vs dictionnaire pour la recherche : O(n) vs O(1), avec mention du coût mémoire supplémentaire du dictionnaire).

### Barème question 2 — Ordres de grandeur et choix de structure (T-STRUCT-03C) — 5 points
- 2.a) Ordres de grandeur : 2 points (1 pt estimation du nombre d'opérations pour n = 1 000, 10 000 et 100 000 en recherche séquentielle, 1 pt confirmation que le dictionnaire reste en O(1) quelle que soit la taille).
- 2.b) Solution adaptée : 2 points (1 pt choix du dictionnaire justifié pour les recherches fréquentes sur de grands ensembles, 1 pt identification d'un cas où la liste est préférable : données ordonnées avec recherche dichotomique ou faible nombre de recherches).
- 2.c) Conversion liste → dictionnaire : 1 point (code Python correct transformant une liste de tuples (cle, valeur) en dictionnaire avec dict() ou compréhension, et mention de la complexité O(n) de cette conversion).

### Barème question 3 — Tests et correction (T-STRUCT-03C) — 5 points
- 3.a) Tests de recherche : 2 points (1 pt test recherche d'un élément présent avec assert et résultat attendu, 1 pt test recherche d'un élément absent avec gestion de KeyError ou retour None).
- 3.b) Correction d'erreur : 2 points (1 pt identification de l'erreur dans un code de recherche donné (par exemple utilisation de == au lieu de in, ou index hors bornes), 1 pt correction fonctionnelle avec justification).
- 3.c) Valeurs par défaut : 1 point (utilisation de dict.get(cle, defaut) pour éviter KeyError, avec test assert vérifiant le comportement sur clé absente).

### Barème question 4 — Implémentation et mesure expérimentale (T-STRUCT-03C) — 5 points
- 4.a) Implémentation recherche liste : 2 points (1 pt boucle parcourant la liste avec comparaison, 1 pt retour correct de l'indice ou None si absent).
- 4.b) Mesure expérimentale : 2 points (1 pt utilisation de time.time() ou timeit pour mesurer les deux recherches, 1 pt tableau comparatif avec n = 1 000, 10 000, 100 000 et commentaire du rapport).
- 4.c) Cas clé mutable : 1 point (explication qu'une liste ne peut pas être clé de dictionnaire car non hashable, avec test levant TypeError).

## Total : 20 points

## Critères de réussite observables
- Les complexités sont correctement identifiées et justifiées pour chaque structure.
- Le code Python est exécutable et les assertions passent sans erreur.
- Le choix de la structure de données est argumenté en fonction du contexte.

## Erreurs fréquentes
- Croire que la recherche dans un dictionnaire est en O(n) comme dans une liste.
- Confondre la recherche par clé (O(1)) et la recherche par valeur (O(n)) dans un dictionnaire.
- Oublier de gérer le cas où la clé est absente (KeyError non attrapé).
- Utiliser index() sur une liste sans vérifier la présence de l'élément (ValueError).
- Ne pas distinguer le coût de construction d'un dictionnaire O(n) et le coût d'une recherche O(1).

## Exercices

Les exercices évalués sont les questions 1 à 3 de l'évaluation recherche dans liste et dictionnaire T03.

## Corrigé

Les réponses détaillées se trouvent dans T03_corrige_recherche_liste_dictionnaire.md.

## Remédiation

En cas de score inférieur à 8/15, reprendre la recherche séquentielle dans une petite liste (5 éléments) avec traçage pas à pas avant de passer au dictionnaire.

## Différenciation

- Socle : question 1a-1b (mécanismes de base de la recherche dans liste et dictionnaire).
- Standard : question 2 (ordres de grandeur et choix de structure justifié).
- Expert : question 3b (correction d'erreur dans un code de recherche donné).

## Séance(s) correspondante(s)

Séance dédiée à la recherche dans les structures linéaires et les tables associatives.
