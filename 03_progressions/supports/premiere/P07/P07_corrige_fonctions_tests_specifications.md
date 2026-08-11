---
title: "P07 - corrige - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "fonctions, tests et spécifications"
notion: "fonctions, tests et spécifications"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
    - "P-LANG-02"
    - "P-LANG-03A"
    - "P-LANG-03B"
    - "P-LANG-03C"
    - "P-LANG-04"
    - "P-LANG-05"
---

# P07 - Corrigé - fonctions, tests et spécifications

## Corrigé du TD
### Exercice 1
- Réponse attendue : signature complète de prix_ttc.
- Méthode : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- Cas limite : prix_ht=0.
### Exercice 2
- Réponse attendue : prix_ttc(80,0.20) -> 96.0.
- Méthode : poser prix_ht >= 0 et taux >= 0.
- Cas limite : taux=0.
### Exercice 3
- Réponse attendue : prix_ttc(-5,0.20) -> ValueError.
- Méthode : vérifier résultat >= prix_ht.
- Cas limite : type chaîne "80".
### Exercice 4
- Réponse attendue : taux=0 -> résultat 80.0.
- Méthode : écrire tests nominal, limite et invalide.
- Cas limite : prix_ht=0.
### Exercice 5
- Réponse attendue : signature complète de prix_ttc.
- Méthode : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- Cas limite : taux=0.
### Exercice 6
- Réponse attendue : prix_ttc(80,0.20) -> 96.0.
- Méthode : poser prix_ht >= 0 et taux >= 0.
- Cas limite : type chaîne "80".
### Exercice 7
- Réponse attendue : prix_ttc(-5,0.20) -> ValueError.
- Méthode : vérifier résultat >= prix_ht.
- Cas limite : prix_ht=0.
### Exercice 8
- Réponse attendue : taux=0 -> résultat 80.0.
- Méthode : écrire tests nominal, limite et invalide.
- Cas limite : taux=0.

### Exercice 9
- Capacité mobilisée : P-LANG-02.
- Réponse attendue : (9a) Traits communs : fonction nommée avec paramètres, mot-clé `return`, expression arithmétique identique. (9b) Traits Python : indentation significative (pas d'accolades), typage dynamique (pas de `float` obligatoire). (9c) Python : annotation optionnelle `-> float` ; JavaScript : implicite ; C : obligatoire dans la signature `float prix_ttc(...)`.
- Méthode : comparer ligne par ligne les trois codes, identifier les éléments syntaxiques communs et les différences.
- Cas limite : un langage fonctionnel (Haskell) n'utiliserait pas `return` — le trait « return explicite » est propre aux langages impératifs.

### Exercice 10
- Capacité mobilisée : P-LANG-05.
- Réponse attendue : (10a) `import math ; math.sqrt(2) * 5` ≈ 7.0710678118654755. (10b) `math.floor(3.7)` → 3 ; `math.floor(-3.2)` → −4 (arrondi vers −∞, pas vers 0). (10c) `math.floor` arrondit vers −∞ (plancher), `math.ceil` arrondit vers +∞ (plafond) ; `math.floor(-3.2)` → −4, `math.ceil(-3.2)` → −3.
- Méthode : importer le module, consulter `help()`, exécuter les fonctions et comparer.
- Cas limite : `math.floor(-3.0)` → −3 (entier exact, pas d'arrondi).

## Corrigé du TP
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Résultat principal : signature complète de prix_ttc.
- Résultat secondaire : prix_ttc(80,0.20) -> 96.0.

## Corrigé de l évaluation
- Question 1 : signature complète de prix_ttc.
- Question 2 : prix_ttc(80,0.20) -> 96.0.
- Question 3 : prix_ttc(-5,0.20) -> ValueError.
- Question 4 : taux=0 -> résultat 80.0.
