---
title: "T10 - TP - Exécuter et tester des requêtes SQL avec SQLite"
level: "terminale"
sequence_id: "T10"
document_type: "tp"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Bases de données"
notion: "Requêtes SQL paramétrées et contrôles avant/après"
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

# T10 - TP - Exécuter et tester des requêtes SQL avec SQLite

## Cadre de séance

- Durée : 75 minutes.
- Travail : binôme, un poste par binôme.
- Objectif : compléter quatre fonctions qui exécutent des requêtes paramétrées, puis prouver leur portée par des tests.
- Fichiers fournis : `code/T10_starter_sql_select_where_join.py` et `code/T10_tests_attendus_sql_select_where_join.py`.
- Fichiers à rendre : le starter complété, renommé `T10_nom1_nom2.py`, et un compte rendu `T10_nom1_nom2.md` contenant les requêtes, trois résultats de tests et l'analyse d'un cas dangereux.

## Base fournie

La fonction `creer_base()` construit le schéma `Eleve(id_eleve, nom, classe)` et `Note(id_note, id_eleve, matiere, note)` avec les quatre élèves et les six notes du cours. Elle n'est pas à modifier.

## Signatures à respecter

```python
def notes_minimum(conn, seuil) -> list[tuple[str, str, int]]:
    ...

def ajouter_note(conn, id_note, id_eleve, matiere, valeur) -> tuple[int, int, str, int]:
    ...

def modifier_note(conn, id_note, valeur) -> tuple[int, int] | None:
    ...

def supprimer_note(conn, id_note) -> bool:
    ...
```

Les valeurs fournies par l'utilisateur doivent être passées à SQLite avec des paramètres `?`, et non assemblées par concaténation dans la chaîne SQL.

## Mise en route — 10 minutes

Depuis le dossier `code/`, exécuter :

```bash
python T10_tests_attendus_sql_select_where_join.py
```

Le starter doit échouer sur une fonction non complétée. Lire le premier échec et noter : nom de la fonction, entrée du test, sortie attendue.

## Étape 1 — Lecture, jointure, filtre et tri — 20 minutes

Compléter `notes_minimum` pour renvoyer `(nom, matiere, note)` pour toutes les notes supérieures ou égales au seuil. L'ordre attendu est : note décroissante, puis nom alphabétique en cas d'égalité.

Avant d'exécuter, prévoir sur papier :

- le résultat pour `seuil = 15` ;
- le résultat frontière pour `seuil = 18` ;
- le résultat vide pour `seuil = 20`.

**Point de contrôle.** La requête doit contenir une projection de trois colonnes, une jointure avec `ON`, un `WHERE` paramétré et un double `ORDER BY`.

## Étape 2 — Insertion contrôlée — 15 minutes

Compléter `ajouter_note` :

1. insérer la ligne reçue en paramètres ;
2. relire uniquement cette ligne ;
3. renvoyer le tuple exact.

Tester le cas nominal `(16, 4, 'MATHS', 12)`. Tester ensuite le cas invalide d'une seconde insertion avec `id_note = 16` : SQLite doit refuser la clé primaire dupliquée.

## Étape 3 — Mise à jour ciblée — 15 minutes

Compléter `modifier_note` avec `WHERE id_note = ?`, puis relire l'identifiant et la valeur. La fonction renvoie `None` si l'identifiant n'existe pas.

Cas nominal : modifier la note 14 à 10. Cas limite : tenter de modifier la note 99. Dans le compte rendu, expliquer pourquoi l'absence de `WHERE` ferait réussir une requête syntaxtiquement correcte mais pédagogiquement fausse.

## Étape 4 — Suppression ciblée — 10 minutes

Compléter `supprimer_note`. La fonction renvoie `True` si une ligne a été supprimée et `False` sinon.

Cas nominal : supprimer la note 13. Cas limite : demander une seconde fois sa suppression. Vérifier aussi par `SELECT` que la ligne 13 est absente.

## Validation finale — 5 minutes

Exécuter les tests sur le fichier complété en remplaçant le nom de module :

```bash
TP_MODULE=T10_nom1_nom2 python T10_tests_attendus_sql_select_where_join.py
```

Le livrable est recevable si :

- tous les tests passent ;
- les quatre signatures sont conservées ;
- les requêtes utilisent des paramètres ;
- le compte rendu distingue résultat nominal, cas limite et cas invalide ;
- l'analyse du `WHERE` manquant décrit le nombre de lignes touchées.

## Exemples corrigés de contrôle — repères enseignant

### Exemple corrigé 1 — seuil frontière

Pour `notes_minimum(conn, 18)`, la requête doit renvoyer uniquement `[('Grace', 'MATHS', 18)]`. La note 18 est incluse par `>=`, puis le double tri est sans effet sur cette liste d'une ligne. Un résultat vide signale l'emploi fautif de `>`.

### Exemple corrigé 2 — identifiant absent

Pour `modifier_note(conn, 99, 12)`, le `UPDATE ... WHERE id_note = ?` touche zéro ligne et la relecture `SELECT id_note, note ...` ne renvoie rien : la fonction retourne `None`. Aucune des six notes existantes ne doit changer.

## Erreurs fréquentes et critères de réussite

- **Erreur fréquente 1 — concaténer le seuil dans la requête.** Antidote : laisser `?` dans le SQL et fournir `(seuil,)` comme paramètres à `execute`.
- **Erreur fréquente 2 — utiliser `fetchone()` pour la liste des notes.** Une seule ligne serait renvoyée. Antidote : choisir `fetchall()` lorsque le contrat annonce une liste de tuples.
- **Critère de réussite observable 1.** Les tests nominaux, frontière, vide et invalide passent sans changer les signatures imposées.
- **Critère de réussite observable 2.** Le compte rendu associe à chaque appel son entrée, sa valeur renvoyée et l'état de la table après l'opération.

## Prolongement pour les élèves rapides

Ajouter une fonction qui renvoie les notes d'une matière donnée au-dessus d'un seuil donné. Les deux valeurs doivent être paramétrées. Écrire trois tests, dont un résultat vide et une matière absente.

## Repères enseignant

- Le corrigé exécutable est `code/T10_corrige_professeur_sql_select_where_join.py`.
- Commande de validation du corrigé : `TP_MODULE=T10_corrige_professeur_sql_select_where_join python T10_tests_attendus_sql_select_where_join.py`.
- Le starter non complété doit échouer ; ce comportement prouve que les tests ne valident pas une coquille vide.
- Ne pas valider une fonction qui imprime le résultat au lieu de le renvoyer : les tests doivent pouvoir comparer la valeur.
