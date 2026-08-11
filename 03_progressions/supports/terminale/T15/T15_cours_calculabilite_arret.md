---
title: "T15 - cours - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - Cours - calculabilité, programme comme donnée et arrêt

## Objectifs spécifiques
- Identifier les données utiles de la situation : arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q).
- Employer le vocabulaire : programme comme donnée, interpréteur, calculabilité, langage indépendant, problème de l arrêt, contradiction.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-LANG-01A.
- T-LANG-01B.
- T-LANG-01C.

## Situation-problème
arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)

## À savoir
- programme comme donnée.
- interpréteur.
- calculabilité.
- langage indépendant.
- problème de l arrêt.
- contradiction.

## Méthodes
- encoder un programme comme texte.
- raisonner indépendamment de Python.
- poser un oracle hypothétique.
- construire un programme contradictoire.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Méthode : encoder un programme comme texte.
- Résultat attendu : source="print(1)" est une donnée.
- Contrôle : capacité T-LANG-01A et cas limite `programme très long mais fini`.
### Exemple corrigé 2
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Méthode : raisonner indépendamment de Python.
- Résultat attendu : arrete(P,x) renvoie True ou False.
- Contrôle : capacité T-LANG-01B et cas limite `langage différent`.
### Exemple corrigé 3
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Méthode : poser un oracle hypothétique.
- Résultat attendu : Q boucle si arrete(Q,Q) dit True.
- Contrôle : capacité T-LANG-01C et cas limite `entrée absente`.
### Exemple corrigé 4
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Méthode : construire un programme contradictoire.
- Résultat attendu : contradiction donc oracle impossible.
- Contrôle : capacité T-LANG-01A et cas limite `programme très long mais fini`.

## Cas limites
- programme très long mais fini.
- langage différent.
- entrée absente.

## Erreurs fréquentes
- non connu confondu avec impossible.
- tests finis comme preuve.
- contradiction oubliée.

## Exercices intégrés
1. Identifier les données utiles dans `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
2. Appliquer : encoder un programme comme texte.
3. Appliquer : raisonner indépendamment de Python.
4. Décider le cas limite `programme très long mais fini`.

## Critères de réussite observables
- Une capacité parmi T-LANG-01A, T-LANG-01B, T-LANG-01C est citée et utilisée.
- Le résultat attendu est explicite : source="print(1)" est une donnée.
- Le cas limite `langage différent` est tranché.

## Lien avec la progression
- Séance : T15-S1 à T15-S4.
- TD : `T15_TD_calculabilite_arret.md`.
- TP : `T15_tp_calculabilite_arret.md`.
- Évaluation : `T15_evaluation_calculabilite_arret.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur calculabilité et arrêt. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : programme, entrée, terminaison, indécidabilité, contradiction, simulation.
- Capacités reliées : T-LANG-01A, T-LANG-01B, T-LANG-01C.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- distinguer un programme qui boucle d’un programme lent.
- formuler le problème de l’arrêt sur une entrée donnée.
- expliquer le raisonnement par contradiction sans le coder.

### Erreurs fréquentes spécifiques
- Un élève peut confondre non calculé et non calculable ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut tester quelques cas et conclure universellement ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut oublier que l’entrée fait partie du problème ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de calculabilité et arrêt.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
