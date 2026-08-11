---
title: "T10 - Cours - Interroger et modifier une base avec SQL"
level: "terminale"
sequence_id: "T10"
document_type: "cours"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "SQL : SELECT, WHERE, JOIN, ORDER BY, INSERT, UPDATE et DELETE"
private_data: false
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03B"
    - "T-BDD-03C"
    - "T-BDD-03D"
    - "T-BDD-03E"
    - "T-BDD-03F"
    - "T-BDD-03G"
    - "T-BDD-03H"
---

# T10 - Cours - Interroger et modifier une base avec SQL

## Objectifs spécifiques

À la fin de la séquence, l'élève doit pouvoir :

- repérer les clauses d'une requête SQL et expliquer leur rôle (`T-BDD-03A`) ;
- choisir les colonnes affichées avec `SELECT ... FROM` (`T-BDD-03B`) ;
- filtrer les lignes avec une condition booléenne dans `WHERE` (`T-BDD-03C`) ;
- relier deux tables par une clé commune avec `JOIN ... ON` (`T-BDD-03D`) ;
- ordonner un résultat avec `ORDER BY` sans modifier les tables (`T-BDD-03E`) ;
- ajouter une ligne avec `INSERT`, modifier des lignes ciblées avec `UPDATE ... WHERE` et supprimer des lignes ciblées avec `DELETE ... WHERE` (`T-BDD-03F` à `T-BDD-03H`).

## Prérequis

- Lire le schéma d'une relation et reconnaître une clé primaire.
- Comprendre qu'une clé étrangère désigne une ligne d'une autre table.
- Évaluer une condition telle que `note >= 15 AND matiere = 'NSI'`.

## Situation-problème

Le conseil de classe demande trois informations : la liste alphabétique des élèves, les notes de NSI supérieures ou égales à 15 avec le nom de l'élève, puis la correction d'une note saisie par erreur. Les noms et les notes sont stockés dans deux tables différentes. Comment obtenir exactement le résultat demandé sans recopier toute la base, et comment garantir qu'une correction ne modifie pas toutes les notes ?

## Activité d'entrée — 8 minutes

Sans écrire encore de SQL, observer les deux tables de référence.

### Table `Eleve`

| id_eleve | nom | classe |
|---:|---|---|
| 1 | Ada | T1 |
| 2 | Linus | T2 |
| 3 | Grace | T1 |
| 4 | Alan | T2 |

### Table `Note`

| id_note | id_eleve | matiere | note |
|---:|---:|---|---:|
| 10 | 1 | NSI | 17 |
| 11 | 2 | NSI | 13 |
| 12 | 3 | NSI | 15 |
| 13 | 1 | MATHS | 14 |
| 14 | 4 | NSI | 9 |
| 15 | 3 | MATHS | 18 |

1. Entourer les deux colonnes qui permettent de relier une note à un élève.
2. Écrire, sans syntaxe SQL, les étapes nécessaires pour obtenir les notes de NSI au moins égales à 15 avec les noms.
3. Prévoir le résultat exact sous la forme d'un tableau à deux colonnes `nom`, `note`.
4. Expliquer pourquoi la colonne `id_note` ne permet pas de relier directement une note à un élève.

**Mise en commun attendue.** On relie `Eleve.id_eleve` à `Note.id_eleve`, puis on garde les lignes de NSI dont la note vaut au moins 15. Le résultat contient `(Ada, 17)` et `(Grace, 15)`. Relier `Eleve.id_eleve` à `Note.id_note` comparerait deux identifiants qui ne décrivent pas le même objet.

## Définitions et méthode générale

Une requête SQL décrit une opération sur des tables : lire des lignes, en ajouter, modifier des valeurs ou supprimer des lignes. Une clause est une partie de la requête ayant un rôle précis. Pour construire une requête autonome, on suit toujours la même méthode : nommer l'intention, choisir les colonnes du résultat, identifier les tables, écrire les conditions de liaison puis de filtrage, et enfin prévoir le résultat exact avant exécution. Pour une modification, ce dernier contrôle se fait d'abord avec un `SELECT` portant le même `WHERE`.

## 1. Lire une requête : une suite de clauses ayant chacune un rôle

Une **requête SQL** est une instruction adressée au système de gestion de base de données. Dans une requête de lecture :

- `SELECT` indique les colonnes à afficher : c'est la **projection** ;
- `FROM` indique la ou les tables utilisées ;
- `JOIN ... ON` indique comment relier les lignes de deux tables ;
- `WHERE` indique quelles lignes conserver : c'est la **sélection** ;
- `ORDER BY` ordonne le résultat obtenu.

L'ordre d'écriture usuel est :

