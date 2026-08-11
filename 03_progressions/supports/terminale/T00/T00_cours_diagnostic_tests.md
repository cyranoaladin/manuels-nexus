---
title: "T00 - Cours - Diagnostic tests"
level: "terminale"
sequence_id: "T00"
document_type: "cours"
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

# T00 - Cours - Diagnostic tests

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

## Définitions et formalisation
- Définition D1 : fonction est utilisé dans Reprise Python et tests avec une donnée, une règle et un contrôle.
- Définition D2 : assertion est utilisé dans Reprise Python et tests avec une donnée, une règle et un contrôle.
- Définition D3 : cas limite est utilisé dans Reprise Python et tests avec une donnée, une règle et un contrôle.
- Définition D4 : spécification est utilisé dans Reprise Python et tests avec une donnée, une règle et un contrôle.
- Cas limite principal : liste d’un élément.

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
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-LANG-03A.
- Point de départ : `[3, 7, 2]`.
- Angle disciplinaire : repérage initial autour de maximum nominal.
- Démarche attendue : parcourir la liste en conservant le meilleur élément.
- Exemple associé : `7`.
- Point de vigilance : Tester seulement le cas donné en exemple.
- Activité de reprise associée : Construire un tableau cas nominal, limite, invalide.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-LANG-03A.
- Point de départ : `[]`.
- Angle disciplinaire : méthode guidée autour de liste vide.
- Démarche attendue : refuser l’entrée avant le parcours.
- Exemple associé : exception documentée.
- Point de vigilance : Écrire un test qui reproduit le code au lieu de la spécification.
- Activité de reprise associée : Formuler le résultat attendu en français avant le code du test.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-LANG-03A.
- Point de départ : `assert maximum([1]) == 1`.
- Angle disciplinaire : transfert argumenté autour de assertion.
- Démarche attendue : traduire une exigence en test exécutable.
- Exemple associé : test passant.
- Point de vigilance : Oublier le cas vide.
- Activité de reprise associée : Ajouter systématiquement une entrée minimale.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-LANG-03A.
- Point de départ : `[1, "x"]`.
- Angle disciplinaire : vérification critique autour de entrée invalide.
- Démarche attendue : définir si le mélange de types est autorisé.
- Exemple associé : erreur contrôlée.
- Point de vigilance : Ne pas lire le message d’échec.
- Activité de reprise associée : Réécrire le message d’échec comme diagnostic.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre maximum nominal avec `[3, 7, 2]` ; attendu : `7`.
- Exercice 2 : expliquer liste vide à partir de `[]` ; attendu : exception documentée.
- Exercice 3 : comparer assertion avec `assert maximum([1]) == 1` ; attendu : test passant.
- Exercice 4 : corriger entrée invalide pour `[1, "x"]` ; attendu : erreur contrôlée.
- Exercice 5 : tester un cas limite lié à liste d’un élément ; attendu : le comportement de maximum nominal est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste vide ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise assertion avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur entrée invalide ; attendu : l’erreur est localisée puis réparée.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7` ; résultat : `7` ; contrôle : faire apparaître le contrôle « liste d’un élément ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée ; résultat : exception documentée ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant ; résultat : test passant ; contrôle : comparer avec le cas « message utile en cas d’échec ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte ; résultat : erreur contrôlée ; contrôle : corriger l’erreur « Ne pas lire le message d’échec. ».
- Corrigé exercice 5 : méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7` ; résultat : le comportement de maximum nominal est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. ».
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre maximum nominal avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « liste d’un élément » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre liste vide avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « aucune valeur initiale » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre assertion avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « message utile en cas d’échec » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre entrée invalide avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « comparaison impossible » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier maximum nominal à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier liste vide à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier assertion à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier entrée invalide à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- fonction : terme à employer dans une justification écrite de la séquence.
- assertion : terme à employer dans une justification écrite de la séquence.
- cas limite : terme à employer dans une justification écrite de la séquence.
- spécification : terme à employer dans une justification écrite de la séquence.

## Utiliser des API ou bibliothèques

La capacité T-LANG-03A demande d'utiliser des API ou bibliothèques dans un programme. En Terminale, cela inclut l'exploration de modules standards et tiers, la lecture de leur documentation, et l'intégration dans un projet.

### Qu'est-ce qu'une API ?

Une **API** (Application Programming Interface) est un ensemble de fonctions, classes et protocoles exposés par une bibliothèque ou un service, permettant à un programme de l'utiliser sans connaître son implémentation interne. L'API est le **contrat d'interface** : elle spécifie les entrées attendues, les sorties produites, et les erreurs possibles.

### Exemple 1 — le module `csv` (bibliothèque standard)

```python
import csv

with open("notes.csv", "r", encoding="utf-8") as f:
    lecteur = csv.DictReader(f)
    for ligne in lecteur:
        print(f"{ligne['nom']} : {ligne['note']}")
```

L'API de `csv.DictReader` : prend un fichier ouvert en lecture, renvoie un itérable de dictionnaires (une clé par en-tête de colonne). Pas besoin de connaître le parsing interne.

### Exemple 2 — le module `json` (sérialisation)

```python
import json

donnees = {"eleve": "Alice", "moyenne": 15.5}
texte = json.dumps(donnees, ensure_ascii=False)
print(texte)  # '{"eleve": "Alice", "moyenne": 15.5}'

reconstitue = json.loads(texte)
print(reconstitue["eleve"])  # Alice
```

L'API expose `dumps` (dict → str) et `loads` (str → dict). Le format JSON est un standard d'échange — l'API masque le parsing.

### Exemple 3 — module tiers `requests` (HTTP)

```python
import requests

reponse = requests.get("https://api.exemple.com/donnees")
if reponse.status_code == 200:
    data = reponse.json()
    print(data)
```

L'API de `requests.get` : prend une URL, renvoie un objet `Response` avec `.status_code`, `.json()`, `.text`. L'utilisateur n'a pas besoin de gérer les sockets ni le protocole HTTP manuellement.

### Bonnes pratiques

1. **Lire la documentation** avant d'utiliser une fonction (`help()`, docstring, site officiel).
2. **Respecter les types** des paramètres (l'API le spécifie).
3. **Gérer les erreurs** (`try/except` pour les cas d'échec documentés).
4. **Ne pas dépendre de l'implémentation** : si l'API change en interne mais garde le même contrat, le code appelant continue de fonctionner.

### Cas limites

- Un module non installé lève `ModuleNotFoundError` à l'import.
- `json.loads` sur une chaîne malformée lève `json.JSONDecodeError`.
- `requests.get` sans réseau lève `requests.ConnectionError`.

## Analyse de variantes disciplinaires
- Variante T00-A : modifier la donnée du premier exemple de T00 - Cours - Diagnostic tests et conserver exactement la même méthode.
- Variante T00-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T00-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T00-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T00-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T00-F : construire une donnée minimale qui force une décision de méthode.
- Variante T00-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T00-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T00-I : relier une erreur fréquente à une activité corrective précise.
- Variante T00-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T00-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T00-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T00-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T00-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T00-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T00-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
