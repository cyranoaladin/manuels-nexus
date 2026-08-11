---
title: "T10 - Version aménagée - Requêtes SQL"
level: "terminale"
sequence_id: "T10"
document_type: "version_amenagee"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Aides graduées pour SELECT, JOIN, ORDER BY, UPDATE et DELETE"
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

# T10 - Version aménagée - Requêtes SQL

## Objectif conservé

Écrire et contrôler une requête SQL complète. Les étapes sont découpées et les mots-clés sont fournis, mais ni la requête finale ni son résultat ne sont donnés.

## Base de travail

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

## Fiche outil — choisir avant d'écrire

| Intention | Mot-clé à choisir |
|---|---|
| afficher | `SELECT` |
| ajouter une ligne | `INSERT` |
| corriger une valeur | `UPDATE` |
| retirer une ligne | `DELETE` |

Pour filtrer une lecture, ajouter `WHERE`. Pour utiliser deux tables, ajouter `JOIN ... ON`. Pour trier le résultat, ajouter `ORDER BY` suivi d'une colonne et de `ASC` (croissant) ou `DESC` (décroissant) : ce tri ne modifie pas les tables.

## Tâche 1 — Lecture avec jointure et tri (`T-BDD-03E`)

**Consigne.** Afficher le nom et la note des élèves ayant au moins 15 en NSI, triées par note décroissante.

### Étape A — choisir les éléments

1. Colonnes à afficher : `________________` et `________________`.
2. Table qui contient le nom : `________________`.
3. Table qui contient la note : `________________`.
4. Colonnes de même sens à relier : `________________ = ________________`.
5. Deux conditions du filtre : `________________` et `________________`.

### Étape B — choisir le tri avant d'assembler

1. Colonne qui doit déterminer l'ordre : `________________`.
2. Cocher le sens demandé : [ ] `ASC` (du plus petit au plus grand / A à Z) ; [ ] `DESC` (du plus grand au plus petit / Z à A).
3. Prévoir la première ligne du résultat : `________________`.
4. Prévoir la dernière ligne du résultat : `________________`.
5. Cocher la phrase correcte : [ ] « le tri modifie les notes stockées » ; [ ] « le tri organise seulement les lignes affichées ».

### Étape C — assembler

Compléter sans changer l'ordre des clauses :

```text
SELECT ________________________________
FROM __________________
JOIN __________________ ON ________________________________
WHERE ________________________________ AND ________________________________
ORDER BY __________________ __________________;
```

### Étape D — vérifier le résultat

Passer chaque ligne de `Note` dans le filtre, puis compléter sans ajouter de ligne :

| nom | note |
|---|---:|
|  |  |
|  |  |

Cocher :

- [ ] toutes les lignes affichées sont en NSI ;
- [ ] toutes les notes affichées valent au moins 15 ;
- [ ] la note 15 a été conservée ;
- [ ] les notes sont décroissantes.
- [ ] la première et la dernière ligne prévues correspondent au tri choisi ;
- [ ] le tri ne modifie ni `Eleve` ni `Note`.

### Espace de réponse guidé — tri du résultat (`T-BDD-03E`)

Avant de rédiger la requête finale, utiliser cet espace pour préparer seulement les choix liés au tri.

- Requête à écrire : `SELECT ________________________________________________________________`
- Entourer la clause qui trie : `WHERE` / `ORDER BY`.
- Colonne de tri : `________________`.
- Sens choisi : [ ] `ASC`  [ ] `DESC`.
- Premier résultat prévu : `________________` ; dernier résultat prévu : `________________`.
- Compléter : « `ORDER BY` trie le résultat mais ne modifie pas `________________`. »

## Tâche 2 — Choisir entre lecture et modification

Pour chaque demande, cocher une seule opération.

| Demande | `SELECT` | `INSERT` | `UPDATE` | `DELETE` |
|---|:---:|:---:|:---:|:---:|
| afficher la note 14 | [ ] | [ ] | [ ] | [ ] |
| corriger la note 14 à 10 | [ ] | [ ] | [ ] | [ ] |
| ajouter la note 16 | [ ] | [ ] | [ ] | [ ] |
| retirer la note 13 | [ ] | [ ] | [ ] | [ ] |

## Tâche 3 — Modification ciblée

**Consigne.** Corriger uniquement la note 14 pour qu'elle vaille 10.

1. Compléter le contrôle avant :

```text
SELECT id_note, note
FROM Note
WHERE ________________________________;
```

2. Écrire la ligne obtenue avant : `________________`.
3. Compléter la modification en réutilisant exactement le même filtre :

```text
UPDATE Note
SET ________________________________
WHERE ________________________________;
```

4. Refaire le contrôle et écrire la ligne après : `________________`.
5. Expliquer en une phrase ce qui arriverait si la dernière clause était supprimée : `____________________________________________________________`.

## Aides à dévoilement progressif

N'utiliser l'aide suivante que si la précédente ne suffit pas.

1. **Aide légère** : entourer le verbe de la consigne et les valeurs numériques importantes.
2. **Aide intermédiaire** : dire à voix basse « colonne affichée, table, lien, filtre, ordre ».
3. **Aide forte** : pour la jointure, compléter la phrase « une note appartient à l'élève lorsque les deux colonnes nommées ... ont la même valeur ».
4. **Aide pour le tri** : dire « `WHERE` choisit les lignes ; `ORDER BY` les range ». Pour une meilleure note en premier, choisir `DESC` ; pour A à Z, choisir `ASC`.

## Validation personnelle

- [ ] Je sais dire si ma requête modifie la base.
- [ ] Mon `JOIN` relie deux colonnes qui ont le même sens.
- [ ] Mon `WHERE` cible exactement les lignes demandées.
- [ ] J'ai choisi une colonne et un sens de tri cohérents avec la consigne.
- [ ] Je sais que `ORDER BY` modifie le résultat, pas les tables.
- [ ] J'ai prévu le résultat à partir des tables, sans le recopier d'une réponse fournie.
