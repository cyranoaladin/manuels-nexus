---
title: "P05 - Fiche cours - Tables CSV, import et cohérence"
level: "premiere"
sequence_id: "P05"
document_type: "fiche_cours"
status: "needs_review"
version: "0.4.2"
source: "BO 2019"
source_creation: "adapted_from_drive"
theme: "Traitement de tables"
notion: "tables CSV"
official_program:
  capacities:
    - "P-TABLE-01"
    - "P-TABLE-02"
readiness: operational
private_data: false
---
# P05 - Fiche cours - Tables CSV, import et cohérence

## À savoir
- Une table CSV est une table de données textuelle : la première ligne donne les descripteurs, puis chaque ligne décrit un enregistrement.
- Source locale utilisée : `Documents_DRIVE/2_NSI/Cours/Première NSI Pierrot caillabet/1_2019-2020/1_Cours/11_traitement de tables/pays_monde.csv`, adaptée sans donnée personnelle.
- Dans `pays_monde.csv`, les descripteurs utilisés sont `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`.
- `csv.reader` lit chaque ligne comme une liste de chaînes. La ligne `Allemagne,Berlin,Europe,82801531` devient `["Allemagne", "Berlin", "Europe", "82801531"]`.
- `csv.DictReader` lit chaque ligne comme un dictionnaire indexé par les noms de colonnes. La même ligne devient `{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"}`.
- Une valeur lue dans un CSV est une chaîne : `row["POPULATION"]` vaut `"82801531"`, donc un traitement numérique exige `int(row["POPULATION"])`.
- P-TABLE-01 : importer et parcourir une table. P-TABLE-02 : rechercher, filtrer, trier ou agréger les données d'une table.

## Méthodes
0. P-TABLE-01 correspond ici à l'import et au parcours de `pays_monde.csv`; P-TABLE-02 correspond au filtrage, à la conversion et au tri.
1. Ouvrir `pays_monde.csv` avec `encoding="utf-8"` et `newline=""`.
2. Lire l'en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` pour vérifier que les champs attendus sont présents.
3. Utiliser `csv.reader` si l'on veut travailler par indices, par exemple `ligne[0]` pour le pays.
4. Utiliser `csv.DictReader` si l'on veut travailler par clés, par exemple `row["CONTINENT"] == "Europe"`.
5. Convertir avant les calculs : `population = int(row["POPULATION"])`.
6. Rejeter une ligne invalide, par exemple `POPULATION="invalide"`, dans une liste d'erreurs avant tout tri.
7. Distinguer le tri lexicographique des chaînes du tri numérique des entiers.
8. Pour un classement contrôlé, trier par continent puis population : `key=lambda row: (row["CONTINENT"], -row["POPULATION"], row["PAYS"])`.

## Exemples corrigés
### Exemple corrigé 1 - Lire une ligne avec `csv.DictReader`
Donnée dans `pays_monde.csv` :

```csv
PAYS,CAPITALE,CONTINENT,POPULATION
Allemagne,Berlin,Europe,82801531
```

Avec `csv.DictReader`, la ligne de données donne :

```python
{"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"}
```

La population n'est pas encore un entier. La conversion correcte est :

```python
population = int(row["POPULATION"])
```

Le résultat numérique est `82801531`.

### Exemple corrigé 2 - Filtrer l'Europe
Extrait :

```python
rows = [
    {"PAYS": "Allemagne", "CAPITALE": "Berlin", "CONTINENT": "Europe", "POPULATION": "82801531"},
    {"PAYS": "Albanie", "CAPITALE": "Tirana", "CONTINENT": "Europe", "POPULATION": "3063320"},
    {"PAYS": "Brésil", "CAPITALE": "Brasilia", "CONTINENT": "Amérique du Sud", "POPULATION": "204259812"},
]
```

Filtrage :

```python
europe = [row for row in rows if row["CONTINENT"] == "Europe"]
```

Résultat attendu : Allemagne et Albanie, pas Brésil.

### Exemple corrigé 3 - Tri lexicographique contre tri numérique
Comparaison des chaînes :

```python
sorted(["82801531", "3063320", "204259812"])
```

Résultat lexicographique : `["204259812", "3063320", "82801531"]`, car les chaînes sont comparées caractère par caractère.

Comparaison des entiers :

```python
sorted([82801531, 3063320, 204259812])
```

Résultat numérique : `[3063320, 82801531, 204259812]`.

### Exemple corrigé 4 - Tri par continent puis population
Après conversion, le tri :

```python
sorted(rows, key=lambda row: (row["CONTINENT"], -row["POPULATION"], row["PAYS"]))
```

