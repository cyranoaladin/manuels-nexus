---
title: "P05 - Td - Tables CSV"
level: "premiere"
sequence_id: "P05"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "adapted_from_drive"
theme: "Traitement de tables"
notion: "table, CSV, filtrage, traitement numérique des populations"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-TABLE-01"
    - "P-TABLE-02"
---

# P05 - TD - Tables CSV

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-TABLE-01
- P-TABLE-02

## Prérequis
- Reconnaître une consigne liée à table.
- Distinguer donnée, méthode et conclusion dans le thème Traitement de tables.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P05-S1 à P05-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un fichier CSV de pays contient des champs `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`. L'extrait utilisé en classe est adapté depuis `Documents_DRIVE/2_NSI/Cours/Première NSI Pierrot caillabet/1_2019-2020/1_Cours/11_traitement de tables/pays_monde.csv`, sans donnée personnelle.

## Activité d’entrée
1. Lire l’en-tête `PAYS,CAPITALE,CONTINENT,POPULATION`.
2. Filtrer les lignes où `CONTINENT == "Europe"`.
3. Calculer la population totale d’un petit extrait européen.
4. Signaler une ligne dont la population n’est pas convertible en entier.

## Source de données utilisée

Le fichier élève normalisé est `03_progressions/supports/premiere/P05/data/pays_monde_extrait.csv`. Il contient uniquement des pays, capitales, continents et populations : aucune donnée élève, aucune note, aucun identifiant personnel.

