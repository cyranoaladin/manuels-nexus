---
title: "P03 - Cours - Texte Unicode et nombres réels"
level: "premiere"
sequence_id: "P03"
document_type: "cours"
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

# P03 - Cours - Texte Unicode et nombres réels

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

## Définitions et formalisation
- Définition D1 : Unicode est utilisé dans Données textuelles et approximation avec une donnée, une règle et un contrôle.
- Définition D2 : UTF-8 est utilisé dans Données textuelles et approximation avec une donnée, une règle et un contrôle.
- Définition D3 : octet est utilisé dans Données textuelles et approximation avec une donnée, une règle et un contrôle.
- Définition D4 : flottant est utilisé dans Données textuelles et approximation avec une donnée, une règle et un contrôle.
- Cas limite principal : caractère dans l’ASCII.

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
## Représentation approximative des nombres réels

La capacité P-DATA-BASE-03 demande de calculer sur quelques exemples la représentation de nombres réels simples. Aucune connaissance précise d'IEEE-754 n'est exigible ; l'essentiel est de comprendre le principe de la représentation en virgule flottante et ses conséquences pratiques.

### Principe de la virgule flottante

Un nombre réel est stocké sous la forme `± m × 2^e`, où `m` (mantisse) est un nombre entre 1 et 2 et `e` (exposant) est un entier relatif. Comme la mantisse est stockée sur un nombre fini de bits, la représentation est **approximative** pour la plupart des nombres décimaux.

### Exemple corrigé 5 — Conversion de 0.75 en binaire

Méthode par multiplications successives de la partie fractionnaire :

```
0.75 × 2 = 1.5  → bit 1, reste 0.5
0.5  × 2 = 1.0  → bit 1, reste 0.0
```

Résultat : 0.75₁₀ = 0.11₂ = 1.1₂ × 2⁻¹. La représentation est **exacte** en binaire.

### Exemple corrigé 6 — Conversion de 0.1 en binaire

```
0.1 × 2 = 0.2  → bit 0
0.2 × 2 = 0.4  → bit 0
0.4 × 2 = 0.8  → bit 0
0.8 × 2 = 1.6  → bit 1, reste 0.6
0.6 × 2 = 1.2  → bit 1, reste 0.2
0.2 × 2 = 0.4  → bit 0  (cycle reprend)
```

Résultat : 0.1₁₀ = 0.0001100110011…₂ — développement binaire **infini périodique**. La machine tronque après un nombre fixe de bits, d'où l'erreur d'arrondi.

Vérification en Python :

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

### Exemple corrigé 7 — Conversion de 5.625 en binaire

Partie entière : 5₁₀ = 101₂.

Partie fractionnaire :

```
0.625 × 2 = 1.25  → bit 1, reste 0.25
0.25  × 2 = 0.5   → bit 0
0.5   × 2 = 1.0   → bit 1, reste 0.0
```

Résultat : 5.625₁₀ = 101.101₂ = 1.01101₂ × 2². Représentation **exacte**.

### Exemple corrigé 8 — Conséquence pratique : comparaison de flottants

Ne jamais tester l'égalité exacte entre flottants. Utiliser une tolérance :

```python
a = 0.1 + 0.2
b = 0.3
# Mauvais : if a == b
# Correct :
if abs(a - b) < 1e-9:
    print("Égaux à la précision machine")
```

### Cas limites des flottants

- 0.75 et 0.5 sont représentables exactement (sommes de puissances négatives de 2).
- 0.1, 0.2 et 0.3 ne le sont pas (développement binaire infini).
- L'accumulation d'erreurs d'arrondi peut fausser un calcul itératif.

## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-DATA-BASE-05A.
- Point de départ : `A`.
- Angle disciplinaire : repérage initial autour de ASCII simple.
- Démarche attendue : lire le point de code U+0041 puis son octet UTF-8.
- Exemple associé : `41` en hexadécimal.
- Point de vigilance : Compter les caractères au lieu des octets en UTF-8.
- Activité de reprise associée : Afficher la liste des octets avec `encode("utf-8")`.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-DATA-BASE-05A.
- Point de départ : `é`.
- Angle disciplinaire : méthode guidée autour de accent UTF-8.
- Démarche attendue : distinguer un caractère et deux octets.
- Exemple associé : `c3 a9`.
- Point de vigilance : Croire que tout caractère occupe un octet.
- Activité de reprise associée : Construire un tableau caractère, point de code, octets.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-DATA-BASE-05A.
- Point de départ : `Aé`.
- Angle disciplinaire : transfert argumenté autour de chaîne mixte.
- Démarche attendue : additionner les tailles UTF-8 de chaque caractère.
- Exemple associé : 2 caractères et 3 octets.
- Point de vigilance : Comparer deux flottants avec égalité stricte après calcul.
- Activité de reprise associée : Utiliser une tolérance absolue et justifier son ordre de grandeur.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-DATA-BASE-05A.
- Point de départ : `0.1 + 0.2`.
- Angle disciplinaire : vérification critique autour de flottant.
- Démarche attendue : comparer avec une tolérance au lieu de `==`.
- Exemple associé : valeur proche de `0.3`.
- Point de vigilance : Confondre point de code et représentation binaire.
- Activité de reprise associée : Séparer nom du caractère et encodage effectif.
- Mini-production : produire une correction d’erreur avec un nouveau test.
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre ASCII simple avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « caractère dans l’ASCII » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre accent UTF-8 avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « longueur en octets différente de la longueur en caractères » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre chaîne mixte avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « chaîne vide » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre flottant avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « arrondi binaire » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier ASCII simple à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier accent UTF-8 à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier chaîne mixte à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier flottant à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- Unicode : terme à employer dans une justification écrite de la séquence.
- UTF-8 : terme à employer dans une justification écrite de la séquence.
- octet : terme à employer dans une justification écrite de la séquence.
- flottant : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P03-A : modifier la donnée du premier exemple de P03 - Cours - Texte Unicode et nombres réels et conserver exactement la même méthode.
- Variante P03-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P03-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P03-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P03-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P03-F : construire une donnée minimale qui force une décision de méthode.
- Variante P03-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P03-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P03-I : relier une erreur fréquente à une activité corrective précise.
- Variante P03-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P03-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P03-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P03-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P03-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P03-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P03-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
