---
title: "T10 - Évaluation - INSERT, UPDATE et DELETE"
level: "terminale"
sequence_id: "T10"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Requêtes SQL de modification"
bareme: "T10_bareme_sql_select_where_join.md"
corrige: "T10_corrige_sql_select_where_join.md"
private_data: false
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03F"
    - "T-BDD-03G"
    - "T-BDD-03H"
---

# T10 - Évaluation - INSERT, UPDATE et DELETE

## Cadre

- Durée : 40 minutes.
- Total : 20 points.
- Documents et exécution sur machine : non autorisés.
- Les questions 2 à 5 sont indépendantes : chacune repart de la base initiale.
- Pour `UPDATE` et `DELETE`, le `SELECT` de contrôle fait partie de la réponse attendue.

Capacités évaluées : `T-BDD-03A`, `T-BDD-03F`, `T-BDD-03G`, `T-BDD-03H`.

## Base initiale fournie

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

## Question 1 — Choisir sans confondre (3 points)

Associer chaque intention à `SELECT`, `INSERT`, `UPDATE` ou `DELETE`, puis indiquer si la base est modifiée.

1. Afficher les notes de NSI.
2. Enregistrer une nouvelle note.
3. Corriger une valeur déjà enregistrée.
4. Retirer une ligne d'essai.

## Question 2 — Insérer (4 points)

Alan obtient 12 en mathématiques. Cette note reçoit l'identifiant 16.

1. Écrire l'instruction complète qui ajoute `Note(16, 4, 'MATHS', 12)`.
2. Écrire un `SELECT` ciblé qui vérifie l'insertion.
3. Donner la ligne exacte renvoyée par ce contrôle.

## Question 3 — Mettre à jour sans déborder (5 points)

La note de NSI d'Alan, identifiée par `id_note = 14`, doit passer de 9 à 10.

1. Écrire le `SELECT` de contrôle avant modification et son résultat.
2. Écrire l'`UPDATE` ciblé.
3. Donner le résultat du même contrôle après modification.
4. Expliquer l'effet de la même instruction sans clause `WHERE`.

## Question 4 — Supprimer sans déborder (5 points)

La note de mathématiques d'Ada, identifiée par `id_note = 13`, doit être supprimée.

1. Écrire le `SELECT` de contrôle avant suppression et son résultat.
2. Écrire le `DELETE` ciblé.
3. Donner le résultat du même contrôle après suppression.
4. Indiquer combien de lignes restent dans `Note`.

## Question 5 — Déboguer une opération dangereuse (3 points)

L'intention est de remplacer uniquement la note 11 par 16, mais la requête proposée est :

```sql
UPDATE Note SET note = 16;
```

1. Décrire précisément son effet sur la base initiale.
2. Écrire la requête corrigée.
3. Donner le `SELECT` à exécuter avant la correction pour vérifier la cible.

## Repères enseignant — à masquer dans la projection élève

| Question | Requête ou décision attendue | Résultat exact | Piège principal | Critère de barème décisif |
|---|---|---|---|---|
| 1 | `SELECT` non modifiant ; les trois autres selon leur verbe | quatre associations correctes | employer `UPDATE` pour afficher | opération cohérente avec l'intention |
| 2 | `INSERT INTO Note(id_note, id_eleve, matiere, note) VALUES (16, 4, 'MATHS', 12);` | `(16, 4, MATHS, 12)` | ordre colonnes/valeurs ou clé déjà utilisée | ligne insérée et contrôle ciblé |
| 3 | `UPDATE Note SET note = 10 WHERE id_note = 14;` | avant `(14, 9)`, après `(14, 10)` | omission de `WHERE` | cible unique et états avant/après |
| 4 | `DELETE FROM Note WHERE id_note = 13;` | avant la ligne 13, après aucune ligne ; 5 lignes restantes | supprimer toutes les notes de maths | cible unique et résultat vide après |
| 5 | six notes deviendraient 16 ; ajouter `WHERE id_note = 11` | contrôle avant : `(11, 13)` | dire seulement « c'est dangereux » | effet quantifié et correction complète |

## Cas limites et erreurs fréquentes — repères enseignant

- **Cas limite 1 — identifiant absent.** Un `UPDATE ... WHERE id_note = 99` ne modifie aucune ligne ; une réponse correcte doit distinguer cette absence d'une erreur de syntaxe.
- **Cas limite 2 — suppression déjà effectuée.** Rejouer le contrôle de la note 13 après `DELETE` donne un résultat vide ; exécuter de nouveau la suppression touche zéro ligne.
- **Erreur fréquente 1 — oublier `WHERE`.** La requête reste syntaxiquement valide mais change les six notes. Antidote : imposer le `SELECT` préalable avec la même condition.
- **Erreur fréquente 2 — réutiliser une clé primaire.** Une insertion avec `id_note = 10` doit être refusée. Antidote : contrôler l'absence de l'identifiant avant `INSERT` et interpréter l'exception d'intégrité.

Le résultat attendu pour chaque modification comprend l'état avant, la requête complète et l'état après ; le corrigé ne valide pas une requête isolée sans preuve de portée.

## Aménagement

La version aménagée commune `T10_version_amenagee_sql_select_where_join.md` propose une grille de choix d'opération et des clauses à compléter, sans afficher la requête finale.
