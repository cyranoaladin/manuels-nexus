---
title: "T09 - cours - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "bases relationnelles, clés et contraintes"
notion: "bases relationnelles, clés et contraintes"
private_data: false
official_program:
  capacities:
    - "T-BDD-01A"
    - "T-BDD-01B"
    - "T-BDD-01C"
    - "T-BDD-02"
---

# T09 - Cours - bases relationnelles, clés et contraintes

## Objectifs spécifiques
- Identifier les données utiles de la situation : Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide.
- Employer le vocabulaire : relation, attribut, tuple, clé primaire, clé étrangère, contrainte de domaine.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-BDD-01A.
- T-BDD-01B.
- T-BDD-01C.
- T-BDD-02.

## Situation-problème
Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide

## À savoir
- relation.
- attribut.
- tuple.
- clé primaire.
- clé étrangère.
- contrainte de domaine.
- contrainte de référence.
- schéma.
- instance.
- anomalie.

## Méthodes
- identifier schéma et instance.
- vérifier unicité id_livre.
- contrôler Emprunt.id_livre.
- repérer id_livre=9 absent.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : identifier schéma et instance.
- Résultat attendu : Livre.id_livre identifie chaque livre.
- Contrôle : capacité T-BDD-01A et cas limite `clé primaire nulle`.
### Exemple corrigé 2
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : vérifier unicité id_livre.
- Résultat attendu : Emprunt.id_livre référence Livre.id_livre.
- Contrôle : capacité T-BDD-01B et cas limite `doublon id_livre=1`.
### Exemple corrigé 3
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : contrôler Emprunt.id_livre.
- Résultat attendu : Emprunt(11,9,Sam) viole la référence.
- Contrôle : capacité T-BDD-01C et cas limite `suppression référencée`.
### Exemple corrigé 4
- Donnée : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
- Méthode : repérer id_livre=9 absent.
- Résultat attendu : suppression d un livre emprunté refusée.
- Contrôle : capacité T-BDD-02 et cas limite `clé primaire nulle`.

## Cas limites
- clé primaire nulle.
- doublon id_livre=1.
- suppression référencée.

## Erreurs fréquentes
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Exercices intégrés
1. Identifier les données utiles dans `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
2. Appliquer : identifier schéma et instance.
3. Appliquer : vérifier unicité id_livre.
4. Décider le cas limite `clé primaire nulle`.

## Critères de réussite observables
- Une capacité parmi T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02 est citée et utilisée.
- Le résultat attendu est explicite : Livre.id_livre identifie chaque livre.
- Le cas limite `doublon id_livre=1` est tranché.

## Lien avec la progression
- Séance : T09-S1 à T09-S4.
- TD : `T09_TD_bases_relationnelles_cles_contraintes.md`.
- TP : `T09_tp_bases_relationnelles_cles_contraintes.md`.
- Évaluation : `T09_evaluation_bases_relationnelles_cles_contraintes.md`.

## Services rendus par un SGBD relationnel

La capacité T-BDD-02 demande d'identifier les services rendus par un système de gestion de bases de données (SGBD) relationnel. Un SGBD n'est pas un simple fichier : il offre des services essentiels que l'application n'a pas à réimplémenter.

### Les quatre services fondamentaux

| Service | Rôle | Exemple |
|---------|------|---------|
| **Persistance** | Les données survivent à l'arrêt du programme ou de la machine | Un INSERT reste en base même après un redémarrage du serveur |
| **Gestion des accès concurrents** | Plusieurs utilisateurs lisent et écrivent simultanément sans corruption | Deux guichetiers réservent des places en parallèle sans vendre le même siège |
| **Efficacité des requêtes** | Le SGBD optimise l'accès aux données (index, plan d'exécution) | Une recherche par clé primaire ne parcourt pas toute la table |
| **Sécurisation et contrôle d'accès** | Droits par utilisateur, chiffrement, journalisation | Un élève peut lire les notes mais pas les modifier |

### Intégrité des données — un service transversal

L'intégrité (contraintes de clé primaire, clé étrangère, unicité, domaine) est un service que le SGBD applique automatiquement : il refuse toute opération qui violerait une contrainte, protégeant la cohérence des données sans que l'application n'ait à le vérifier.

### Cas limites

- Un fichier CSV offre la persistance mais aucun des trois autres services.
- SQLite offre persistance et intégrité mais gère mal la concurrence lourde.
- Redis est un magasin clé-valeur en mémoire (non relationnel) ; il offre la vitesse mais sa persistance est optionnelle et configurable (snapshots RDB, journalisation AOF).

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur bases relationnelles. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : relation, attribut, tuple, clé primaire, clé étrangère, contrainte, schéma, instance.
- Capacités reliées : T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- identifier la clé primaire d’une relation.
- contrôler une clé étrangère avec la table référencée.
- détecter une anomalie de redondance.

### Erreurs fréquentes spécifiques
- Un élève peut confondre tuple et attribut ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier une contrainte de domaine ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut créer une clé étrangère sans clé cible ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de bases relationnelles.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
