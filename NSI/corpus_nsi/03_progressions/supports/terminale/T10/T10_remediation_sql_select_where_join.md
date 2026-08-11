---
title: "T10 - Remédiation - Choisir, cibler et relier en SQL"
level: "terminale"
sequence_id: "T10"
document_type: "remediation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Diagnostic des erreurs SQL"
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

# T10 - Remédiation - Choisir, cibler et relier en SQL

## Mode d'emploi

Durée : 25 à 35 minutes. Commencer par le diagnostic, suivre seulement le parcours correspondant à l'erreur observée, puis réaliser la tâche de sortie sans aide. Le but n'est pas de recopier le cours mais de reconstruire une autre façon de décider.

## Diagnostic rapide

| Item | Réponse de l'élève | Parcours conseillé si la réponse est fausse |
|---|---|---|
| « Afficher la note 14 » modifie-t-il la base ? | non | A — choisir l'opération |
| `UPDATE Note SET note = 10;` touche-t-il une seule ligne ? | non, toutes les lignes | B — contrôler la portée |
| Une note se relie-t-elle à un élève par `Note.id_eleve` ? | oui | C — construire la jointure |
| `WHERE` classe-t-il les lignes de A à Z ? | non, il les filtre | D — trier le résultat |
| `ORDER BY nom ASC` modifie-t-il `Eleve` ? | non, il ordonne seulement le résultat | D — trier le résultat |

## Parcours A — Confusion `SELECT` / `UPDATE`

### Autre représentation : l'état avant/après

Compléter ce tableau avant d'écrire du SQL.

| Intention | Faut-il un résultat affiché ? | L'état après doit-il différer ? | Famille d'opération |
|---|---|---|---|
| connaître la note 14 | oui | non |  |
| corriger la note 14 de 9 à 10 | oui, pour vérifier | oui |  |

**Règle reconstruite.** Si l'état doit rester identique, commencer par `SELECT`. Si une valeur existante doit changer, utiliser `UPDATE`, mais seulement après un `SELECT` de contrôle.

### Tâche de réparation

Parmi les deux débuts `SELECT id_note, note FROM Note` et `UPDATE Note SET note = 10`, choisir celui qui répond à « afficher la note 14 », puis ajouter la condition qui cible cette ligne. Expliquer pourquoi l'autre début modifierait la base.

### Vérification différée

Une réponse correcte contient un `SELECT` et un filtre sur `id_note = 14`. Elle ne contient pas `UPDATE`.

## Parcours B — Oubli de `WHERE`

### Autre représentation : la carte d'impact

Pour chaque ligne de `Note`, cocher si elle serait modifiée par `UPDATE Note SET note = 10;`. Que constate-t-on ? Ajouter ensuite la condition `id_note = 14` et refaire les coches.

| id_note | 10 | 11 | 12 | 13 | 14 | 15 |
|---:|---|---|---|---|---|---|
| sans `WHERE` |  |  |  |  |  |  |
| avec `WHERE id_note = 14` |  |  |  |  |  |  |

### Tâche de réparation

1. Écrire le `SELECT` qui ne renvoie que la ligne 14.
2. Conserver exactement sa condition pour écrire l'`UPDATE` ciblé.
3. Annoncer l'état de la ligne 14 avant et après.

### Vérification différée

Sans `WHERE`, les six cases sont cochées. Avec le filtre, seule la colonne 14 l'est. Avant : note 9 ; après : note 10.

## Parcours C — `JOIN` sans `ON` ou mauvaise clé

### Autre représentation : relier les identifiants

Tracer une flèche depuis chaque valeur `Note.id_eleve` vers la même valeur dans `Eleve.id_eleve`. Par exemple, la ligne `Note(10, 1, 'NSI', 17)` pointe vers `Eleve(1, 'Ada', 'T1')`.

1. Vers quel élève pointe la note 12 ?
2. Pourquoi aucune flèche ne part de `Note.id_note = 12` vers `Eleve.id_eleve` ?
3. Compléter en français : « une note appartient à l'élève lorsque ... ».

### Tâche de réparation

Corriger la seule ligne fautive :

```sql
SELECT Eleve.nom, Note.note
FROM Eleve
JOIN Note ON Eleve.id_eleve = Note.id_note
WHERE Note.id_note = 12;
```

Puis annoncer le nom et la note obtenus.

### Vérification différée

La note 12 pointe vers Grace par la valeur commune `id_eleve = 3`; le résultat corrigé est Grace 15. `id_note` identifie une note, pas un élève.

## Parcours D — Confusion `WHERE` / `ORDER BY` (`T-BDD-03E`)

### Autre représentation : filtrer, puis trier le résultat

Comparer les deux requêtes suivantes :

```sql
SELECT nom
FROM Eleve
WHERE classe = 'T2';
```

```sql
SELECT nom
FROM Eleve
WHERE classe = 'T2'
ORDER BY nom ASC;
```

Dans les deux cas, `WHERE` conserve les deux élèves de T2 : Alan et Linus. Seule la seconde requête impose l'ordre alphabétique `Alan`, puis `Linus`. `ORDER BY` ne retire aucune ligne et ne modifie pas la table `Eleve` : il ordonne uniquement le résultat affiché.

### Tâche de réparation

On veut afficher les notes de NSI de la plus grande à la plus petite. Écrire la requête complète qui affiche `id_note` et `note`, puis :

1. choisir la colonne de tri ;
2. choisir entre `ASC` et `DESC` ;
3. prévoir le premier et le dernier tuple du résultat ;
4. expliquer pourquoi remplacer `ORDER BY` par `WHERE` ne répondrait pas à la consigne.

### Vérification différée

La requête attendue se termine par `ORDER BY note DESC`. Le premier tuple est `(10, 17)` et le dernier `(14, 9)`. `ASC` produirait l'ordre inverse ; ni `ASC` ni `DESC` ne changent les valeurs stockées dans `Note`.

## Tâche de sortie isomorphe — sans aide

Sur la base de référence, répondre aux trois demandes suivantes sans consulter les parcours :

1. Afficher le nom et la note correspondant à `id_note = 11` en reliant les deux tables.
2. Corriger cette note à 16 avec un contrôle avant et après.
3. Écrire la requête qui supprimerait uniquement la note 15, puis expliquer l'effet de la même requête sans `WHERE`.
4. Afficher les noms des élèves de T2 dans l'ordre alphabétique, annoncer le premier et le dernier nom, puis expliquer pourquoi ce tri ne modifie pas `Eleve`.

## Critères de sortie de remédiation

- L'opération correspond au verbe de l'intention.
- La jointure est justifiée par le sens des deux colonnes `id_eleve`.
- Tout `UPDATE` ou `DELETE` est précédé d'un `SELECT` portant le même filtre.
- `WHERE` filtre les lignes et `ORDER BY` les trie avec une colonne et un sens (`ASC` ou `DESC`) justifiés.
- Le résultat trié est distingué de l'ordre et des valeurs stockés dans les tables.
- L'élève prévoit l'état avant et l'état après sans réponse fournie.
