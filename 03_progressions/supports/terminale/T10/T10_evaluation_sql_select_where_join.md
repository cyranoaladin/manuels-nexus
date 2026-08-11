---
title: "T10 - Évaluation - SELECT, WHERE, JOIN et ORDER BY"
level: "terminale"
sequence_id: "T10"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Requêtes SQL de lecture"
bareme: "T10_bareme_sql_select_where_join.md"
corrige: "T10_corrige_sql_select_where_join.md"
private_data: false
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03B"
    - "T-BDD-03C"
    - "T-BDD-03D"
    - "T-BDD-03E"
---

# T10 - Évaluation - SELECT, WHERE, JOIN et ORDER BY

## Cadre

- Durée : 40 minutes.
- Total : 20 points.
- Documents et exécution sur machine : non autorisés.
- Toute requête doit être écrite intégralement. Une réponse sans résultat exact lorsqu'il est demandé est incomplète.

Capacités évaluées : `T-BDD-03A`, `T-BDD-03B`, `T-BDD-03C`, `T-BDD-03D`, `T-BDD-03E`.

## Base fournie

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

## Question 1 — Lire une requête (4 points)

```sql
SELECT nom, classe
FROM Eleve
WHERE classe = 'T2'
ORDER BY nom ASC;
```

1. Associer à chaque clause son rôle : colonnes affichées, table lue, lignes conservées, ordre du résultat.
2. Donner le résultat exact sous forme de tableau.
3. Dire si la requête modifie la base et justifier.

**Production attendue.** Quatre annotations, un tableau de deux lignes et une justification.

## Question 2 — Écrire un filtre (4 points)

Écrire une requête qui affiche `id_note` et `note` pour les notes de mathématiques supérieures ou égales à 15, par note décroissante. Donner le résultat exact.

**Production attendue.** Une requête complète utilisant une seule table et un tableau résultat.

## Question 3 — Construire une jointure (5 points)

Écrire une requête qui affiche le nom et la note des élèves ayant une note de NSI strictement inférieure à 14. Trier le résultat par note croissante. Donner le résultat exact et justifier la clé utilisée après `ON`.

**Production attendue.** Requête complète, tableau de deux lignes et phrase justifiant la clé de jointure.

## Question 4 — Déboguer une mauvaise clé (3 points)

Un élève écrit :

```sql
SELECT Eleve.nom, Note.matiere
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_note;
```

1. Expliquer pourquoi le résultat est vide sur la base fournie, même si la requête est syntaxiquement plausible.
2. Corriger seulement la condition de jointure.
3. Indiquer le nombre de lignes produit par la requête corrigée.

## Question 5 — Transférer (4 points)

Afficher le nom, la matière et la note des élèves de T1 ayant une note supérieure ou égale à 15. Trier par note décroissante, puis par nom alphabétique. Donner les trois lignes dans l'ordre exact.

## Repères enseignant — à masquer dans la projection élève

| Question | Requête ou décision attendue | Résultat exact | Piège principal | Critère de barème décisif |
|---|---|---|---|---|
| 1 | lecture des quatre clauses | `(Alan, T2)`, `(Linus, T2)` | croire que `ORDER BY` modifie la table | rôles et ordre exact |
| 2 | `SELECT id_note, note FROM Note WHERE matiere = 'MATHS' AND note >= 15 ORDER BY note DESC;` | `(15, 18)` | garder Ada 14 ou oublier la matière | deux conditions dans `WHERE` |
| 3 | `SELECT Eleve.nom, Note.note FROM Eleve JOIN Note ON Eleve.id_eleve = Note.id_eleve WHERE Note.matiere = 'NSI' AND Note.note < 14 ORDER BY Note.note ASC;` | `(Alan, 9)`, `(Linus, 13)` | joindre sur `id_note` | clé de jointure correcte et justifiée |
| 4 | remplacer par `Eleve.id_eleve = Note.id_eleve` | 6 lignes | corriger une autre clause | expliquer le sens différent des deux identifiants |
| 5 | jointure, filtre sur T1 et note, double tri | `(Grace, MATHS, 18)`, `(Ada, NSI, 17)`, `(Grace, NSI, 15)` | filtrer seulement la NSI | résultat inédit et tri exact |

## Critères, cas limites et erreurs fréquentes — repères enseignant

- **Critère de réussite observable 1.** Chaque colonne demandée apparaît dans `SELECT`, chaque table nécessaire dans `FROM` ou `JOIN`, sans colonne supplémentaire.
- **Critère de réussite observable 2.** Le tableau de résultat contient le bon nombre de lignes et respecte chaque critère de tri, y compris en cas d'égalité.
- **Cas limite 1 — valeur frontière.** Une note égale à 15 est conservée par `>= 15` ; l'exclure révèle une confusion entre `>` et `>=`.
- **Cas limite 2 — jointure sans correspondance.** Avec la mauvaise clé de la question 4, aucun identifiant 1 à 4 n'égale un identifiant 10 à 15 : le résultat est vide, ce qui doit être expliqué à partir des données.
- **Erreur fréquente 1 — corriger la syntaxe sans le sens.** Remplacer une colonne au hasard peut produire une requête exécutable mais fausse. Antidote : formuler « une note appartient à un élève lorsque... ».
- **Erreur fréquente 2 — appliquer le tri avant le filtre dans le raisonnement.** Antidote : déterminer d'abord l'ensemble des lignes conservées, puis ordonner seulement cet ensemble.

Le résultat attendu de la question 5 est la suite exacte des trois tuples du tableau ci-dessus ; le corrigé doit vérifier séparément jointure, filtre et double tri.

## Aménagement

La version aménagée commune `T10_version_amenagee_sql_select_where_join.md` conserve les mêmes objectifs et propose des aides graduées sans fournir les requêtes complètes.
