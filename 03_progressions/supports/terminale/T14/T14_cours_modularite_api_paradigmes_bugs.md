---
title: "T14 - cours - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "modularité, API, paradigmes et bugs"
notion: "modularité, API, paradigmes et bugs"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
    - "T-LANG-03B"
    - "T-LANG-03C"
    - "T-LANG-04A"
    - "T-LANG-04B"
    - "T-LANG-05"
---

# T14 - Cours - modularité, API, paradigmes et bugs

## Objectifs spécifiques
- Identifier les données utiles de la situation : meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}].
- Employer le vocabulaire : API, documentation, module, paradigme impératif, paradigme fonctionnel, objet.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-LANG-03A.
- T-LANG-03B.
- T-LANG-03C.
- T-LANG-04A.
- T-LANG-04B.
- T-LANG-05.

## Situation-problème
meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]

## À savoir
- API.
- documentation.
- module.
- paradigme impératif.
- paradigme fonctionnel.
- objet.
- bug de typage.
- effet de bord.

## Méthodes
- utiliser une API ou bibliothèque (T-LANG-03A).
- exploiter la documentation d'une API (T-LANG-03B).
- créer un module simple et le documenter (T-LANG-03C).
- distinguer paradigmes impératif, fonctionnel et objet (T-LANG-04A).
- choisir le paradigme selon le champ d'application (T-LANG-04B).
- répondre aux causes typiques de bugs (T-LANG-05).

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : utiliser une API ou bibliothèque (T-LANG-03A).
- Résultat attendu : `from meteo import moyenne_temperature ; moyenne_temperature(releves)` renvoie `30.0`. L'API est utilisée sans connaître son implémentation interne.
- Contrôle : capacité T-LANG-03A et cas limite `liste vide`.
### Exemple corrigé 2
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : exploiter la documentation d'une API (T-LANG-03B).
- Résultat attendu : lire la docstring de `moyenne_temperature` pour connaître le format attendu (liste de dictionnaires avec clé `temperature`), le type de retour (`float`) et les exceptions levées (`ValueError` si liste vide).
- Contrôle : capacité T-LANG-03B et cas limite `clé temperature absente`.
### Exemple corrigé 3
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : créer un module simple et le documenter (T-LANG-03C).
- Résultat attendu : créer le fichier `meteo.py` contenant `def moyenne_temperature(releves):` avec docstring, puis l'importer depuis `main.py` avec `from meteo import moyenne_temperature`.
- Contrôle : capacité T-LANG-03C et cas limite `module sans docstring`.
### Exemple corrigé 4
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : distinguer paradigmes impératif, fonctionnel et objet (T-LANG-04A).
- Résultat attendu : version impérative (boucle `for` avec accumulateur), version fonctionnelle (`sum(r["temperature"] for r in releves) / len(releves)`), version objet (`Releve.moyenne()`). Les trois produisent `30.0`.
- Contrôle : capacité T-LANG-04A et cas limite `liste vide`.
### Exemple corrigé 5
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : choisir le paradigme selon le champ d'application (T-LANG-04B).
- Résultat attendu : l'approche fonctionnelle convient pour un calcul sans effet de bord ; l'approche objet convient si `Releve` doit aussi stocker ville et date ; l'approche impérative convient pour un script simple.
- Contrôle : capacité T-LANG-04B et cas limite `type chaîne temperature="31"`.
### Exemple corrigé 6
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Méthode : répondre aux causes typiques de bugs (T-LANG-05).
- Résultat attendu : cause typique = division par zéro si `releves` est vide ; réponse = lever `ValueError` avec message explicite ; test = `assert moyenne_temperature([])` lève `ValueError`.
- Contrôle : capacité T-LANG-05 et cas limite `liste vide`.

## Cas limites
- liste vide.
- clé temperature absente.
- type chaîne.

## Erreurs fréquentes
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Exercices intégrés
1. Identifier les données utiles dans `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
2. Appliquer : utiliser l'API `moyenne_temperature` sans connaître son implémentation (T-LANG-03A).
3. Appliquer : créer le module `meteo.py` avec docstring et l'importer (T-LANG-03C).
4. Appliquer : distinguer les versions impérative, fonctionnelle et objet du calcul de moyenne (T-LANG-04A).
5. Décider le cas limite `liste vide` et écrire un test révélant le bug de division par zéro (T-LANG-05).

## Critères de réussite observables
- Une capacité parmi T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05 est citée et utilisée.
- Le résultat attendu est explicite : moyenne_temperature(releves) -> 30.0.
- Le cas limite `clé temperature absente` est tranché.

## Lien avec la progression
- Séance : T14-S1 à T14-S4.
- TD : `T14_TD_modularite_api_paradigmes_bugs.md`.
- TP : `T14_tp_modularite_api_paradigmes_bugs.md`.
- Évaluation : `T14_evaluation_modularite_api_paradigmes_bugs.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur modularité, API et bugs. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : module, interface, contrat, API, exception, test de régression, effet de bord.
- Capacités reliées : T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- utiliser une API ou bibliothèque et exploiter sa documentation (T-LANG-03A, T-LANG-03B).
- créer un module simple avec docstring et l’importer (T-LANG-03C).
- distinguer les paradigmes impératif, fonctionnel et objet sur un même exemple (T-LANG-04A).
- choisir le paradigme adapté au champ d’application (T-LANG-04B).
- identifier une cause typique de bug et écrire un test qui la révèle (T-LANG-05).

### Erreurs fréquentes spécifiques
- Un élève peut modifier une API sans mettre à jour ses appels ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut masquer une exception utile ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut corriger un bug sans test de régression ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de modularité, API et bugs.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