```sql
SELECT colonnes
FROM table
JOIN autre_table ON condition_de_jointure
WHERE condition_de_filtrage
ORDER BY colonne ASC ou DESC;
```

### Preuve de cours T-BDD-03E — trier un résultat avec `ORDER BY`

`ORDER BY` / `ASC` / `DESC` trie le résultat sans modifier la table : la requête complète `SELECT nom FROM Eleve ORDER BY nom ASC;` renvoie exactement `Ada`, `Alan`, `Grace`, `Linus` ; avec `DESC`, l'ordre serait inversé.

Un second exemple, mis en forme clause par clause, montre comment un tri s'applique après une jointure et comment deux notes égales seraient départagées par ordre alphabétique du nom :

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.matiere = 'NSI'
ORDER BY Note.note DESC, Eleve.nom ASC;
```

Résultat exact :

| nom | note |
|---|---:|
| Ada | 17 |
| Grace | 15 |
| Linus | 13 |
| Alan | 9 |

Le premier critère, `Note.note DESC`, place les notes de la plus grande à la plus petite. Si deux élèves avaient la même note, le second critère, `Eleve.nom ASC`, les classerait par nom croissant. Après cette requête, les quatre lignes de NSI de la table `Note` sont inchangées : seul leur ordre dans ce résultat est fixé.

**Erreurs fréquentes.** Oublier `DESC` produit ici le classement inverse ; croire que `ORDER BY` filtre des lignes confond le tri avec `WHERE` ; croire qu'il réécrit la table confond une requête de lecture avec `UPDATE`.

Toutes les clauses ne sont pas obligatoires. En revanche, si une jointure est utilisée, sa condition `ON` doit dire quelles colonnes représentent la même information.

### Exemple corrigé 1 — projection et tri

**Question.** Afficher le nom et la classe de chaque élève, par ordre alphabétique.

1. Le résultat demande `nom` et `classe` : ces deux colonnes vont dans `SELECT`.
2. Elles appartiennent toutes deux à `Eleve` : cette table va dans `FROM`.
3. L'ordre alphabétique porte sur `nom` : on ajoute `ORDER BY nom ASC`.

```sql
SELECT nom, classe
FROM Eleve
ORDER BY nom ASC;
```

Résultat exact :

| nom | classe |
|---|---|
| Ada | T1 |
| Alan | T2 |
| Grace | T1 |
| Linus | T2 |

**Pourquoi `ORDER BY` ne change-t-il pas la table ?** Il ordonne seulement les lignes du résultat affiché. Une nouvelle requête sans `ORDER BY` n'est pas obligée de conserver cet ordre.

### Non-exemple

```sql
SELECT Eleve
FROM nom;
```

Cette instruction inverse table et colonne : `Eleve` est le nom de la table, `nom` celui d'une colonne.

### Question flash

Dans `SELECT classe FROM Eleve WHERE nom = 'Ada';`, quelle clause choisit la colonne affichée ? quelle clause élimine les autres élèves ?

Réponse : `SELECT classe` choisit la colonne ; `WHERE nom = 'Ada'` filtre les lignes.

## 2. Filtrer avec `WHERE`

`WHERE` conserve seulement les lignes pour lesquelles une condition est vraie. Les opérateurs usuels sont `=`, `<>`, `<`, `<=`, `>`, `>=`, ainsi que `AND`, `OR` et `NOT`.

### Méthode réutilisable — écrire un filtre

1. Écrire d'abord `SELECT` et `FROM` en fonction du résultat demandé.
2. Traduire chaque contrainte de l'énoncé en une condition simple.
3. Relier les conditions par `AND` si elles doivent être vraies ensemble, par `OR` si une seule suffit.
4. Exécuter mentalement la condition ligne par ligne.
5. Vérifier les valeurs frontières, notamment `>=` contre `>`.

### Exemple corrigé 2 — deux conditions

**Question.** Afficher `id_eleve` et `note` pour les notes de NSI au moins égales à 15.

```sql
SELECT id_eleve, note
FROM Note
WHERE matiere = 'NSI' AND note >= 15
ORDER BY note DESC;
```

Trace du filtre :

| id_note | matiere | note | `matiere = 'NSI'` | `note >= 15` | conservée ? |
|---:|---|---:|---|---|---|
| 10 | NSI | 17 | vrai | vrai | oui |
| 11 | NSI | 13 | vrai | faux | non |
| 12 | NSI | 15 | vrai | vrai | oui |
| 13 | MATHS | 14 | faux | faux | non |
| 14 | NSI | 9 | vrai | faux | non |
| 15 | MATHS | 18 | faux | vrai | non |

Résultat exact : `(1, 17)` puis `(3, 15)`.

**Piège.** Remplacer `>= 15` par `> 15` ferait disparaître la note 15 de Grace. L'antidote consiste à tester explicitement la valeur frontière.

## 3. Relier deux tables avec `JOIN ... ON`

Une **jointure** construit des lignes en associant des lignes de deux tables qui satisfont une condition. Ici, `Eleve.id_eleve` est la clé primaire de `Eleve` et `Note.id_eleve` est la clé étrangère qui désigne l'élève concerné.

### Méthode réutilisable — construire une jointure

1. Repérer la colonne demandée dans chaque table.
2. Identifier la clé primaire et la clé étrangère qui décrivent le même élève.
3. Écrire `JOIN Note ON Eleve.id_eleve = Note.id_eleve`.
4. Ajouter le filtre `WHERE` après la jointure si seules certaines associations sont demandées.
5. Contrôler une ligne : la note d'identifiant 10 porte `id_eleve = 1`, donc elle doit être associée à Ada.

### Exemple corrigé 3 — jointure, filtre et tri

**Question.** Afficher le nom et la note des élèves ayant au moins 15 en NSI, de la meilleure note à la moins bonne.

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.matiere = 'NSI' AND Note.note >= 15
ORDER BY Note.note DESC, Eleve.nom ASC;
```