## Exemples corrigés précis
### Exemple corrigé 1 - lecture CSV
- Donnée étudiée : `PAYS,CAPITALE,CONTINENT,POPULATION` puis `Allemagne,Berlin,Europe,82801531`.
- Méthode : lire l’en-tête, associer chaque champ à sa valeur, convertir `POPULATION` en entier.
- Résultat obtenu : `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}`.
- Contrôle : le cas limite « fichier pays_monde.csv vide » est vérifié séparément.
### Exemple corrigé 2 - filtrage
- Donnée étudiée : Allemagne, Albanie, Brésil.
- Méthode : conserver les lignes dont `CONTINENT` vaut exactement `Europe`.
- Résultat obtenu : Allemagne et Albanie sont retenues ; Brésil est exclu.
- Contrôle : le cas limite « aucun pays du continent demandé » est vérifié séparément.
### Exemple corrigé 3 - traitement numérique des populations
- Donnée étudiée : populations Allemagne `82801531`, Albanie `3063320`, Brésil `204259812` et Erreur `invalide`.
- Méthode : convertir les trois populations en entiers puis additionner.
- Résultat obtenu : `valides = ["Allemagne", "Albanie", "Brésil"]` et `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- Contrôle : le cas limite « sélection vide avant tri numérique » est vérifié séparément.
### Exemple corrigé 4 - tri par continent puis population
- Donnée étudiée : lignes regroupées par CONTINENT.
- Méthode : associer par une clé commune.
- Résultat obtenu : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Contrôle : le cas limite « continent absent » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : résoudre la lecture de `Allemagne,Berlin,Europe,82801531`.
- Production attendue : dictionnaire typé avec population entière.
- Contrainte de contrôle : faire apparaître le contrôle « fichier pays_monde.csv vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : expliquer le filtrage Europe sur Allemagne, Albanie et Brésil.
- Production attendue : `["Allemagne", "Albanie"]`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : contrôler et convertir les populations Allemagne, Albanie, Brésil et Erreur.
- Production attendue : `valides = ["Allemagne", "Albanie", "Brésil"]` et `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- Contrainte de contrôle : comparer avec le cas « sélection vide avant tri numérique ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : corriger tri par continent puis population pour lignes regroupées par CONTINENT.
- Production attendue : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Contrainte de contrôle : corriger l’erreur « Ignorer silencieusement une ligne mal formée. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : tester un cas limite lié à fichier pays_monde.csv vide.
- Production attendue : un fichier avec seulement l’en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` donne une liste vide de pays.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : classer deux méthodes possibles pour filtrage.
- Production attendue : la méthode `csv.DictReader` est choisie pour accéder à `row["CONTINENT"]` sans indice fragile.
- Contrainte de contrôle : identifier pourquoi « Comparer une valeur numérique restée chaîne. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : justifier un transfert qui utilise traitement numérique des populations avec une donnée nouvelle.
- Production attendue : sur `Espagne,Madrid,Europe,46754778`, `int(row["POPULATION"])` donne `46754778` et la ligne reste dans Europe.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-TABLE-01.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur tri par continent puis population.
- Production attendue : l’erreur est le tri de chaînes ; réparation : convertir puis utiliser la clé `(CONTINENT, -POPULATION, PAYS)`.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Isoler les lignes invalides dans une liste de rejets. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}`.
- Contrôle : faire apparaître le contrôle « fichier pays_monde.csv vide ».
- Erreur traitée : EF1 - Traiter l’en-tête comme une donnée.
- Donnée utilisée alpha dans P05 td tables csv : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P05 td tables csv : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P05 td tables csv : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : Allemagne et Albanie sont sélectionnées ; Brésil ne l’est pas.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Comparer une valeur numérique restée chaîne.
- Donnée utilisée beta dans P05 td tables csv : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P05 td tables csv : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P05 td tables csv : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `valides = ["Allemagne", "Albanie", "Brésil"]` et `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- Contrôle : comparer avec le cas « sélection vide avant tri numérique ».
- Erreur traitée : EF3 - Diviser par zéro après filtrage vide.
- Donnée utilisée gamma dans P05 td tables csv : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P05 td tables csv : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P05 td tables csv : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Contrôle : corriger l’erreur « Ignorer silencieusement une ligne mal formée. ».
- Erreur traitée : EF4 - Ignorer silencieusement une ligne mal formée.
- Donnée utilisée delta dans P05 td tables csv : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P05 td tables csv : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P05 td tables csv : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
Allemagne,Berlin,Europe,82801531`, appliquer la méthode « lire avec csv.reader puis convertir POPULATION en int », puis écrire `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}`.
- Résultat : un fichier avec seulement l’en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` donne une liste vide de pays.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Traiter l’en-tête comme une donnée.
- Donnée utilisée epsilon dans P05 td tables csv : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P05 td tables csv : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P05 td tables csv : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode `csv.DictReader` est choisie pour accéder à `row["CONTINENT"]` sans indice fragile.
- Contrôle : identifier pourquoi « Comparer une valeur numérique restée chaîne. » est une erreur.
- Erreur traitée : EF2 - Comparer une valeur numérique restée chaîne.
- Donnée utilisée zeta dans P05 td tables csv : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P05 td tables csv : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P05 td tables csv : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : sur `Espagne,Madrid,Europe,46754778`, `int(row["POPULATION"])` donne `46754778` et la ligne reste dans Europe.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Diviser par zéro après filtrage vide.
- Donnée utilisée eta dans P05 td tables csv : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P05 td tables csv : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P05 td tables csv : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est le tri de chaînes ; réparation : convertir puis utiliser la clé `(CONTINENT, -POPULATION, PAYS)`.
- Contrôle : proposer une activité corrective inspirée de « Isoler les lignes invalides dans une liste de rejets. ».
- Erreur traitée : EF4 - Ignorer silencieusement une ligne mal formée.
- Donnée utilisée theta dans P05 td tables csv : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P05 td tables csv : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P05 td tables csv : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P05 td tables csv : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- Erreur fréquente EF1 - Traiter l’en-tête comme une donnée.
- Erreur fréquente EF2 - Comparer une valeur numérique restée chaîne.
- Erreur fréquente EF3 - Diviser par zéro après filtrage vide.
- Erreur fréquente EF4 - Ignorer silencieusement une ligne mal formée.

## Remédiation ciblée
- Activité corrective EF1 : Marquer l’en-tête et commencer les données à la ligne suivante.
- Activité corrective EF2 : Convertir explicitement avant les comparaisons numériques.
- Activité corrective EF3 : Tester la sélection avant le tri numérique.
- Activité corrective EF4 : Isoler les lignes invalides dans une liste de rejets.

## Différenciation
- Socle : traiter `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531` avec une fiche méthode fournie.
- Standard : traiter un extrait contenant Allemagne, Albanie et Brésil en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « sélection vide avant tri numérique » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.


## Fil conducteur P05 - pays_monde.csv
- Capacités travaillées : P-TABLE-01 pour importer et parcourir `pays_monde.csv`, P-TABLE-02 pour filtrer, convertir et trier la table.
- Champs obligatoires : `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`.
- Lecture comparée : `csv.reader` donne des listes, `csv.DictReader` donne des dictionnaires comme `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"}`.
- Conversion obligatoire : `int(row["POPULATION"])` transforme `"82801531"` en `82801531` et rejette la ligne invalide `POPULATION="invalide"`.
- Filtrage Europe : Allemagne et Albanie sont conservées, Brésil est exclu.
- Tri lexicographique : `sorted(["100", "20", "3"])` donne `"100", "20", "3"`; ce n’est pas un tri numérique.
- Tri numérique : `sorted([100, 20, 3])` donne `3, 20, 100`.
- Tri par continent puis population : la clé `(row["CONTINENT"], -row["POPULATION"], row["PAYS"])` classe d’abord par continent, puis par population décroissante.


## Pipeline contrôlé P05
1. Charger avec `csv.DictReader`.
2. Convertir `POPULATION` avec `int(row["POPULATION"])`.
3. Séparer `valides` et `erreurs`.
4. Filtrer les lignes valides par `CONTINENT`.
5. Trier les lignes valides par `CONTINENT` puis `POPULATION`.

Résultats attendus sur l’extrait de référence :
- `valides = ["Allemagne", "Albanie", "Brésil"]`.
- `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- `Europe valide = ["Allemagne", "Albanie"]`.
