---
title: "T14 - corrige - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "corrige"
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

# T14 - Corrigé - modularité, API, paradigmes et bugs

## Corrigé du TD
### Exercice 1
- Réponse attendue : moyenne_temperature(releves) -> 30.0.
- Méthode : définir fonction publique documentée.
- Cas limite : liste vide.
### Exercice 2
- Réponse attendue : from meteo import moyenne_temperature.
- Méthode : séparer module et script principal.
- Cas limite : clé temperature absente.
### Exercice 3
- Réponse attendue : temperature="31" refusée ou convertie.
- Méthode : choisir paradigme selon tâche.
- Cas limite : type chaîne.
### Exercice 4
- Réponse attendue : liste vide -> ValueError.
- Méthode : écrire un test révélant un bug.
- Cas limite : liste vide.
### Exercice 5
- Réponse attendue : moyenne_temperature(releves) -> 30.0.
- Méthode : définir fonction publique documentée.
- Cas limite : clé temperature absente.
### Exercice 6
- Capacité mobilisée : T-LANG-05.
- Réponse attendue : cause : effet de bord à l'import — le module exécute du code (print, calcul, mutation de variable globale) dès qu'il est importé ; correction : protéger le code exécutable par `if __name__ == "__main__":` afin qu'il ne s'exécute que lorsque le fichier est lancé directement, pas lors d'un import.
- Méthode : identifier l'instruction provoquant l'effet de bord (appel de fonction ou affectation au niveau module), puis la déplacer dans le bloc `if __name__ == "__main__":`.
- Cas limite : variable globale mutée à l'import — si un autre module importe celui-ci, la mutation se produit une seule fois (au premier import, grâce au cache `sys.modules`), mais l'état global reste pollué pour tous les importateurs.
### Exercice 7
- Réponse attendue : temperature="31" refusée ou convertie.
- Méthode : choisir paradigme selon tâche.
- Cas limite : liste vide.
### Exercice 8
- Réponse attendue : liste vide -> ValueError.
- Méthode : écrire un test révélant un bug.
- Cas limite : clé temperature absente.

## Corrigé du TP
- Donnée : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- Résultat principal : moyenne_temperature(releves) -> 30.0.
- Résultat secondaire : from meteo import moyenne_temperature.

## Corrigé de l évaluation
- Question 1 : moyenne_temperature(releves) -> 30.0.
- Question 2 : from meteo import moyenne_temperature.
- Question 3 : temperature="31" refusée ou convertie.
- Question 4 : liste vide -> ValueError.
