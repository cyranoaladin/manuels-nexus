---
title: "T10 - TD - SELECT, WHERE, JOIN et ORDER BY"
level: "terminale"
sequence_id: "T10"
document_type: "td"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Requêtes SQL de lecture"
private_data: false
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03B"
    - "T-BDD-03C"
    - "T-BDD-03D"
    - "T-BDD-03E"
---

# T10 - TD - SELECT, WHERE, JOIN et ORDER BY

## Objectif et organisation

Construire et contrôler des requêtes de lecture sur une base relationnelle. Durée indicative : 55 minutes. Les exercices 1 et 2 constituent le socle ; les exercices 3 à 5 relèvent du niveau standard ; l'exercice 6 est un transfert approfondi.

Pour chaque requête écrite, le livrable comprend : la requête SQL complète, le résultat exact sous forme de tableau et une phrase justifiant au moins une clause.

## Base de référence

### `Eleve`

| id_eleve | nom | classe |
|---:|---|---|
| 1 | Ada | T1 |
| 2 | Linus | T2 |
| 3 | Grace | T1 |
| 4 | Alan | T2 |

### `Note`

| id_note | id_eleve | matiere | note |
|---:|---:|---|---:|
| 10 | 1 | NSI | 17 |
| 11 | 2 | NSI | 13 |
| 12 | 3 | NSI | 15 |
| 13 | 1 | MATHS | 14 |
| 14 | 4 | NSI | 9 |
| 15 | 3 | MATHS | 18 |

## Exercices

### Exercice 1 — Lire et annoter une requête [socle, 6 min]

Capacités : `T-BDD-03A`, `T-BDD-03E`.

```sql
SELECT nom, classe
FROM Eleve
WHERE classe = 'T2'
ORDER BY nom ASC;
```

1. Recopier la requête et annoter le rôle de chaque clause.
2. Donner le résultat exact.
3. Dire si la table `Eleve` a été modifiée.

**Livrable.** Une requête annotée, un tableau à deux colonnes et une phrase de conclusion.

### Exercice 2 — Tracer un filtre [socle, 8 min]

Capacité : `T-BDD-03C`.

On cherche les notes strictement inférieures à 15.

1. Compléter la table de trace suivante pour chacune des six lignes de `Note`.

| id_note | note | `note < 15` | ligne conservée ? |
|---:|---:|---|---|
| 10 | 17 |  |  |
| 11 | 13 |  |  |
| 12 | 15 |  |  |
| 13 | 14 |  |  |
| 14 | 9 |  |  |
| 15 | 18 |  |  |

2. Écrire la requête qui affiche `id_note` et `note` pour ces lignes, dans l'ordre croissant des notes.
3. Expliquer pourquoi la ligne de note 15 n'apparaît pas.

**Livrable.** Table de trace, requête et résultat exact.

### Exercice 3 — Écrire une projection filtrée [standard, 8 min]

Capacités : `T-BDD-03B`, `T-BDD-03C`, `T-BDD-03E`.

Le professeur veut les identifiants des élèves de T1, classés du plus grand au plus petit identifiant.

1. Écrire la requête complète.
2. Prévoir le résultat exact.
3. Indiquer quelle partie changer pour obtenir les élèves de T2 sans modifier les colonnes affichées.

**Livrable.** Requête, tableau de résultat et modification locale explicitée.

### Exercice 4 — Construire une jointure et suivre une ligne [standard, 12 min]

Capacités : `T-BDD-03A`, `T-BDD-03C`, `T-BDD-03D`.

On veut afficher le nom, la matière et la note pour toutes les notes d'Ada.

1. Nommer les colonnes qui permettent de relier `Eleve` et `Note`.
2. Écrire une requête avec `JOIN ... ON` et `WHERE`.
3. Suivre la ligne `Note(13, 1, 'MATHS', 14)` : à quelle ligne de `Eleve` est-elle associée ? pourquoi est-elle conservée ?
4. Donner le résultat exact, trié par matière.

**Livrable.** Clé de jointure justifiée, requête, trace d'une ligne et résultat.

### Exercice 5 — Déboguer une requête [standard, 10 min]

Capacité : `T-BDD-03D`.

