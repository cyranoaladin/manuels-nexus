---
title: "T10 - TD - INSERT, UPDATE et DELETE"
level: "terminale"
sequence_id: "T10"
document_type: "td"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Requêtes SQL de modification"
private_data: false
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03F"
    - "T-BDD-03G"
    - "T-BDD-03H"
---

# T10 - TD - INSERT, UPDATE et DELETE

## Objectif et règle de travail

Choisir et sécuriser une opération de modification. Durée indicative : 55 minutes. Sauf indication contraire, chaque exercice repart de la base initiale ci-dessous : les modifications d'un exercice ne se cumulent pas avec le suivant.

Pour `UPDATE` et `DELETE`, le livrable doit toujours contenir : le `SELECT` de contrôle avant, la requête de modification, le `SELECT` de contrôle après et les lignes exactes obtenues.

## Base initiale

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

### Exercice 1 — Choisir l'opération [socle, 6 min]

Capacité : `T-BDD-03A`.

Pour chaque intention, choisir parmi `SELECT`, `INSERT`, `UPDATE`, `DELETE` et justifier en une phrase.

1. Afficher les notes de Grace.
2. Enregistrer une nouvelle note de mathématiques pour Linus.
3. Corriger la valeur de la note 11.
4. Retirer la ligne 14, créée pendant un essai.
5. Afficher seulement les notes de NSI au moins égales à 15.

**Livrable.** Tableau `intention / opération / la base est-elle modifiée ? / justification`.

### Exercice 2 — Insérer une ligne [socle, 8 min]

Capacité : `T-BDD-03F`.

Linus obtient 16 en mathématiques. La nouvelle note doit avoir l'identifiant 16.

1. Écrire l'instruction `INSERT` en nommant les quatre colonnes.
2. Écrire le `SELECT` qui vérifie uniquement la ligne 16.
3. Donner le résultat exact de ce contrôle.
4. Expliquer pourquoi remplacer l'identifiant 16 par 10 provoquerait une erreur.

**Livrable.** `INSERT`, requête de contrôle, ligne obtenue et explication sur la clé primaire.

### Exercice 3 — Corriger une seule note [standard, 10 min]

Capacité : `T-BDD-03G`.

La note d'identifiant 11 vaut 16 et non 13.

1. Écrire le `SELECT` de contrôle avant modification.
2. Écrire un `UPDATE` qui ne modifie que cette ligne.
3. Réutiliser le contrôle après modification et donner les résultats avant/après.
4. Justifier pourquoi `WHERE id_eleve = 2` serait moins précis dans une base où Linus peut avoir plusieurs notes.

**Livrable.** Trois requêtes, deux états et justification du choix de la clé.

### Exercice 4 — Supprimer une ligne ciblée [standard, 9 min]

Capacité : `T-BDD-03H`.

La note 14 est une donnée d'essai à supprimer.

1. Écrire le `SELECT` qui annonce exactement la ligne supprimée.
2. Écrire le `DELETE` ciblé.
3. Écrire le contrôle après suppression et prévoir son résultat.
4. Indiquer combien de lignes restent dans `Note`.

**Livrable.** Contrôle avant, suppression, contrôle après, résultat vide et nombre de lignes restantes.

### Exercice 5 — Analyser deux requêtes dangereuses [standard, 10 min]

Capacités : `T-BDD-03G`, `T-BDD-03H`.

```sql
UPDATE Note SET note = 12;
DELETE FROM Note WHERE matiere = 'NSI';
```

1. Pour chaque requête, annoncer précisément les lignes touchées sur la base initiale.
2. La première intention était de corriger uniquement la note 14 à 12 : écrire la requête sûre.
3. La seconde intention était de supprimer uniquement la note de NSI de Linus : écrire une condition qui cible une seule ligne.
4. Écrire pour chaque correction le `SELECT` préalable qui aurait révélé l'erreur de portée.

**Livrable.** Diagnostic quantifié, deux requêtes corrigées et deux contrôles préalables.

### Exercice 6 — Transfert : traiter une campagne de corrections [approfondissement, 12 min]

Capacités : `T-BDD-03F` à `T-BDD-03H`.

Les trois opérations suivantes doivent être appliquées dans cet ordre sur une même copie de la base :

1. ajouter `Note(16, 4, 'MATHS', 12)` ;
2. corriger la note 14 de 9 à 10 ;
3. supprimer la note 13.

Écrire les trois instructions. Après chacune, écrire un `SELECT` ciblé qui prouve l'effet obtenu. Enfin, prévoir le contenu de :

```sql
SELECT id_note, id_eleve, matiere, note
FROM Note
ORDER BY id_note ASC;
```

**Livrable.** Trois modifications, trois contrôles et la table finale ordonnée contenant six lignes.

## Corrigé intégré enseignant

### Corrigé exercice 1

| Intention | Opération | Base modifiée ? | Justification observable |
|---|---|---|---|
| afficher les notes de Grace | `SELECT` | non | on lit des lignes existantes. |
| enregistrer la note de Linus | `INSERT` | oui | une nouvelle ligne est ajoutée. |
| corriger la note 11 | `UPDATE` | oui | une valeur d'une ligne existante change. |
| retirer la ligne 14 | `DELETE` | oui | une ligne existante disparaît. |
| afficher les notes de NSI au moins égales à 15 | `SELECT ... WHERE` | non | la condition filtre une lecture. |

Le contrôle consiste à repérer le verbe d'action puis à demander si l'état de la table doit changer. Le résultat attendu distingue ainsi les deux lectures des trois modifications ; choisir `UPDATE` pour « afficher » confondrait observation et transformation.

