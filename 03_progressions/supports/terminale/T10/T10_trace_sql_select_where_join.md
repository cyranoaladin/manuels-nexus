---
title: "T10 - Trace écrite - Lire et modifier avec SQL"
level: "terminale"
sequence_id: "T10"
document_type: "trace"
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

# T10 - Trace écrite - Lire et modifier avec SQL

## 1. Définitions minimales

- `SELECT` choisit les colonnes affichées ; `FROM` indique les tables lues.
- `WHERE` conserve les lignes qui vérifient une condition.
- `JOIN ... ON` associe des lignes de deux tables lorsque la condition de jointure est vraie.
- `ORDER BY` ordonne le résultat sans modifier les tables.
- `INSERT` ajoute une ligne ; `UPDATE ... WHERE` modifie les lignes ciblées ; `DELETE ... WHERE` supprime les lignes ciblées.

## 2. Quand utiliser quelle opération ?

| Verbe de l'intention | Forme SQL | Effet sur la base |
|---|---|---|
| afficher, chercher, compter | `SELECT` | aucun |
| ne garder que certaines lignes affichées | `WHERE` dans le `SELECT` | aucun |
| relier des données de deux tables | `JOIN ... ON` | aucun |
| ajouter une ligne | `INSERT` | modification |
| corriger une valeur | `UPDATE ... WHERE` | modification |
| retirer une ligne | `DELETE ... WHERE` | modification |

## 3. Méthode numérotée pour une requête de lecture

1. **Projection** : écrire dans `SELECT` les colonnes demandées.
2. **Source** : écrire dans `FROM` les tables qui possèdent ces colonnes.
3. **Jointure** : si deux tables sont nécessaires, relier une clé étrangère à la clé primaire de même sens.
4. **Filtre** : traduire chaque contrainte en condition dans `WHERE`.
5. **Tri** : ajouter `ORDER BY` uniquement si l'ordre est demandé.
6. **Contrôle** : exécuter mentalement la requête ligne par ligne et tester la valeur frontière.

## 4. Exemple complet

Schéma : `Eleve(id_eleve, nom, classe)` et `Note(id_note, id_eleve, matiere, note)`.

**But.** Afficher le nom et la note des élèves ayant au moins 15 en NSI.

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_eleve
WHERE Note.matiere = 'NSI' AND Note.note >= 15
ORDER BY Note.note DESC;
```

### Trace des états importants

| id_note | élève joint | matière | note | condition vraie ? | sortie |
|---:|---|---|---:|---|---|
| 10 | Ada | NSI | 17 | oui | `(Ada, 17)` |
| 11 | Linus | NSI | 13 | non | aucune |
| 12 | Grace | NSI | 15 | oui | `(Grace, 15)` |
| 13 | Ada | MATHS | 14 | non | aucune |
| 14 | Alan | NSI | 9 | non | aucune |
| 15 | Grace | MATHS | 18 | non | aucune |

Résultat : Ada 17, puis Grace 15.

## 5. Méthode sûre pour modifier

1. Écrire un `SELECT` dont le `WHERE` désigne exactement les lignes visées.
2. Vérifier le résultat et le nombre de lignes.
3. Exécuter `UPDATE ... SET ... WHERE ...` ou `DELETE FROM ... WHERE ...` avec le même filtre.
4. Refaire le `SELECT` pour contrôler l'état après.

Exemple :

```sql
SELECT id_note, note FROM Note WHERE id_note = 14;
UPDATE Note SET note = 10 WHERE id_note = 14;
SELECT id_note, note FROM Note WHERE id_note = 14;
```

État avant : `(14, 9)`. État après : `(14, 10)`.

## 6. Pièges et antidotes

| Piège | Conséquence | Antidote |
|---|---|---|
| `JOIN` sur `Eleve.id_eleve = Note.id_note` | clés de sens différent, résultat faux ou vide | dire en français ce que relie la clé avant d'écrire `ON` |
| `WHERE note > 15` au lieu de `>= 15` | la valeur frontière 15 disparaît | tester explicitement 15 |
| `UPDATE Note SET note = 10;` | toutes les notes deviennent 10 | exécuter d'abord le `SELECT` de contrôle |
| `DELETE FROM Note;` | toutes les notes disparaissent | annoncer la clé de la ligne à retirer |

## 7. Cas limites à connaître

- Un filtre peut produire un résultat vide : ce n'est pas nécessairement une erreur.
- Une jointure interne ne montre pas un élève qui n'a aucune note.
- `UPDATE` ou `DELETE` avec un `WHERE` qui ne correspond à aucune ligne ne change rien.
- Une clé primaire déjà utilisée rend un `INSERT` invalide.

## 8. Auto-vérification

Sans regarder le cours, répondre :

1. Quelle clause choisit les colonnes affichées ?
2. Quelle égalité relie ici `Eleve` et `Note` ?
3. Pourquoi `ORDER BY` ne remplace-t-il pas `WHERE` ?
4. Quel contrôle doit précéder un `DELETE` ?
5. Quel est l'effet d'un `UPDATE` sans `WHERE` ?

Réponses de contrôle : `SELECT` ; `Eleve.id_eleve = Note.id_eleve` ; trier n'élimine aucune ligne ; un `SELECT` avec le même filtre ; toutes les lignes de la table sont modifiées.