Raisonnement :

1. La projection demande un nom (`Eleve`) et une note (`Note`) : deux tables sont nécessaires.
2. La jointure associe les mêmes valeurs d'`id_eleve`.
3. `WHERE` élimine les autres matières et les notes inférieures à 15.
4. `ORDER BY` place 17 avant 15.

Résultat exact :

| nom | note |
|---|---:|
| Ada | 17 |
| Grace | 15 |

### Contre-exemple — mauvaise clé

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_note;
```

La requête est syntaxiquement plausible, mais les deux identifiants n'ont pas le même sens. Avec les données fournies, aucun `id_eleve` (1 à 4) n'est égal à un `id_note` (10 à 15) : le résultat est vide. L'antidote est de formuler la phrase « la note appartient à l'élève dont les deux `id_eleve` sont égaux » avant d'écrire `ON`.

### Cas limite — jointure sans `ON`

Selon le dialecte SQL, omettre `ON` peut produire toutes les associations possibles : 4 élèves × 6 notes = 24 lignes. Ce produit cartésien ne répond pas à la question « à qui appartient cette note ? ».

## 4. Ajouter une ligne avec `INSERT`

`INSERT` ajoute une nouvelle ligne. Les colonnes et les valeurs doivent être dans le même ordre.

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note)
VALUES (16, 2, 'MATHS', 16);
```

Après l'insertion, la ligne `(16, 2, 'MATHS', 16)` existe. Une vérification ciblée est :

```sql
SELECT id_note, id_eleve, matiere, note
FROM Note
WHERE id_note = 16;
```

**Pièges.** Réutiliser `id_note = 10` viole l'unicité de la clé primaire. Utiliser `id_eleve = 8` crée une référence vers un élève absent si l'intégrité référentielle est activée.

## 5. Modifier des lignes avec `UPDATE ... WHERE`

`UPDATE` change une ou plusieurs valeurs dans les lignes ciblées par `WHERE`.

### Méthode de modification sûre

1. Écrire un `SELECT` avec le futur `WHERE` pour voir les lignes ciblées.
2. Vérifier que le nombre et l'identité des lignes correspondent à l'intention.
3. Remplacer `SELECT ... FROM` par `UPDATE ... SET`, en conservant exactement le même `WHERE`.
4. Exécuter un nouveau `SELECT` pour contrôler le résultat.

**Exemple.** La note 11 a été saisie 13 au lieu de 16.

```sql
SELECT id_note, note FROM Note WHERE id_note = 11;
UPDATE Note SET note = 16 WHERE id_note = 11;
SELECT id_note, note FROM Note WHERE id_note = 11;
```

Avant : `(11, 13)`. Après : `(11, 16)`. Les cinq autres notes sont inchangées.

### Contre-exemple dangereux

```sql
UPDATE Note SET note = 16;
```

Sans `WHERE`, les six notes deviennent 16. L'antidote est la règle « pas d'`UPDATE` avant d'avoir exécuté le `SELECT` de contrôle ».

## 6. Supprimer des lignes avec `DELETE ... WHERE`

`DELETE FROM` supprime les lignes qui satisfont `WHERE`. Il ne supprime pas seulement la valeur d'une cellule.

**Exemple.** La note d'identifiant 14 est un essai à retirer.

```sql
SELECT * FROM Note WHERE id_note = 14;
DELETE FROM Note WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;
```

Le premier `SELECT` renvoie `(14, 4, 'NSI', 9)`. Le second ne renvoie aucune ligne : la suppression a bien été ciblée.

