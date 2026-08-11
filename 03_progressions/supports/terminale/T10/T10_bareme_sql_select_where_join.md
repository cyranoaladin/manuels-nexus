---
title: "T10 - Barème - Requêtes SQL de lecture et de modification"
level: "terminale"
sequence_id: "T10"
document_type: "bareme"
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

# T10 - Barème - Requêtes SQL de lecture et de modification

## Principes communs

- Les points sont attribués au critère observable, même si un autre critère de la question est faux.
- Une erreur de syntaxe locale (`;` absent, casse des mots-clés) ne retire pas les points de méthode si la requête reste non ambiguë.
- Une requête non exécutable perd les points « requête complète », mais conserve les points de table, projection ou condition correctement identifiables.
- Un résultat exact sans requête ne reçoit que les points de résultat.
- Pour `UPDATE` et `DELETE`, l'absence de `WHERE` est une erreur structurante : la question de modification est plafonnée à la moitié de ses points, car l'effet contredit la cible annoncée.

## Évaluation `SELECT`, `WHERE`, `JOIN`, `ORDER BY` — 20 points

### Barème question 1 — 4 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Identifie le rôle de `SELECT`, `FROM`, `WHERE` et `ORDER BY` | 2 | 0,5 par rôle exact |
| Produit exactement `(Alan, T2)`, puis `(Linus, T2)` | 1 | 0,5 si les deux lignes sont présentes mais mal ordonnées |
| Indique que la base n'est pas modifiée et relie ce fait à `SELECT` | 1 | 0,5 si « non » est donné sans justification |

### Barème question 2 — 4 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Choisit `Note` et projette `id_note, note` | 1 | 0,5 pour la bonne table seule ou la bonne projection seule |
| Écrit les deux conditions `matiere = 'MATHS'` et `note >= 15`, reliées par `AND` | 1,5 | 0,75 par condition correcte ; 0 si elles sont reliées par `OR` |
| Ordonne par `note DESC` | 0,5 | aucun point pour `ASC` |
| Annonce uniquement `(15, 18)` | 1 | 0,5 si la ligne est correcte avec une ligne parasite |

### Barème question 3 — 5 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Projette `Eleve.nom, Note.note` depuis les deux tables | 1 | 0,5 si une seule colonne est projetée correctement |
| Écrit `JOIN Note ON Eleve.id_eleve = Note.id_eleve` | 1,5 | 0,5 pour la présence de `JOIN`, 1 pour l'égalité de clés correcte |
| Filtre simultanément `matiere = 'NSI'` et `note < 14` | 1 | 0,5 par condition correcte |
| Ordonne par note croissante | 0,5 | aucun point pour un ordre décroissant |
| Donne `(Alan, 9)`, puis `(Linus, 13)` | 0,5 | 0,25 par ligne correcte |
| Justifie que la clé étrangère `Note.id_eleve` désigne la clé primaire `Eleve.id_eleve` | 0,5 | aucun point pour « parce que les noms sont identiques » seul |

### Barème question 4 — 3 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Explique que `id_eleve` et `id_note` n'identifient pas le même type d'objet | 1 | 0,5 si le constat « mauvaise clé » n'est pas expliqué |
| S'appuie sur les valeurs 1 à 4 contre 10 à 15 pour expliquer le résultat vide | 0,5 | aucun point pour une affirmation non reliée aux données |
| Corrige en `Eleve.id_eleve = Note.id_eleve` | 1 | 0,5 si les bonnes colonnes sont citées sans égalité complète |
| Annonce six lignes après correction | 0,5 | aucun point pour 4 ou 24 lignes |

