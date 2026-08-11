---
title: "T14 - td - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "td"
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

# T14 - TD - modularité, API, paradigmes et bugs

## Objectifs
- Travailler API, documentation, module, paradigme impératif, paradigme fonctionnel.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : T-LANG-03A.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=alpha
- Consigne : définir fonction publique documentée ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : moyenne_temperature(releves) -> 30.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : T-LANG-03B.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=beta
- Consigne : séparer module et script principal ; traiter aussi `clé temperature absente` si nécessaire.
- Réponse attendue : from meteo import moyenne_temperature.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé temperature absente`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : T-LANG-03C.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=gamma
- Consigne : choisir paradigme selon tâche ; traiter aussi `type chaîne` si nécessaire.
- Réponse attendue : temperature="31" refusée ou convertie.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `type chaîne`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : T-LANG-04A.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=delta
- Consigne : écrire un test révélant un bug ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : liste vide -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 5
- Type : justification.
- Capacité officielle : T-LANG-04B.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=epsilon
- Consigne : définir fonction publique documentée ; traiter aussi `clé temperature absente` si nécessaire.
- Réponse attendue : moyenne_temperature(releves) -> 30.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé temperature absente`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : T-LANG-05.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=zeta
- Consigne : identifier la cause du bug (effet de bord à l'import) puis corriger en séparant module et script principal ; traiter aussi `variable globale mutée` si nécessaire.
- Réponse attendue : cause : effet de bord (exécution à l'import) ; correction : from meteo import moyenne_temperature avec garde `if __name__ == "__main__"`.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `variable globale mutée`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : T-LANG-03A.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=eta
- Consigne : choisir paradigme selon tâche ; traiter aussi `liste vide` si nécessaire.
- Réponse attendue : temperature="31" refusée ou convertie.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `liste vide`.
### Exercice 8
- Type : justification.
- Capacité officielle : T-LANG-03B.
- Données : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`. ; jeu_exercice=theta
- Consigne : écrire un test révélant un bug ; traiter aussi `clé temperature absente` si nécessaire.
- Réponse attendue : liste vide -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `clé temperature absente`.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : T-LANG-03A.
- Résultat attendu : moyenne_temperature(releves) -> 30.0.
- Justification : la tâche `définir fonction publique documentée` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : import avec effet de bord.
- Donnée utilisée alpha dans T14 TD modularite api paradigmes bugs : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : T-LANG-03B.
- Résultat attendu : from meteo import moyenne_temperature.
- Justification : la tâche `séparer module et script principal` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : API sans docstring.
- Donnée utilisée beta dans T14 TD modularite api paradigmes bugs : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : T-LANG-03C.
- Résultat attendu : temperature="31" refusée ou convertie.
- Justification : la tâche `choisir paradigme selon tâche` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : bug corrigé sans test.
- Donnée utilisée gamma dans T14 TD modularite api paradigmes bugs : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : T-LANG-04A.
- Résultat attendu : liste vide -> ValueError.
- Justification : la tâche `écrire un test révélant un bug` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : import avec effet de bord.
- Donnée utilisée delta dans T14 TD modularite api paradigmes bugs : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : T-LANG-04B.
- Résultat attendu : moyenne_temperature(releves) -> 30.0.
- Justification : la tâche `définir fonction publique documentée` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : API sans docstring.
- Donnée utilisée epsilon dans T14 TD modularite api paradigmes bugs : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : T-LANG-05.
- Résultat attendu : cause : effet de bord (exécution à l'import) ; correction : from meteo import moyenne_temperature avec garde `if __name__ == "__main__"`.
- Justification : la tâche `identifier la cause du bug (effet de bord à l'import) puis corriger en séparant module et script principal` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : variable globale mutée silencieusement.
- Donnée utilisée zeta dans T14 TD modularite api paradigmes bugs : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : T-LANG-03A.
- Résultat attendu : temperature="31" refusée ou convertie.
- Justification : la tâche `choisir paradigme selon tâche` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : import avec effet de bord.
- Donnée utilisée eta dans T14 TD modularite api paradigmes bugs : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : T-LANG-03B.
- Résultat attendu : liste vide -> ValueError.
- Justification : la tâche `écrire un test révélant un bug` s applique à `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]` ; erreur évitée : API sans docstring.
- Donnée utilisée theta dans T14 TD modularite api paradigmes bugs : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T14 TD modularite api paradigmes bugs : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T14 TD modularite api paradigmes bugs : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T14 TD modularite api paradigmes bugs : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `clé temperature absente`.

## Cas limites travaillés
- liste vide.
- clé temperature absente.
- type chaîne.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `moyenne_temperature(releves) -> 30.0`.
- Au moins un cas limite de la section précédente est décidé.

