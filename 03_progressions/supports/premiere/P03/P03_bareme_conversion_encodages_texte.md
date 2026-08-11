---
title: "P03 - barème - Conversion et encodages de texte"
level: "premiere"
sequence_id: "P03"
document_type: "bareme"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Données textuelles et approximation"
notion: "encodage, UTF-8, Latin-1, ASCII, conversion"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-05B"
---

# P03 - Barème - Conversion et encodages de texte

## Objectifs

- Vérifier la compréhension des encodages de caractères (ASCII, Latin-1, UTF-8).
- Évaluer la capacité à identifier et corriger des erreurs d'encodage.
- Contrôler la maîtrise de la conversion entre encodages en Python.

## Capacités officielles

- P-DATA-BASE-05B : Convertir un texte dans différents formats d'encodage en utilisant les fonctions Python appropriées.

## Prérequis

- Connaître la table ASCII (caractères 0-127).
- Savoir que Latin-1 étend ASCII aux caractères 128-255.
- Comprendre le principe de l'encodage multi-octets UTF-8.
- Maîtriser les fonctions Python ord(), chr(), encode(), decode().

## Situation-problème

Un développeur reçoit un fichier texte provenant d'un système ancien encodé en Latin-1. L'affichage dans son éditeur UTF-8 produit des caractères incorrects (mojibake). Il doit identifier l'encodage d'origine, comprendre la source de l'erreur et convertir le fichier correctement. Le barème guide l'évaluation de cette compétence.

## Activité d’entrée

Encoder la chaîne "Noël" en UTF-8 et en Latin-1 avec Python, comparer les octets obtenus et expliquer la différence.

## Exemple

La chaîne "café" encodée en UTF-8 donne b'caf\xc3\xa9' (4 caractères, 5 octets). En Latin-1 elle donne b'caf\xe9' (4 caractères, 4 octets). Le caractère 'é' occupe 1 octet en Latin-1 et 2 octets en UTF-8.

## Barème question par question

### Barème question 1 — Identification et encodage UTF-8 (P-DATA-BASE-05B) — 5 points
- 1.a) Identification de l'encodage : 2 points (1 pt encodage correct identifié parmi ASCII/Latin-1/UTF-8, 1 pt justification par le nombre d'octets ou la plage de valeurs).
- 1.b) Octets UTF-8 : 2 points (1 pt nombre d'octets correct pour le caractère accentué, 1 pt valeurs hexadécimales exactes).
- 1.c) Code Python : 1 point (appel correct à encode('utf-8') avec résultat vérifié).

### Barème question 2 — Erreur d'encodage et correction (P-DATA-BASE-05B) — 5 points
- 2.a) Identification de l'erreur : 2 points (1 pt nature de l'erreur identifiée (décodage Latin-1 d'un flux UTF-8 ou inversement), 1 pt justification claire).
- 2.b) Correction : 2 points (1 pt méthode de correction correcte (ré-encoder puis décoder), 1 pt code Python fonctionnel).
- 2.c) Explication Latin-1 : 1 point (explication que Latin-1 mappe chaque octet à un caractère, donc ne produit jamais d'erreur de décodage mais peut donner des caractères incorrects).

### Barème question 3 — Compatibilité ASCII / Latin-1 / UTF-8 (P-DATA-BASE-05B) — 5 points
- 3.a) Identité ASCII : 2 points (1 pt les 128 premiers caractères sont identiques dans les trois encodages, 1 pt explication que UTF-8 est rétrocompatible avec ASCII).
- 3.b) Résultat d'un programme : 2 points (1 pt résultat correct de l'exécution, 1 pt justification par les propriétés de l'encodage).
- 3.c) Tiret cadratin : 1 point (le caractère '—' (U+2014) nécessite 3 octets en UTF-8 et n'existe pas en Latin-1, avec explication).

### Barème question 4 — Programme de conversion (P-DATA-BASE-05B) — 5 points
- 4.a) Programme : 2 points (1 pt ouverture du fichier avec le bon encodage source, 1 pt écriture avec l'encodage cible et gestion des erreurs).
- 4.b) Octets de "Noël" : 2 points (1 pt octets UTF-8 corrects : b'No\xc3\xabl' (5 octets), 1 pt octets Latin-1 corrects : b'No\xebl' (4 octets)).
- 4.c) Caractère € : 1 point (U+20AC, 3 octets en UTF-8 : \xe2\x82\xac, présent en Latin-9 mais absent de Latin-1).

## Total : 20 points

## Critères de réussite observables
- Les valeurs hexadécimales des octets sont correctes pour chaque encodage.
- Les erreurs d'encodage sont identifiées avec leur cause précise.
- Le code Python proposé est exécutable et produit le résultat attendu.

## Erreurs fréquentes
- Confondre encode() et decode() en Python.
- Croire que Latin-1 et UTF-8 sont identiques pour les caractères accentués.
- Oublier que UTF-8 utilise un nombre variable d'octets par caractère.
- Ne pas distinguer le point de code Unicode de sa représentation en octets.

## Exercices

Les exercices évalués sont les questions 1 à 4 de l'évaluation conversion et encodages de texte P03.

## Corrigé

Les réponses détaillées se trouvent dans P03_corrige_conversion_encodages_texte.md.

## Remédiation

En cas de score inférieur à 10/20, reprendre la comparaison ASCII/UTF-8 sur des caractères simples (lettres non accentuées) avant de passer aux caractères multi-octets.

## Différenciation

- Socle : question 1 (identification d'encodage et octets UTF-8 simples).
- Standard : questions 2 et 3 (erreurs d'encodage et compatibilité).
- Expert : question 4c (caractère € et limites de Latin-1).

## Séance(s) correspondante(s)

Séance dédiée aux encodages de texte et conversions entre formats.
