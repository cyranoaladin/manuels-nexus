---
title: "T10 - Fiche cours - SQL : SELECT, WHERE, JOIN"
level: "terminale"
sequence_id: "T10"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "SQL"
notion: "requêtes de lecture"
official_program:
  capacities:
    - "T-BDD-03A"
    - "T-BDD-03B"
    - "T-BDD-03C"
    - "T-BDD-03D"
    - "T-BDD-03E"
readiness: operational
private_data: false
---
# T10 - Fiche cours - SQL : SELECT, WHERE, JOIN

## À savoir
- Schéma minimal utilisé : `Eleve(id_eleve, nom, classe)` et `Note(id_note, id_eleve, matiere, note)`.
- `SELECT` choisit les colonnes affichées ; `WHERE` filtre les lignes.
- `JOIN` relie deux tables avec une condition, ici `Eleve.id_eleve = Note.id_eleve`.
- `ORDER BY` ordonne le résultat sans modifier les tables.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E.
2. T-BDD-03A : écrire `SELECT` et `FROM` pour choisir les colonnes.
3. T-BDD-03B : ajouter `WHERE` pour filtrer avant de lire le résultat.
4. T-BDD-03C et T-BDD-03D : écrire une jointure avec condition explicite.
5. T-BDD-03E : ajouter `ORDER BY note DESC` pour classer les lignes obtenues.

## Exemples corrigés
### Exemple corrigé 1 - SELECT simple
`SELECT nom, classe FROM Eleve;` affiche deux colonnes de la table `Eleve`.
### Exemple corrigé 2 - WHERE
`SELECT nom FROM Eleve WHERE classe = "T1";` ne garde que les élèves de T1.
### Exemple corrigé 3 - JOIN
`SELECT Eleve.nom, Note.note FROM Eleve JOIN Note ON Eleve.id_eleve = Note.id_eleve;` associe chaque note à un nom.
### Exemple corrigé 4 - ORDER BY
`SELECT matiere, note FROM Note WHERE id_eleve = 2 ORDER BY note DESC;` classe les notes de l’élève 2.
### Exemple corrigé 5 - Erreur de jointure
`Eleve JOIN Note` sans `ON` produit des associations non maîtrisées entre toutes les lignes.
### Exemple corrigé 6 - Filtrer avant ou après
Filtrer `classe = "T1"` dans `WHERE` limite les élèves concernés avant la lecture des notes jointes.

## Erreurs fréquentes
- Confondre le vocabulaire de requêtes de lecture avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de requêtes de lecture et modification : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur SQL : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour requêtes de lecture, à traiter selon la convention du chapitre T10.
- Donnée invalide dans requêtes de lecture et modification, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de SQL où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-BDD-03A : écrire la requête qui affiche tous les noms.
### Mini-exercice 2
T-BDD-03B : filtrer les notes de mathématiques.
### Mini-exercice 3
T-BDD-03C : joindre `Eleve` et `Note` par `id_eleve`.
### Mini-exercice 4
T-BDD-03E : trier les notes par ordre décroissant.

## Réponses rapides
1. `SELECT nom FROM Eleve;`.
2. `SELECT note FROM Note WHERE matiere = "maths";`.
3. `... JOIN Note ON Eleve.id_eleve = Note.id_eleve`.
4. `ORDER BY note DESC` place les notes les plus hautes en premier.

## À retenir
- T10 : requêtes de lecture se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de SQL doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T10, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T10 sur requêtes de lecture reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T10-S1 | réelle | séance présente dans la progression |
| TD | T10_TD_sql_select_where_join.md | existant | support TD créé en needs_review |
| Évaluation | T10_evaluation_sql_select_where_join.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer requêtes de lecture avec un exemple différent de ceux de la fiche T10.
- Je peux citer au moins une capacité parmi T-BDD-03A, T-BDD-03B, T-BDD-03C, T-BDD-03D, T-BDD-03E et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T10 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de SQL sans transformer la fiche en corrigé complet.