Un élève propose :

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_note
WHERE Note.matiere = 'NSI';
```

1. La syntaxe peut être acceptée, mais le résultat est vide avec les données fournies. Expliquer précisément pourquoi.
2. Corriger uniquement la clause fautive.
3. Donner le nombre de lignes du résultat corrigé.
4. Expliquer ce qui pourrait se produire si la clause `ON` était entièrement omise.

**Livrable.** Diagnostic fondé sur le sens des identifiants, clause corrigée et nombre de lignes.

### Exercice 6 — Transfert : préparer un tableau d'honneur [approfondissement, 11 min]

Capacités : `T-BDD-03B` à `T-BDD-03E`.

Le tableau d'honneur doit afficher les élèves ayant une note au moins égale à 15, toutes matières confondues. Pour chaque ligne, afficher `nom`, `matiere` et `note`. Classer d'abord par note décroissante, puis par nom alphabétique en cas d'égalité.

1. Écrire la requête complète.
2. Donner les trois lignes du résultat dans l'ordre exact.
3. Justifier les deux critères de `ORDER BY`.
4. Cas limite : si Alan obtenait aussi 18 en NSI, à quel endroit sa ligne apparaîtrait-elle ?

**Livrable.** Requête, résultat exact, justification du tri et décision sur le cas limite.

## Corrigé intégré enseignant

### Corrigé exercice 1

- **Méthode** : `SELECT` projette, `FROM` choisit la table, `WHERE` filtre T2 et `ORDER BY` trie.
- **Résultat** : la requête fournie renvoie `(Alan, T2)` puis `(Linus, T2)` sans modifier `Eleve`.
- **Contrôle** : l'ordre alphabétique place Alan avant Linus ; une requête `SELECT` ne change aucune ligne.

### Corrigé exercice 2

```sql
SELECT id_note, note FROM Note WHERE note < 15 ORDER BY note ASC;
```

Résultat : `(14, 9)`, `(11, 13)`, `(13, 14)`. La note 15 est exclue car `15 < 15` est faux ; c'est le contrôle de la valeur frontière.

| id_note | note | `note < 15` | ligne conservée ? |
|---:|---:|---|---|
| 10 | 17 | faux | non |
| 11 | 13 | vrai | oui |
| 12 | 15 | faux | non |
| 13 | 14 | vrai | oui |
| 14 | 9 | vrai | oui |
| 15 | 18 | faux | non |

La table de trace applique la condition à chaque ligne avant le tri. `ORDER BY note ASC` réordonne ensuite les trois lignes conservées ; il ne change pas le résultat du filtre.

### Corrigé exercice 3

```sql
SELECT id_eleve FROM Eleve WHERE classe = 'T1' ORDER BY id_eleve DESC;
```

Résultat : `3`, puis `1`. Pour T2, seule la valeur de la condition devient `'T2'` ; la projection reste `id_eleve`.

La méthode consiste à séparer les trois décisions : `SELECT id_eleve` fixe l'unique colonne du résultat, `WHERE classe = 'T1'` conserve Ada et Grace, puis `ORDER BY id_eleve DESC` place l'identifiant 3 avant l'identifiant 1. Changer la classe ne doit donc modifier ni la projection ni le tri.

### Corrigé exercice 4

```sql
SELECT Eleve.nom, Note.matiere, Note.note
FROM Eleve JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Eleve.nom = 'Ada' ORDER BY Note.matiere ASC;
```

Résultat : `(Ada, MATHS, 14)` puis `(Ada, NSI, 17)`. La note 13 rejoint Ada parce que les deux valeurs `id_eleve` valent 1.

Le raisonnement se fait en deux temps : `ON Eleve.id_eleve = Note.id_eleve` associe chaque note à son propriétaire, puis `WHERE Eleve.nom = 'Ada'` élimine les associations des autres élèves. Le contrôle du résultat retrouve exactement les deux lignes de `Note` dont `id_eleve` vaut 1.

### Corrigé exercice 5

La clause fautive compare un identifiant d'élève à un identifiant de note. Elle devient :

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.matiere = 'NSI';
```

La requête corrigée renvoie quatre lignes : `(Ada, 17)`, `(Linus, 13)`, `(Grace, 15)` et `(Alan, 9)`. Avec la mauvaise égalité, aucun `id_eleve` compris entre 1 et 4 n'est égal à un `id_note` compris entre 10 et 15 : le résultat est donc vide. Sans condition de jointure, un produit cartésien de 4 × 6, soit 24 associations, peut être produit avant le filtre sur la matière.

### Corrigé exercice 6

```sql
SELECT Eleve.nom, Note.matiere, Note.note
FROM Eleve JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.note >= 15
ORDER BY Note.note DESC, Eleve.nom ASC;
```

Résultat : `(Grace, MATHS, 18)`, `(Ada, NSI, 17)`, `(Grace, NSI, 15)`. Si Alan avait 18, le second tri le placerait avant Grace.

## Différenciation

### Aides graduées

- Aide 1 : souligner dans l'énoncé les noms des colonnes à afficher.
- Aide 2 : écrire le squelette `SELECT ... FROM ... JOIN ... ON ... WHERE ... ORDER BY ...` puis supprimer les clauses inutiles.
- Aide 3 : pour `ON`, compléter la phrase « une note appartient à un élève lorsque ... ».

### Prolongement pour les élèves rapides

Écrire une seconde requête qui affiche uniquement les noms, sans doublon, des élèves ayant au moins une note supérieure ou égale à 15. `DISTINCT` est un approfondissement explicitement signalé : expliquer le besoin avant d'utiliser ce mot-clé.

## Erreurs fréquentes à diagnostiquer

- **Erreur fréquente 1 — filtrer avant de relier mentalement les tables.** Un élève cherche `nom` dans `Note`. Antidote : écrire au-dessus de chaque colonne la table qui la possède, puis construire `JOIN ... ON` avant `WHERE`.
- **Erreur fréquente 2 — lire `ORDER BY` comme un filtre.** Le nombre de lignes ne change pas quand on trie. Antidote : compter d'abord les lignes conservées par `WHERE`, puis seulement les ordonner.

## Critères de réussite

- Les colonnes de `SELECT` correspondent exactement au résultat demandé.
- La condition `WHERE` est testée sur les valeurs frontières.
- La jointure utilise `Eleve.id_eleve = Note.id_eleve` et cette égalité est justifiée par le sens des colonnes.
- Le tableau annoncé contient exactement les lignes produites par la requête.
