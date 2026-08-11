---
title: "P07 - td - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "td"
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

# P07 - TD - fonctions, tests et spécifications

## Objectifs
- Travailler signature, précondition, postcondition, assertion, test unitaire.
- Produire huit réponses vérifiables avec données explicites.

## Progression socle / standard / approfondissement
- Socle : exercices 1 et 2.
- Standard : exercices 3 à 6.
- Approfondissement : exercices 7 et 8.

## Exercices
### Exercice 1
- Type : lecture/analyse.
- Capacité officielle : P-LANG-01.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=alpha
- Consigne : écrire def prix_ttc(prix_ht: float, taux: float) -> float ; traiter aussi `prix_ht=0` si nécessaire.
- Réponse attendue : signature complète de prix_ttc.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `prix_ht=0`.
### Exercice 2
- Type : production/écriture.
- Capacité officielle : P-LANG-02.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=beta
- Consigne : poser prix_ht >= 0 et taux >= 0 ; traiter aussi `taux=0` si nécessaire.
- Réponse attendue : prix_ttc(80,0.20) -> 96.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `taux=0`.
### Exercice 3
- Type : production/écriture.
- Capacité officielle : P-LANG-03A.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=gamma
- Consigne : vérifier résultat >= prix_ht ; traiter aussi `type chaîne "80"` si nécessaire.
- Réponse attendue : prix_ttc(-5,0.20) -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `type chaîne "80"`.
### Exercice 4
- Type : cas limite.
- Capacité officielle : P-LANG-03B.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=delta
- Consigne : écrire tests nominal, limite et invalide ; traiter aussi `prix_ht=0` si nécessaire.
- Réponse attendue : taux=0 -> résultat 80.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `prix_ht=0`.
### Exercice 5
- Type : justification.
- Capacité officielle : P-LANG-03C.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=epsilon
- Consigne : écrire def prix_ttc(prix_ht: float, taux: float) -> float ; traiter aussi `taux=0` si nécessaire.
- Réponse attendue : signature complète de prix_ttc.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `taux=0`.
### Exercice 6
- Type : lecture/analyse.
- Capacité officielle : P-LANG-04.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=zeta
- Consigne : poser prix_ht >= 0 et taux >= 0 ; traiter aussi `type chaîne "80"` si nécessaire.
- Réponse attendue : prix_ttc(80,0.20) -> 96.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `type chaîne "80"`.
### Exercice 7
- Type : production/écriture.
- Capacité officielle : P-LANG-05.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=eta
- Consigne : vérifier résultat >= prix_ht ; traiter aussi `prix_ht=0` si nécessaire.
- Réponse attendue : prix_ttc(-5,0.20) -> ValueError.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `prix_ht=0`.
### Exercice 8
- Type : justification.
- Capacité officielle : P-LANG-01.
- Données : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`. ; jeu_exercice=theta
- Consigne : écrire tests nominal, limite et invalide ; traiter aussi `taux=0` si nécessaire.
- Réponse attendue : taux=0 -> résultat 80.0.
- Critère de réussite : donnée exacte, méthode nommée, résultat final et décision sur `taux=0`.

### Exercice 9
- Type : lecture/analyse.
- Capacité officielle : P-LANG-02.
- Données : trois versions de la fonction `prix_ttc` — en Python (`def prix_ttc(prix_ht, taux): return prix_ht * (1 + taux)`), en JavaScript (`function prix_ttc(prix_ht, taux) { return prix_ht * (1 + taux); }`), en C (`float prix_ttc(float prix_ht, float taux) { return prix_ht * (1 + taux); }`).
- Consigne : (9a) identifier trois traits communs aux trois langages ; (9b) identifier deux traits particuliers à Python par rapport aux deux autres ; (9c) pour chaque langage, préciser comment le type de retour est indiqué.
- Réponse attendue : traits communs (fonction nommée, paramètres, return) ; traits Python (indentation significative, pas de type obligatoire) ; type retour (Python : annotation optionnelle, JS : implicite, C : obligatoire `float`).
- Critère de réussite : au moins 3 traits communs cités, 2 traits particuliers, justification par citation du code.

### Exercice 10
- Type : production/écriture.
- Capacité officielle : P-LANG-05.
- Données : le module `math` de Python (fonctions `math.sqrt`, `math.floor`, `math.ceil`, `math.pi`).
- Consigne : (10a) écrire un programme qui utilise `math.sqrt` pour calculer la diagonale d'un carré de côté 5 (formule : côté × √2) ; (10b) utiliser `help(math.floor)` pour décrire ce que fait `math.floor` puis calculer `math.floor(3.7)` et `math.floor(-3.2)` ; (10c) expliquer la différence entre `math.floor` et `math.ceil` en utilisant la documentation.
- Réponse attendue : (10a) `math.sqrt(2) * 5` ≈ 7.07 ; (10b) `math.floor(3.7)` → 3, `math.floor(-3.2)` → −4 ; (10c) floor arrondit vers −∞, ceil vers +∞.
- Critère de réussite : import correct, fonction appelée avec bons arguments, résultat vérifié, documentation citée.

## Corrigé
### Corrigé exercice 1
- Capacité mobilisée : P-LANG-01.
- Résultat attendu : signature complète de prix_ttc.
- Justification : la tâche `écrire def prix_ttc(prix_ht: float, taux: float) -> float` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : test unique non suffisant.
- Donnée utilisée alpha dans P07 TD fonctions tests specifications : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Capacité mobilisée : P-LANG-02.
- Résultat attendu : prix_ttc(80,0.20) -> 96.0.
- Justification : la tâche `poser prix_ht >= 0 et taux >= 0` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : précondition absente.
- Donnée utilisée beta dans P07 TD fonctions tests specifications : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Capacité mobilisée : P-LANG-03A.
- Résultat attendu : prix_ttc(-5,0.20) -> ValueError.
- Justification : la tâche `vérifier résultat >= prix_ht` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : effet de bord global.
- Donnée utilisée gamma dans P07 TD fonctions tests specifications : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Capacité mobilisée : P-LANG-03B.
- Résultat attendu : taux=0 -> résultat 80.0.
- Justification : la tâche `écrire tests nominal, limite et invalide` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : test unique non suffisant.
- Donnée utilisée delta dans P07 TD fonctions tests specifications : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Capacité mobilisée : P-LANG-03C.
- Résultat attendu : signature complète de prix_ttc.
- Justification : la tâche `écrire def prix_ttc(prix_ht: float, taux: float) -> float` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : précondition absente.
- Donnée utilisée epsilon dans P07 TD fonctions tests specifications : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Capacité mobilisée : P-LANG-04.
- Résultat attendu : prix_ttc(80,0.20) -> 96.0.
- Justification : la tâche `poser prix_ht >= 0 et taux >= 0` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : effet de bord global.
- Donnée utilisée zeta dans P07 TD fonctions tests specifications : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Capacité mobilisée : P-LANG-05.
- Résultat attendu : prix_ttc(-5,0.20) -> ValueError.
- Justification : la tâche `vérifier résultat >= prix_ht` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : test unique non suffisant.
- Donnée utilisée eta dans P07 TD fonctions tests specifications : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Capacité mobilisée : P-LANG-01.
- Résultat attendu : taux=0 -> résultat 80.0.
- Justification : la tâche `écrire tests nominal, limite et invalide` s applique à `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError` ; erreur évitée : précondition absente.
- Donnée utilisée theta dans P07 TD fonctions tests specifications : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P07 TD fonctions tests specifications : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P07 TD fonctions tests specifications : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P07 TD fonctions tests specifications : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

### Corrigé exercice 9
- Capacité mobilisée : P-LANG-02.
- Résultat attendu : traits communs (fonction nommée, paramètres, return) ; traits Python (indentation, typage dynamique) ; type retour (Python optionnel, JS implicite, C obligatoire).
- Justification : la tâche `comparer trois versions de la même fonction` s'applique à `def prix_ttc / function prix_ttc / float prix_ttc` ; erreur évitée : confondre syntaxe et sémantique.
- Donnée utilisée iota dans P07 TD fonctions tests specifications : cas iota de l'exercice 9 avec les trois versions Python, JavaScript et C.
- Méthode iota dans P07 TD fonctions tests specifications : comparaison ligne par ligne, extraction des éléments syntaxiques communs et divergents.
- Résultat iota dans P07 TD fonctions tests specifications : tableau traits communs (3) et traits particuliers (2) avec citation du code source.
- Contrôle iota dans P07 TD fonctions tests specifications : le cas limite « langage fonctionnel sans return explicite » est discuté.

### Corrigé exercice 10
- Capacité mobilisée : P-LANG-05.
- Résultat attendu : `math.sqrt(2)*5` ≈ 7.07 ; `math.floor(3.7)` → 3, `math.floor(-3.2)` → −4 ; floor vers −∞, ceil vers +∞.
- Justification : la tâche `utiliser la documentation du module math` s'applique à `math.sqrt, math.floor, math.ceil` ; erreur évitée : confondre floor et troncature vers zéro.
- Donnée utilisée kappa dans P07 TD fonctions tests specifications : cas kappa de l'exercice 10 avec les fonctions sqrt, floor et ceil du module math.
- Méthode kappa dans P07 TD fonctions tests specifications : import du module, consultation de help(), exécution et comparaison des résultats.
- Résultat kappa dans P07 TD fonctions tests specifications : diagonale calculée, résultats floor/ceil vérifiés sur positifs et négatifs.
- Contrôle kappa dans P07 TD fonctions tests specifications : le cas limite `math.floor(-3.0) → −3` (entier exact, pas d'arrondi) est vérifié.

## Erreurs fréquentes
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Différenciation
- Socle : données annotées.
- Standard : méthode complète.
- Expert : transfert avec `taux=0`.

## Cas limites travaillés
- prix_ht=0.
- taux=0.
- type chaîne "80".

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `signature complète de prix_ttc`.
- Au moins un cas limite de la section précédente est décidé.

