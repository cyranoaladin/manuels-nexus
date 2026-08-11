---
title: "P05 - Version amenagee - Tables CSV"
level: "premiere"
sequence_id: "P05"
document_type: "version_amenagee"
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


# P05 - Version aménagée - Tables CSV

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

## Version aménagée - Énoncé élève
### Question aménagée 1
- Énoncé élève : traiter lecture CSV avec la donnée `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531`.
- Aide intégrée : commencer par lire avec csv.reader puis convertir POPULATION en int.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Traiter l’en-tête comme une donnée.
### Question aménagée 2
- Énoncé élève : traiter filtrage avec la donnée un extrait contenant Allemagne, Albanie et Brésil.
- Aide intégrée : commencer par conserver les lignes dont CONTINENT vaut Europe.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Comparer une valeur numérique restée chaîne.
### Question aménagée 3
- Énoncé élève : traiter traitement numérique des populations avec la donnée `82801531`, `3063320`, valeur `invalide`.
- Aide intégrée : commencer par convertir POPULATION avec int(row["POPULATION"]), puis placer la ligne dans erreurs si ValueError est levée.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Diviser par zéro après filtrage vide.
### Question aménagée 4
- Énoncé élève : traiter tri par continent puis population avec la donnée lignes regroupées par CONTINENT.
- Aide intégrée : commencer par associer par une clé commune.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Ignorer silencieusement une ligne mal formée.
## Exercices numérotés
- Exercice 1 : résoudre lecture CSV avec `PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531` avec aide possible sur la méthode.
- Exercice 2 : expliquer filtrage à partir de un extrait contenant Allemagne, Albanie et Brésil avec aide possible sur la méthode.
- Exercice 3 : comparer traitement numérique des populations avec `82801531`, `3063320`, valeur `invalide` avec aide possible sur la méthode.
- Exercice 4 : corriger tri par continent puis population pour lignes regroupées par CONTINENT avec aide possible sur la méthode.
- Exercice 5 : tester un cas limite lié à fichier pays_monde.csv vide avec aide possible sur la méthode.
- Exercice 6 : classer deux méthodes possibles pour filtrage avec aide possible sur la méthode.
- Exercice 7 : justifier un transfert qui utilise traitement numérique des populations avec une donnée nouvelle avec aide possible sur la méthode.
- Exercice 8 : étendre un énoncé volontairement erroné sur tri par continent puis population avec aide possible sur la méthode.
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
