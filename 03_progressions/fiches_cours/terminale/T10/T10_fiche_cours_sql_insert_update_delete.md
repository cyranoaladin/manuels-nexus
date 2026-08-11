---
title: "T10 - Fiche cours - SQL : INSERT, UPDATE, DELETE"
level: "terminale"
sequence_id: "T10"
document_type: "fiche_cours"
status: "needs_review"
version: "0.1.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "SQL"
notion: "requêtes de modification"
official_program:
  capacities:
    - "T-BDD-03F"
    - "T-BDD-03G"
    - "T-BDD-03H"
readiness: operational
private_data: false
---
# T10 - Fiche cours - SQL : INSERT, UPDATE, DELETE

## À savoir
- Schéma minimal utilisé : `Eleve(id_eleve, nom, classe)` et `Note(id_note, id_eleve, matiere, note)`.
- `INSERT` ajoute une ligne complète ou partielle selon les colonnes indiquées.
- `UPDATE` modifie les lignes ciblées par `WHERE`.
- `DELETE` supprime les lignes ciblées ; une vérification par `SELECT` précède la modification.

## Méthodes
1. Capacités explicitement travaillées dans les méthodes et exercices : T-BDD-03F, T-BDD-03G, T-BDD-03H.
2. T-BDD-03F : écrire les colonnes puis les valeurs d’un `INSERT`.
3. T-BDD-03G : vérifier par `SELECT` les lignes que `UPDATE` va modifier.
4. T-BDD-03H : vérifier par `SELECT` les lignes que `DELETE` va supprimer.
5. Après modification, refaire un `SELECT` ciblé pour contrôler la table après.

## Exemples corrigés
### Exemple corrigé 1 - INSERT avec table avant/après
Avant : `Eleve` contient les identifiants 1 à 4. Requête : `INSERT INTO Eleve(id_eleve, nom, classe) VALUES (5, "Nadia", "T1");`. Après : une ligne id 5 existe.
### Exemple corrigé 2 - UPDATE ciblé
Avant : `Note(14, 4, "NSI", 9)`. Requête : `UPDATE Note SET note = 10 WHERE id_note = 14;`. Après : la note 14 vaut 10.
### Exemple corrigé 3 - DELETE ciblé
Vérification : `SELECT * FROM Note WHERE id_note = 13;`. Suppression : `DELETE FROM Note WHERE id_note = 13;`. Après : la requête de vérification ne renvoie plus de ligne.
### Exemple corrigé 4 - Risque UPDATE sans WHERE
`UPDATE Note SET note = 20;` modifie toutes les notes : c’est une erreur de portée.
### Exemple corrigé 5 - Risque DELETE trop large
`DELETE FROM Note WHERE matiere = "maths";` supprime toutes les notes de mathématiques, pas une seule copie.

## Erreurs fréquentes
- Confondre le vocabulaire de requêtes de modification avec une simple récitation : corriger par un exemple calculé ou exécuté.
- Oublier une hypothèse de requêtes de lecture et modification : corriger en l’écrivant avant la méthode.
- Conclure sans contrôle sur SQL : corriger par un cas limite ou une vérification inverse.

## Cas limites
- Cas de départ vide ou nul pour requêtes de modification, à traiter selon la convention du chapitre T10.
- Donnée invalide dans requêtes de lecture et modification, par exemple symbole interdit, clé absente ou requête trop large selon la fiche.
- Cas frontière de SQL où une seule valeur change la méthode ou le résultat attendu.

## Mini-exercices
### Mini-exercice 1
T-BDD-03F : ajouter l’élève id 5 nommé Sami en T2.
### Mini-exercice 2
T-BDD-03G : modifier seulement la note id 14 à 10.
### Mini-exercice 3
T-BDD-03H : supprimer seulement la note id 13.
### Mini-exercice 4
Écrire le `SELECT` de contrôle avant un `UPDATE` sur id_note 14.

## Réponses rapides
1. `INSERT INTO Eleve(id_eleve, nom, classe) VALUES (5, "Sami", "T2");`.
2. `UPDATE Note SET note = 10 WHERE id_note = 14;`.
3. `DELETE FROM Note WHERE id_note = 13;`.
4. `SELECT * FROM Note WHERE id_note = 14;` vérifie la cible avant modification.

## À retenir
- T10 : requêtes de modification se révise avec une définition, une méthode et un exemple corrigé.
- Les capacités T-BDD-03F, T-BDD-03G, T-BDD-03H restent en travail tant que TD, TP, évaluation, barème et revues humaines manquent.
- Un exemple de SQL doit changer autre chose qu’une simple valeur pour tester la compréhension.
- Pour T10, le tableau de liens distingue les supports existants et les supports inscrits au registre.
- La fiche T10 sur requêtes de modification reste needs_review et ne déclenche ni publication ni couverture.

## Lien avec la progression

| Élément | Fichier | Statut | Remarque |
|---|---|---|---|
| Séance | T10-S1 | réelle | séance présente dans la progression |
| TD | T10_TD_sql_insert_update_delete.md | existant | support TD créé en needs_review |
| Évaluation | T10_evaluation_sql_insert_update_delete.md | existant | support d’évaluation créé en needs_review |

## Auto-évaluation
- Je peux expliquer requêtes de modification avec un exemple différent de ceux de la fiche T10.
- Je peux citer au moins une capacité parmi T-BDD-03F, T-BDD-03G, T-BDD-03H et dire où elle est travaillée dans la fiche.
- Je peux dire quel support lié à T10 existe déjà ou reste inscrit au registre.
- Je peux identifier un cas limite de SQL sans transformer la fiche en corrigé complet.
