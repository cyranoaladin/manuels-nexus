---
title: "P05 - Cours - Tables CSV"
level: "premiere"
sequence_id: "P05"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
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

# P05 - Cours - Tables CSV

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
Le fichier `pays_monde.csv` contient des pays, capitales, continents et populations à lire, filtrer, convertir et trier.

## Activité d’entrée
1. Lire une ligne d’en-tête.
2. Filtrer les lignes où `CONTINENT == "Europe"`.
3. Convertir puis trier numériquement les populations valides.
4. Signaler une ligne avec champ manquant.

## Définitions et formalisation
- Définition D1 : table est utilisé dans Traitement de tables avec une donnée, une règle et un contrôle.
- Définition D2 : CSV est utilisé dans Traitement de tables avec une donnée, une règle et un contrôle.
- Définition D3 : filtrage est utilisé dans Traitement de tables avec une donnée, une règle et un contrôle.
- Définition D4 : traitement numérique des populations est utilisé dans Traitement de tables avec une donnée, une règle et un contrôle.
- Cas limite principal : fichier pays_monde.csv vide.

## Exemples corrigés précis
### Exemple corrigé 1 - lecture CSV
- Donnée étudiée : `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531`.
- Méthode : lire avec csv.reader puis convertir POPULATION en int.
- Résultat obtenu : `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}`.
- Contrôle : le cas limite « fichier pays_monde.csv vide » est vérifié séparément.
### Exemple corrigé 2 - filtrage
- Donnée étudiée : un extrait contenant Allemagne, Albanie et Brésil.
- Méthode : conserver les lignes dont CONTINENT vaut Europe.
- Résultat obtenu : `["Allemagne", "Albanie"]`.
- Contrôle : le cas limite « aucun pays du continent demandé » est vérifié séparément.
### Exemple corrigé 3 - traitement numérique des populations
- Donnée étudiée : `82801531`, `3063320`, valeur `invalide`.
- Méthode : convertir POPULATION avec int(row["POPULATION"]), puis placer la ligne dans erreurs si ValueError est levée.
- Résultat obtenu : `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- Contrôle : le cas limite « sélection vide avant tri numérique » est vérifié séparément.
### Exemple corrigé 4 - tri par continent puis population
- Donnée étudiée : lignes regroupées par CONTINENT.
- Méthode : associer par une clé commune.
- Résultat obtenu : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Contrôle : le cas limite « continent absent » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-TABLE-01.
- Point de départ : `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531`.
- Angle disciplinaire : repérage initial autour de lecture CSV.
- Démarche attendue : lire avec csv.reader puis convertir POPULATION en int.
- Exemple associé : dictionnaire Allemagne avec `POPULATION` convertie en entier `82801531`.
- Point de vigilance : Traiter l’en-tête comme une donnée.
- Activité de reprise associée : Marquer l’en-tête et commencer les données à la ligne suivante.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-TABLE-01.
- Point de départ : un extrait contenant Allemagne, Albanie et Brésil.
- Angle disciplinaire : méthode guidée autour de filtrage.
- Démarche attendue : conserver les lignes dont CONTINENT vaut Europe.
- Exemple associé : liste Europe valide `["Allemagne", "Albanie"]` après exclusion de Brésil et de la ligne invalide.
- Point de vigilance : Comparer une valeur numérique restée chaîne.
- Activité de reprise associée : Convertir explicitement avant les comparaisons numériques.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-TABLE-01.
- Point de départ : `82801531`, `3063320`, valeur `invalide`.
- Angle disciplinaire : transfert argumenté autour de traitement numérique des populations.
- Démarche attendue : convertir POPULATION avec int(row["POPULATION"]), puis placer la ligne dans erreurs si ValueError est levée.
- Exemple associé : liste `erreurs` contenant uniquement `{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}`.
- Point de vigilance : Diviser par zéro après filtrage vide.
- Activité de reprise associée : Tester la sélection avant le tri numérique.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-TABLE-01.
- Point de départ : lignes regroupées par CONTINENT.
- Angle disciplinaire : vérification critique autour de tri par continent puis population.
- Démarche attendue : associer par une clé commune.
- Exemple associé : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Point de vigilance : Ignorer silencieusement une ligne mal formée.
- Activité de reprise associée : Isoler les lignes invalides dans une liste de rejets.
- Mini-production : produire une correction d’erreur avec un nouveau test.
## Exercices numérotés
- Exercice 1 : résoudre lecture CSV avec `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531` ; attendu : `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}`.
- Exercice 2 : expliquer filtrage à partir de un extrait contenant Allemagne, Albanie et Brésil ; attendu : `["Allemagne", "Albanie"]`.
- Exercice 3 : comparer traitement numérique des populations avec `82801531`, `3063320`, valeur `invalide` ; attendu : `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]`.
- Exercice 4 : corriger tri par continent puis population pour lignes regroupées par CONTINENT ; attendu : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT`.
- Exercice 5 : tester un cas limite lié à fichier pays_monde.csv vide ; attendu : un fichier avec seulement l’en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` donne une liste vide de pays.
- Exercice 6 : classer deux méthodes possibles pour filtrage ; attendu : la méthode `csv.DictReader` est choisie pour accéder à `row["CONTINENT"]` sans indice fragile.
- Exercice 7 : justifier un transfert qui utilise traitement numérique des populations avec une donnée nouvelle ; attendu : sur `Espagne,Madrid,Europe,46754778`, `int(row["POPULATION"])` donne `46754778` et la ligne reste dans Europe.
- Exercice 8 : étendre un énoncé volontairement erroné sur tri par continent puis population ; attendu : l’erreur est le tri de chaînes ; réparation : convertir puis utiliser la clé `(CONTINENT, -POPULATION, PAYS)`.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531`, appliquer la méthode « lire avec csv.reader puis convertir POPULATION en int », puis écrire `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}` ; résultat : `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}` ; contrôle : faire apparaître le contrôle « fichier pays_monde.csv vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de conserver les lignes dont CONTINENT vaut Europe avant de conclure par `["Allemagne", "Albanie"]` ; résultat : `["Allemagne", "Albanie"]` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « sélection vide avant tri numérique » et valider que ValueError place la ligne invalide dans erreurs ; résultat : `erreurs = [{"PAYS": "Erreur", "CAPITALE": "NA", "CONTINENT": "Europe", "POPULATION": "invalide"}]` ; contrôle : comparer avec le cas « sélection vide avant tri numérique ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Ignorer silencieusement une ligne mal formée. » puis reprendre la procédure correcte ; résultat : dans le groupe Europe : Allemagne `(82801531)` avant Albanie `(3063320)`, puis les autres continents selon `CONTINENT` ; contrôle : corriger l’erreur « Ignorer silencieusement une ligne mal formée. ».
- Corrigé exercice 5 : méthode : identifier `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531`, appliquer la méthode « lire avec csv.reader puis convertir POPULATION en int », puis écrire `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": 82801531}` ; résultat : un fichier avec seulement l’en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` donne une liste vide de pays ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de conserver les lignes dont CONTINENT vaut Europe avant de conclure par `["Allemagne", "Albanie"]` ; résultat : la méthode `csv.DictReader` est choisie pour accéder à `row["CONTINENT"]` sans indice fragile ; contrôle : identifier pourquoi « Comparer une valeur numérique restée chaîne. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « sélection vide avant tri numérique » et valider que ValueError place la ligne invalide dans erreurs ; résultat : sur `Espagne,Madrid,Europe,46754778`, `int(row["POPULATION"])` donne `46754778` et la ligne reste dans Europe ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Ignorer silencieusement une ligne mal formée. » puis reprendre la procédure correcte ; résultat : l’erreur est le tri de chaînes ; réparation : convertir puis utiliser la clé `(CONTINENT, -POPULATION, PAYS)` ; contrôle : proposer une activité corrective inspirée de « Isoler les lignes invalides dans une liste de rejets. ».
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre lecture CSV avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « fichier pays_monde.csv vide » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre filtrage avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « aucun pays du continent demandé » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre traitement numérique des populations avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « sélection vide avant tri numérique » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre tri par continent puis population avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « continent absent » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier lecture CSV à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier filtrage à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier traitement numérique des populations à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier tri par continent puis population à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- table : terme à employer dans une justification écrite de la séquence.
- CSV : terme à employer dans une justification écrite de la séquence.
- filtrage : terme à employer dans une justification écrite de la séquence.
- traitement numérique des populations : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P05-A : modifier la donnée du premier exemple de P05 - Cours - Tables CSV et conserver exactement la même méthode.
- Variante P05-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P05-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P05-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P05-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P05-F : construire une donnée minimale qui force une décision de méthode.
- Variante P05-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P05-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P05-I : relier une erreur fréquente à une activité corrective précise.
- Variante P05-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P05-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P05-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P05-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P05-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P05-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P05-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.


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
