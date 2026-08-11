---
title: "T10 - Corrigé - Requêtes SQL de lecture et de modification"
level: "terminale"
sequence_id: "T10"
document_type: "corrige"
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

# T10 - Corrigé - Requêtes SQL de lecture et de modification

Les requêtes sont écrites pour le schéma `Eleve(id_eleve, nom, classe)` et `Note(id_note, id_eleve, matiere, note)`. D'autres mises en forme sont acceptables si elles produisent exactement les mêmes lignes et respectent la consigne.

## Corrigé du TD `SELECT`, `WHERE`, `JOIN`, `ORDER BY`

### Exercice 1 — Lire et annoter

- `SELECT nom, classe` choisit les deux colonnes affichées.
- `FROM Eleve` indique la table lue.
- `WHERE classe = 'T2'` conserve Alan et Linus.
- `ORDER BY nom ASC` les place dans l'ordre alphabétique.

| nom | classe |
|---|---|
| Alan | T2 |
| Linus | T2 |

La base n'est pas modifiée : `SELECT` construit seulement un résultat.

**Erreur typique.** Répondre Ada puis Grace revient à filtrer T1 au lieu de T2. L'antidote consiste à évaluer la condition sur chaque ligne avant de trier.

### Exercice 2 — Tracer un filtre

| id_note | note | `note < 15` | ligne conservée ? |
|---:|---:|---|---|
| 10 | 17 | faux | non |
| 11 | 13 | vrai | oui |
| 12 | 15 | faux | non |
| 13 | 14 | vrai | oui |
| 14 | 9 | vrai | oui |
| 15 | 18 | faux | non |

```sql
SELECT id_note, note
FROM Note
WHERE note < 15
ORDER BY note ASC;
```

Résultat : `(14, 9)`, `(11, 13)`, `(13, 14)`. La note 15 est exclue parce que `15 < 15` est faux. Avec `<= 15`, la ligne 12 serait aussi conservée.

### Exercice 3 — Projection filtrée

```sql
SELECT id_eleve
FROM Eleve
WHERE classe = 'T1'
ORDER BY id_eleve DESC;
```

Résultat : `(3)`, puis `(1)`. Pour obtenir T2, on ne change que la valeur du filtre : `WHERE classe = 'T2'`.

**Variante acceptable.** Qualifier la colonne par `Eleve.id_eleve` ne change pas le résultat.

### Exercice 4 — Jointure et suivi d'une ligne

Les colonnes de même sens sont `Eleve.id_eleve` et `Note.id_eleve`.

```sql
SELECT Eleve.nom, Note.matiere, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Eleve.nom = 'Ada'
ORDER BY Note.matiere ASC;
```

La ligne `Note(13, 1, 'MATHS', 14)` porte `id_eleve = 1`. Elle est associée à `Eleve(1, 'Ada', 'T1')`, puis conservée car le nom joint vaut Ada.

| nom | matiere | note |
|---|---|---:|
| Ada | MATHS | 14 |
| Ada | NSI | 17 |

**Cas limite.** Si Ada n'avait aucune note, cette jointure interne ne produirait aucune ligne pour elle.

### Exercice 5 — Débogage

`Eleve.id_eleve` vaut 1, 2, 3 ou 4, tandis que `Note.id_note` vaut 10 à 15. Ces identifiants décrivent des objets différents et aucune valeur n'est égale : le résultat est vide.

Clause corrigée :

```sql
JOIN Note ON Eleve.id_eleve = Note.id_eleve
```

La requête corrigée produit six lignes, une par note. Sans `ON`, un produit cartésien peut associer chacun des quatre élèves aux six notes, soit 24 lignes non pertinentes.

### Exercice 6 — Tableau d'honneur

```sql
SELECT Eleve.nom, Note.matiere, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.note >= 15
ORDER BY Note.note DESC, Eleve.nom ASC;
```

| nom | matiere | note |
|---|---|---:|
| Grace | MATHS | 18 |
| Ada | NSI | 17 |
| Grace | NSI | 15 |

Le premier critère classe les notes ; le second rend prévisible l'ordre entre deux notes égales. Si Alan obtenait 18 en NSI, sa ligne apparaîtrait avant celle de Grace car `Alan` précède `Grace`.

## Corrigé du TD `INSERT`, `UPDATE`, `DELETE`

### Exercice 1 — Choisir l'opération

| Intention | Opération | Modification ? | Justification |
|---|---|---|---|
| afficher les notes de Grace | `SELECT` | non | on construit un résultat |
| enregistrer une nouvelle note | `INSERT` | oui | une ligne est ajoutée |
| corriger la note 11 | `UPDATE` | oui | une valeur existante change |
| retirer la ligne 14 | `DELETE` | oui | une ligne disparaît |
| afficher les notes de NSI au moins égales à 15 | `SELECT` avec `WHERE` | non | le filtre agit sur le résultat |

### Exercice 2 — Insérer

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note)
VALUES (16, 2, 'MATHS', 16);