place les pays par `CONTINENT`, puis par `POPULATION` décroissante dans chaque continent. Dans le groupe Europe, Allemagne (`82801531`) vient avant Albanie (`3063320`).

## Erreurs fréquentes
- Traiter l'en-tête `PAYS,CAPITALE,CONTINENT,POPULATION` comme une ligne de pays : il faut le lire comme descripteurs.
- Comparer `"82801531"` et `"3063320"` sans conversion : le tri lexicographique n'est pas un tri numérique.
- Écrire `int(row["POPULATION"])` sans gérer `POPULATION="invalide"` : une ligne invalide doit être isolée.
- Filtrer avec `row["continent"]` alors que la clé réelle est `CONTINENT`.
- Mélanger `csv.reader` et `csv.DictReader` sans expliquer pourquoi on choisit l'un ou l'autre.

## Cas limites
- Fichier vide : aucune ligne ne doit être traitée comme pays.
- En-tête incomplet : sans `POPULATION`, la conversion numérique est impossible.
- Ligne invalide : `Erreur,NA,Europe,invalide` va dans les rejets.
- Sélection vide : filtrer `CONTINENT == "Océanie"` dans un extrait qui n'en contient pas donne `[]`.
- Égalité de population : le troisième critère `PAYS` stabilise le tri.

## Mini-exercices
### Mini-exercice 1
Donner le dictionnaire obtenu avec `csv.DictReader` pour `Albanie,Tirana,Europe,3063320`.

### Mini-exercice 2
Dans l'extrait Allemagne, Albanie, Brésil, écrire la liste des pays obtenue après filtrage `CONTINENT == "Europe"`.

### Mini-exercice 3
Comparer le résultat de `sorted(["100", "20", "3"])` et de `sorted([100, 20, 3])`.

### Mini-exercice 4
Dire ce que doit produire `int(row["POPULATION"])` si `row["POPULATION"] == "invalide"`.

### Mini-exercice 5
Écrire la clé de tri pour classer par continent puis population décroissante.

### Mini-exercice 6
Associer P-TABLE-01 à l'étape d'import avec `csv.DictReader`, puis P-TABLE-02 à l'étape de filtrage Europe et de tri numérique.

## Réponses rapides
1. `{"PAYS": "Albanie", "CAPITALE": "Tirana", "CONTINENT": "Europe", "POPULATION": "3063320"}`.
2. `["Allemagne", "Albanie"]`.
3. Tri lexicographique : `["100", "20", "3"]`; tri numérique : `[3, 20, 100]`.
4. La conversion lève `ValueError`; la ligne est ajoutée à la liste des rejets.
5. `key=lambda row: (row["CONTINENT"], -row["POPULATION"], row["PAYS"])`, après conversion de `POPULATION`.
6. P-TABLE-01 correspond à l’import et au parcours de table avec `csv.DictReader`; P-TABLE-02 correspond au filtrage, à la conversion numérique, au tri et à la recherche dans la table.

## À retenir
- `csv.reader` donne des listes ; `csv.DictReader` donne des dictionnaires.
- Les champs de P05 sont `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`.
- `int(row["POPULATION"])` est obligatoire avant un calcul ou un tri numérique.
- Le tri lexicographique trie des chaînes, pas des nombres.
- Le tri numérique compare des entiers.
- Une ligne invalide doit être isolée avant de produire un résultat.
- P-TABLE-01 et P-TABLE-02 restent en `needs_review` : cette fiche aide à réviser mais ne prouve aucune couverture publiable.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | P05-S1 | prête | lecture de `pays_monde.csv` avec `csv.reader` et `csv.DictReader` |
| TD | 03_progressions/supports/premiere/P05/P05_td_tables_csv.md | existant | exercices sur filtre Europe, conversion et ligne invalide |
| TP | 03_progressions/supports/premiere/P05/P05_tp_tables_csv.md | existant | fonctions `charger_pays_csv`, `filtrer_par_continent`, `convertir_populations`, `trier_par_continent_population` |
| Évaluation | 03_progressions/supports/premiere/P05/P05_evaluation_tables_csv.md | existant | questions sur P-TABLE-01 et P-TABLE-02 |

## Auto-évaluation
- Je sais expliquer la différence entre `csv.reader` et `csv.DictReader`.
- Je sais lire une ligne Allemagne ou Albanie dans `pays_monde.csv`.
- Je sais convertir `POPULATION` avec `int(row["POPULATION"])`.
- Je sais dire pourquoi un tri lexicographique peut être faux pour des populations.
- Je sais isoler une ligne invalide au lieu de produire un résultat arbitraire.
- Je sais relier P-TABLE-01 à l'import et P-TABLE-02 au filtrage ou au tri.


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