### Barème question 5 — 4 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Projette nom, matière et note depuis les tables appropriées | 0,5 | aucun point si une colonne demandée manque |
| Joint sur les deux `id_eleve` | 1 | 0,5 si `JOIN` est présent mais `ON` incomplet |
| Filtre `classe = 'T1'` et `note >= 15` | 1 | 0,5 par condition correcte |
| Écrit le double tri `note DESC, nom ASC` | 0,5 | 0,25 si seul le premier tri est correct |
| Donne exactement les trois lignes dans l'ordre attendu | 1 | 0,25 par ligne correcte, plus 0,25 pour l'ordre complet |

**Total lecture : 4 + 4 + 5 + 3 + 4 = 20 points.**

## Évaluation `INSERT`, `UPDATE`, `DELETE` — 20 points

### Barème question 1 — 3 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Associe afficher, enregistrer, corriger, retirer à `SELECT`, `INSERT`, `UPDATE`, `DELETE` | 2 | 0,5 par association correcte |
| Classe correctement `SELECT` comme non modifiant et les trois autres comme modifiants | 1 | 0,25 par décision correcte |

### Barème question 2 — 4 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Choisit `INSERT INTO Note` et nomme les quatre colonnes | 0,75 | 0,25 pour la table, 0,5 pour les colonnes complètes |
| Aligne exactement les valeurs `(16, 4, 'MATHS', 12)` avec les colonnes | 1,25 | 0,25 par valeur placée correctement, plus 0,25 si l'ordre est cohérent |
| Écrit un `SELECT` avec `WHERE id_note = 16` | 1 | 0,5 si le contrôle affiche toute la table sans cibler la ligne |
| Annonce `(16, 4, 'MATHS', 12)` | 1 | 0,5 si la ligne est reconnaissable mais une valeur est mal placée |

### Barème question 3 — 5 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Contrôle avant avec `WHERE id_note = 14` et annonce `(14, 9)` | 1,25 | 0,75 pour le `SELECT`, 0,5 pour le résultat |
| Écrit `UPDATE Note SET note = 10` | 1 | 0,5 pour la bonne table, 0,5 pour l'affectation |
| Cible `WHERE id_note = 14` | 1 | critère indispensable ; déclenche le plafond si absent |
| Annonce `(14, 10)` après modification | 0,75 | 0,5 si seule la nouvelle valeur est donnée |
| Explique que sans `WHERE` les six notes deviendraient 10 | 1 | 0,5 si « toutes les notes » est dit sans quantification |

### Barème question 4 — 5 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Contrôle avant avec `WHERE id_note = 13` et annonce la ligne complète | 1,25 | 0,75 pour le `SELECT`, 0,5 pour le résultat |
| Écrit `DELETE FROM Note` | 0,75 | aucun point pour `DELETE Note` sans `FROM` |
| Cible `WHERE id_note = 13` | 1 | critère indispensable ; déclenche le plafond si absent |
| Annonce un résultat vide après le même contrôle | 1 | 0,5 si la disparition est dite sans requête de contrôle |
| Indique qu'il reste cinq lignes | 1 | aucun point pour six lignes |

### Barème question 5 — 3 points

| Critère observable | Points | Réponse partielle prévue |
|---|---:|---|
| Explique que les six lignes recevraient la note 16 | 0,75 | 0,5 si « toutes » est dit sans nombre |
| Corrige avec `UPDATE Note SET note = 16 WHERE id_note = 11` | 1,25 | 0,75 si le `WHERE` est correct mais l'affectation incomplète |
| Écrit `SELECT id_note, note FROM Note WHERE id_note = 11` | 1 | 0,5 si le bon `WHERE` est donné sans requête complète |

**Total modification : 3 + 4 + 5 + 5 + 3 = 20 points.**

## Grille formative pour les TD

Pour chaque exercice, l'enseignant peut relever quatre observables sans les convertir automatiquement en note :

1. l'opération choisie correspond au verbe de l'intention ;
2. les tables, colonnes et clés sont identifiées par leur sens ;
3. la requête est complète et sa portée est contrôlée ;
4. le résultat annoncé est obtenu ligne par ligne à partir des données.