### Contre-exemple dangereux

```sql
DELETE FROM Note;
```

Sans `WHERE`, toutes les lignes de `Note` sont supprimées. En pratique, une transaction permet de revenir en arrière avant validation ; au niveau du programme, il faut surtout savoir contrôler la cible et expliquer le risque.

## 7. Choisir la bonne opération

| Intention | Opération principale | La table est-elle modifiée ? |
|---|---|---|
| Afficher des données | `SELECT` | non |
| Ne conserver que certaines lignes du résultat | `WHERE` dans un `SELECT` | non |
| Associer des données de deux tables | `JOIN ... ON` dans un `SELECT` | non |
| Ajouter une ligne | `INSERT` | oui |
| Changer une valeur existante | `UPDATE ... WHERE` | oui |
| Retirer une ou plusieurs lignes | `DELETE ... WHERE` | oui |

## Erreurs fréquentes et antidotes

| Erreur spécifique | Effet | Antidote |
|---|---|---|
| Employer `UPDATE` pour simplement afficher une note | la base est modifiée inutilement | commencer par le verbe de l'intention : « afficher » implique `SELECT` |
| Confondre `WHERE` et `ORDER BY` | les lignes sont triées mais pas filtrées | écrire la condition booléenne puis la tester sur chaque ligne |
| Joindre `Eleve.id_eleve` à `Note.id_note` | associations fausses ou résultat vide | vérifier que les deux colonnes ont le même sens |
| Oublier `WHERE` dans `UPDATE` | toutes les lignes sont modifiées | exécuter d'abord le `SELECT` de contrôle |
| Oublier `WHERE` dans `DELETE` | toutes les lignes sont supprimées | annoncer par écrit les lignes qui doivent disparaître |

### Erreur fréquente 1 — choisir une instruction qui ne correspond pas à l'intention

Un élève lit « corriger l'affichage de la note 11 » et écrit immédiatement `UPDATE`. Il faut d'abord séparer les intentions : si la valeur stockée est fausse, `UPDATE` convient ; si seule la présentation est demandée, la base ne doit pas changer et il faut un `SELECT`. L'antidote est la question de contrôle : « l'état de la table doit-il être différent après l'instruction ? »

### Erreur fréquente 2 — écrire la jointure d'après le nom des colonnes sans vérifier leur sens

`Note.id_note` et `Eleve.id_eleve` sont tous deux des identifiants, mais ils n'identifient pas le même objet. La clé étrangère `Note.id_eleve` désigne le propriétaire de la note : c'est elle qu'il faut comparer à `Eleve.id_eleve`. L'antidote consiste à lire la condition `ON` comme une phrase : « cette note appartient à cet élève lorsque leurs identifiants d'élève sont égaux ».

## Différenciation

### Appui — réduire la charge sans supprimer l'objectif

- Surligner d'une couleur les colonnes demandées, d'une autre les conditions.
- Utiliser des étiquettes mobiles `SELECT`, `FROM`, `JOIN`, `ON`, `WHERE`, `ORDER BY` avant de recopier la requête.
- Pour une jointure, compléter la phrase « la ligne de `Note` appartient à la ligne de `Eleve` lorsque ... ».

### Standard

- Écrire la requête complète, prévoir le résultat exact puis vérifier chaque ligne.
- Pour `UPDATE` et `DELETE`, fournir le `SELECT` de contrôle avant et après.

### Approfondissement

- Écrire une requête qui affiche, par ordre décroissant, toutes les notes d'Ada avec leur matière.
- Expliquer pourquoi deux notes égales nécessitent un second critère de tri si l'on veut un ordre entièrement prévisible.

## Critères de révision et auto-vérification

1. Puis-je dire, sans exemple, ce que choisissent `SELECT`, `FROM` et `WHERE` ?
2. Puis-je justifier la clé de jointure par le sens des colonnes ?
3. Puis-je prévoir le résultat exact d'une requête sur les tables fournies ?
4. Avant un `UPDATE` ou un `DELETE`, ai-je écrit le `SELECT` qui contrôle la cible ?

## Lien avec le programme

| Capacité | Preuve dans ce cours |
|---|---|
| T-BDD-03A | lecture et ordre des clauses d'une requête |
| T-BDD-03B | exemple travaillé de projection |
| T-BDD-03C | méthode et table de trace d'un filtre |
| T-BDD-03D | construction et contre-exemple de jointure |
| T-BDD-03E | tri alphabétique et tri décroissant |
| T-BDD-03F | insertion puis vérification ciblée |
| T-BDD-03G | protocole sûr d'`UPDATE ... WHERE` |
| T-BDD-03H | protocole sûr de `DELETE ... WHERE` et risque associé |