SELECT id_note, id_eleve, matiere, note
FROM Note
WHERE id_note = 16;
```

Résultat du contrôle : `(16, 2, 'MATHS', 16)`. L'identifiant 10 est déjà la clé primaire d'une autre note : le réutiliser violerait l'unicité.

**Erreur typique.** Inverser `id_note` et `id_eleve` peut produire une ligne syntaxiquement valide mais fausse. Vérifier l'alignement colonne/valeur avant exécution.

### Exercice 3 — Mettre à jour une seule note

```sql
SELECT id_note, note FROM Note WHERE id_note = 11;
UPDATE Note SET note = 16 WHERE id_note = 11;
SELECT id_note, note FROM Note WHERE id_note = 11;
```

Avant : `(11, 13)`. Après : `(11, 16)`. Les autres lignes restent inchangées. `WHERE id_eleve = 2` ciblerait toutes les notes de Linus dans une base plus complète ; la clé primaire `id_note = 11` désigne sans ambiguïté une seule note.

### Exercice 4 — Supprimer une ligne ciblée

```sql
SELECT * FROM Note WHERE id_note = 14;
DELETE FROM Note WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;
```

Avant : `(14, 4, 'NSI', 9)`. Après : aucune ligne. Il reste cinq lignes dans `Note`.

### Exercice 5 — Requêtes dangereuses

`UPDATE Note SET note = 12;` modifie les six lignes : toutes les notes deviennent 12. `DELETE FROM Note WHERE matiere = 'NSI';` supprime les quatre lignes 10, 11, 12 et 14.

Corrections :

```sql
SELECT * FROM Note WHERE id_note = 14;
UPDATE Note SET note = 12 WHERE id_note = 14;

SELECT * FROM Note WHERE id_note = 11;
DELETE FROM Note WHERE id_note = 11;
```

**Réponse partielle acceptable.** `WHERE id_eleve = 2 AND matiere = 'NSI'` cible aussi une seule ligne dans la base fournie, mais `id_note = 11` exprime plus directement l'identité de la ligne.

### Exercice 6 — Campagne de corrections

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note)
VALUES (16, 4, 'MATHS', 12);
SELECT * FROM Note WHERE id_note = 16;

UPDATE Note SET note = 10 WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;

DELETE FROM Note WHERE id_note = 13;
SELECT * FROM Note WHERE id_note = 13;
```

Contrôles successifs : `(16, 4, 'MATHS', 12)`, puis `(14, 4, 'NSI', 10)`, puis aucune ligne pour l'identifiant 13.

État final :

| id_note | id_eleve | matiere | note |
|---:|---:|---|---:|
| 10 | 1 | NSI | 17 |
| 11 | 2 | NSI | 13 |
| 12 | 3 | NSI | 15 |
| 14 | 4 | NSI | 10 |
| 15 | 3 | MATHS | 18 |
| 16 | 4 | MATHS | 12 |

## Corrigé de l'évaluation `SELECT`, `WHERE`, `JOIN`, `ORDER BY`

### Question 1

`SELECT` choisit `nom` et `classe`, `FROM` lit `Eleve`, `WHERE` conserve T2 et `ORDER BY` trie par nom. Résultat :

| nom | classe |
|---|---|
| Alan | T2 |
| Linus | T2 |

La base n'est pas modifiée : aucune instruction d'écriture n'est exécutée.

### Question 2

```sql
SELECT id_note, note
FROM Note
WHERE matiere = 'MATHS' AND note >= 15
ORDER BY note DESC;
```

Résultat : `(15, 18)`. Ada a 14 en mathématiques : sa ligne est exclue.

### Question 3

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.matiere = 'NSI' AND Note.note < 14
ORDER BY Note.note ASC;
```

| nom | note |
|---|---:|
| Alan | 9 |
| Linus | 13 |

Les deux colonnes `id_eleve` ont le même sens : la clé étrangère de `Note` désigne la clé primaire de l'élève.

### Question 4

La mauvaise requête compare des identifiants d'élèves (1 à 4) avec des identifiants de notes (10 à 15), donc aucune association n'est produite. Correction :

```sql
JOIN Note ON Eleve.id_eleve = Note.id_eleve
```

La requête corrigée produit six lignes.

### Question 5

```sql
SELECT Eleve.nom, Note.matiere, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Eleve.classe = 'T1' AND Note.note >= 15
ORDER BY Note.note DESC, Eleve.nom ASC;
```

Résultat : `(Grace, MATHS, 18)`, `(Ada, NSI, 17)`, `(Grace, NSI, 15)`.

## Corrigé de l'évaluation `INSERT`, `UPDATE`, `DELETE`

### Question 1

Afficher : `SELECT`, non modifiant. Enregistrer : `INSERT`, modifiant. Corriger : `UPDATE`, modifiant. Retirer : `DELETE`, modifiant.

### Question 2

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note)
VALUES (16, 4, 'MATHS', 12);
SELECT * FROM Note WHERE id_note = 16;
```

Résultat : `(16, 4, 'MATHS', 12)`.

### Question 3

```sql
SELECT id_note, note FROM Note WHERE id_note = 14;
UPDATE Note SET note = 10 WHERE id_note = 14;
SELECT id_note, note FROM Note WHERE id_note = 14;
```

Avant : `(14, 9)`. Après : `(14, 10)`. Sans `WHERE`, les six notes deviendraient 10.

### Question 4

```sql
SELECT * FROM Note WHERE id_note = 13;
DELETE FROM Note WHERE id_note = 13;
SELECT * FROM Note WHERE id_note = 13;
```

Avant : `(13, 1, 'MATHS', 14)`. Après : aucune ligne. Il reste cinq lignes.

### Question 5

La requête proposée remplace les six notes par 16. Correction et contrôle préalable :

```sql
SELECT id_note, note FROM Note WHERE id_note = 11;
UPDATE Note SET note = 16 WHERE id_note = 11;
```

Le contrôle préalable renvoie `(11, 13)` ; il prouve que la condition cible la bonne ligne.

## Principes de correction

- Les guillemets simples ou doubles autour des chaînes sont acceptés si le dialecte annoncé les accepte ; les guillemets simples restent la forme de référence.
- Une requête incomplète qui exprime la bonne table et la bonne condition reçoit les points correspondants du barème, mais pas les points de requête exécutable.
- Une erreur de tri ne doit pas annuler une jointure correcte.
- Un `UPDATE` ou un `DELETE` sans `WHERE` subit le plafond prévu au barème, même si la syntaxe est correcte, car l'effet obtenu contredit la consigne.
