---
title: "T04 - Cours - Récursivité"
level: "terminale"
sequence_id: "T04"
document_type: "cours"
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
---

# T04 - Cours - Récursivité

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

## Définitions et formalisation
- Définition D1 : appel récursif est utilisé dans Langage et preuve de terminaison avec une donnée, une règle et un contrôle.
- Définition D2 : cas de base est utilisé dans Langage et preuve de terminaison avec une donnée, une règle et un contrôle.
- Définition D3 : terminaison est utilisé dans Langage et preuve de terminaison avec une donnée, une règle et un contrôle.
- Définition D4 : pile d’appels est utilisé dans Langage et preuve de terminaison avec une donnée, une règle et un contrôle.
- Cas limite principal : entier négatif refusé.

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
## Méthode — analyser un appel récursif

Pour analyser le fonctionnement d'un programme récursif (T-LANG-02B) :

1. **Identifier le cas de base** : quelle condition arrête la récursion ?
2. **Tracer les appels** : suivre la pile d'appels avec les valeurs d'arguments à chaque niveau. Exemple : `somme([4, 1, 3])` → `4 + somme([1, 3])` → `4 + 1 + somme([3])` → `4 + 1 + 3 + somme([])` → `4 + 1 + 3 + 0 = 8`.
3. **Prouver la terminaison** : exhiber un variant (mesure entière positive strictement décroissante à chaque appel). Si le variant est `n`, montrer que chaque appel récursif diminue `n` d'au moins 1.
4. **Compter les appels** : le nombre d'appels récursifs de `fact(n)` est `n`, celui de `somme(lst)` est `len(lst)`.

### Exemple corrigé 4 - terminaison
- Donnée étudiée : `n` décroît vers 0.
- Méthode : montrer une mesure entière strictement décroissante.
- Résultat obtenu : preuve de terminaison.
- Contrôle : le cas limite « appel avec même argument » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-LANG-02A.
- Point de départ : `4!`.
- Angle disciplinaire : repérage initial autour de factorielle.
- Démarche attendue : appliquer `n * fact(n-1)` jusqu’au cas `0!`.
- Exemple associé : `24`.
- Point de vigilance : Oublier le cas de base.
- Activité de reprise associée : Encadrer le cas de base avant d’écrire l’appel récursif.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-LANG-02A.
- Point de départ : `[4, 1, 3]`.
- Angle disciplinaire : méthode guidée autour de somme de liste.
- Démarche attendue : séparer tête et reste.
- Exemple associé : `8`.
- Point de vigilance : Faire un appel récursif qui ne rapproche pas du cas de base.
- Activité de reprise associée : Tracer la valeur de l’argument à chaque appel.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-LANG-02A.
- Point de départ : `["a", "b"]`.
- Angle disciplinaire : transfert argumenté autour de longueur.
- Démarche attendue : ajouter 1 à la longueur du reste.
- Exemple associé : `2`.
- Point de vigilance : Confondre valeur retournée et affichage des appels.
- Activité de reprise associée : Dessiner la pile d’appels avec valeurs de retour.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-LANG-02A.
- Point de départ : `n` décroît vers 0.
- Angle disciplinaire : vérification critique autour de terminaison.
- Démarche attendue : montrer une mesure entière strictement décroissante.
- Exemple associé : preuve de terminaison.
- Point de vigilance : Ne pas traiter l’entrée vide.
- Activité de reprise associée : Tester d’abord la liste vide ou `n = 0`.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre factorielle avec `4!` ; attendu : `24`.
- Exercice 2 : expliquer somme de liste à partir de `[4, 1, 3]` ; attendu : `8`.
- Exercice 3 : comparer longueur avec `["a", "b"]` ; attendu : `2`.
- Exercice 4 : corriger terminaison pour `n` décroît vers 0 ; attendu : preuve de terminaison.
- Exercice 5 : tester un cas limite lié à entier négatif refusé ; attendu : le comportement de factorielle est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour somme de liste ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise longueur avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur terminaison ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24` ; résultat : `24` ; contrôle : faire apparaître le contrôle « entier négatif refusé ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8` ; résultat : `8` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « reste vide » et valider `2` ; résultat : `2` ; contrôle : comparer avec le cas « reste vide ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte ; résultat : preuve de terminaison ; contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. ».
- Corrigé exercice 5 : méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24` ; résultat : le comportement de factorielle est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « reste vide » et valider `2` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. ».
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre factorielle avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « entier négatif refusé » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre somme de liste avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « liste vide » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre longueur avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « reste vide » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre terminaison avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « appel avec même argument » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier factorielle à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier somme de liste à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier longueur à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier terminaison à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- appel récursif : terme à employer dans une justification écrite de la séquence.
- cas de base : terme à employer dans une justification écrite de la séquence.
- terminaison : terme à employer dans une justification écrite de la séquence.
- pile d’appels : terme à employer dans une justification écrite de la séquence.

## Paradigmes de programmation — impératif, fonctionnel, objet

La capacité T-LANG-04A demande de distinguer sur des exemples les paradigmes impératif, fonctionnel et objet.

### Le même problème en trois paradigmes

Problème : calculer la somme des éléments d'une liste.

**Impératif** (Python, boucle avec état mutable) :
```python
def somme_imperatif(lst):
    total = 0
    for x in lst:
        total += x
    return total
```

**Fonctionnel** (Python, récursion sans état mutable) :
```python
def somme_fonctionnel(lst):
    if not lst:
        return 0
    return lst[0] + somme_fonctionnel(lst[1:])
```

**Objet** (Python, encapsulation dans une classe) :
```python
class ListeNombres:
    def __init__(self, valeurs):
        self.valeurs = valeurs

    def somme(self):
        total = 0
        for x in self.valeurs:
            total += x
        return total
```

### Traits distinctifs

| Paradigme | Unité de base | État | Contrôle de flux |
|-----------|--------------|------|-----------------|
| Impératif | Instruction | Mutable (variables modifiées) | Boucles, conditions |
| Fonctionnel | Fonction | Immutable (pas d'effet de bord) | Récursion, composition |
| Objet | Objet (données + méthodes) | Encapsulé (attributs privés) | Messages entre objets |

### Cas limites

- Python est **multi-paradigme** : on peut mélanger les trois styles dans un même programme.
- La récursion (fonctionnel) a une limite de profondeur en Python : chaque appel empile un cadre d'appel, et au-delà de ~1000 appels imbriqués, Python lève `RecursionError`.
- Un paradigme n'est pas intrinsèquement supérieur — le choix dépend du problème.

## Analyse de variantes disciplinaires
- Variante T04-A : modifier la donnée du premier exemple de T04 - Cours - Récursivité et conserver exactement la même méthode.
- Variante T04-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T04-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T04-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T04-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T04-F : construire une donnée minimale qui force une décision de méthode.
- Variante T04-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T04-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T04-I : relier une erreur fréquente à une activité corrective précise.
- Variante T04-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T04-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T04-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T04-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T04-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T04-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T04-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