### Corrigé exercice 2

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note) VALUES (16, 2, 'MATHS', 16);
SELECT * FROM Note WHERE id_note = 16;
```

Le contrôle renvoie `(16, 2, MATHS, 16)`. Réutiliser 10 viole l'unicité de la clé primaire `id_note`.

La liste des colonnes et la liste des valeurs ont le même ordre : 16 devient l'identifiant de note, 2 relie la ligne à Linus, `MATHS` est la matière et 16 la note. Le `SELECT` final isole l'identifiant 16 ; obtenir exactement une ligne prouve que l'insertion a porté sur la donnée voulue.

### Corrigé exercice 3

```sql
SELECT id_note, note FROM Note WHERE id_note = 11;
UPDATE Note SET note = 16 WHERE id_note = 11;
SELECT id_note, note FROM Note WHERE id_note = 11;
```

Avant : `(11, 13)` ; après : `(11, 16)`. La clé `id_note` cible une ligne, contrairement à un simple `id_eleve` potentiellement partagé.

La méthode réutilise exactement le même filtre avant et après la modification. Le premier résultat établit l'état initial ; `UPDATE ... WHERE id_note = 11` ne change que la colonne `note` de cette ligne ; le second résultat vérifie à la fois la nouvelle valeur et la conservation de l'identifiant.

### Corrigé exercice 4

```sql
SELECT * FROM Note WHERE id_note = 14;
DELETE FROM Note WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;
```

Le premier contrôle renvoie la ligne 14, le second aucun résultat. Il reste cinq lignes dans `Note`.

La condition `WHERE id_note = 14` est d'abord testée par le `SELECT` : une seule ligne est annoncée. Après `DELETE`, la même condition doit produire un résultat vide ; si elle renvoyait encore une ligne, la suppression n'aurait pas atteint la cible.

### Corrigé exercice 5

Le premier `UPDATE` touche les six lignes de `Note`, alors que l'intention n'en vise qu'une. Le `DELETE` touche les quatre notes de NSI, d'identifiants 10, 11, 12 et 14, alors que seule la note de Linus doit disparaître.

```sql
SELECT * FROM Note WHERE id_note = 14;
UPDATE Note SET note = 12 WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;

SELECT * FROM Note WHERE id_note = 11;
DELETE FROM Note WHERE id_note = 11;
SELECT * FROM Note WHERE id_note = 11;
```

Pour la correction de la note 14, les contrôles renvoient d'abord `(14, 4, NSI, 9)`, puis `(14, 4, NSI, 12)`. Pour la suppression, le contrôle renvoie d'abord `(11, 2, NSI, 13)`, puis un résultat vide. L'erreur traitée est l'absence de condition assez sélective : le `SELECT` préalable quantifie sa portée avant toute modification.

### Corrigé exercice 6

```sql
INSERT INTO Note(id_note, id_eleve, matiere, note) VALUES (16, 4, 'MATHS', 12);
SELECT * FROM Note WHERE id_note = 16;
UPDATE Note SET note = 10 WHERE id_note = 14;
SELECT * FROM Note WHERE id_note = 14;
DELETE FROM Note WHERE id_note = 13;
SELECT * FROM Note WHERE id_note = 13;
```

Les contrôles ciblés renvoient successivement `(16, 4, MATHS, 12)`, `(14, 4, NSI, 10)`, puis aucun résultat pour 13. La table finale ordonnée est :

| id_note | id_eleve | matiere | note |
|---:|---:|---|---:|
| 10 | 1 | NSI | 17 |
| 11 | 2 | NSI | 13 |
| 12 | 3 | NSI | 15 |
| 14 | 4 | NSI | 10 |
| 15 | 3 | MATHS | 18 |
| 16 | 4 | MATHS | 12 |

Le raisonnement conserve l'état produit par chaque instruction : l'insertion crée 16, la mise à jour change seulement 14 et la suppression retire seulement 13. Réinitialiser la base entre les étapes ferait perdre cette composition des effets.

## Différenciation

### Aides graduées

- Aide 1 : entourer le verbe de l'intention : afficher, ajouter, corriger ou supprimer.
- Aide 2 : pour `UPDATE` et `DELETE`, écrire d'abord la phrase « je veux toucher la ligne dont ... ».
- Aide 3 : transformer cette phrase en `WHERE`, puis l'essayer dans un `SELECT`.

### Prolongement pour les élèves rapides

Expliquer, sans syntaxe supplémentaire exigible, comment une transaction permettrait d'annuler la campagne de l'exercice 6 si le contrôle final était incorrect. Ce prolongement est explicitement hors exigible syntaxique.

## Erreurs fréquentes à diagnostiquer

- **Erreur fréquente 1 — vérifier après mais pas avant.** Une modification déjà trop large ne peut pas être rendue sûre par un simple constat final. Antidote : exécuter le `SELECT` avec le même `WHERE` avant `UPDATE` ou `DELETE` et annoncer le nombre de lignes visées.
- **Erreur fréquente 2 — confondre identifiant d'élève et identifiant de note.** Un élève peut posséder plusieurs notes, tandis que `id_note` cible une seule ligne. Antidote : choisir la clé qui correspond exactement à l'unicité demandée par l'intention.

## Critères de réussite

- `INSERT` aligne colonnes et valeurs et utilise une clé primaire libre.
- Chaque `UPDATE` et chaque `DELETE` contient un `WHERE` qui cible les lignes annoncées.
- Les contrôles avant et après utilisent la même condition que la modification.
- Le résultat final est calculé à partir de l'état précédent, sans réinitialiser la base dans l'exercice 6.
