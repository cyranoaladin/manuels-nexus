---
title: "T09 - evaluation - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "evaluation"
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

# T09 - Évaluation - bases relationnelles, clés et contraintes

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-BDD-01A, T-BDD-01B, T-BDD-01C, T-BDD-02.

## Questions
### Question 1
- Capacité officielle : T-BDD-01A.
- Énoncé : à partir de `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`, identifier schéma et instance.
- Réponse attendue : le schéma est Livre(id_livre, titre) et Emprunt(id_emprunt, id_livre, nom) ; l'instance est l'ensemble des tuples fournis. id_livre est la clé primaire de Livre.
- Barème : 1 point donnée, 1 point méthode (distinguer schéma et instance), 1 point résultat (schéma nommé avec attributs), 1 point justification sur `clé primaire nulle`.
### Question 2
- Capacité officielle : T-BDD-01B.
- Énoncé : à partir de `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`, vérifier unicité id_livre.
- Réponse attendue : dans l'instance, id_livre prend les valeurs 1 et 2 (toutes distinctes) : la contrainte d'unicité de la clé primaire est respectée dans Livre. Le contenu confirme la structure.
- Barème : 1 point donnée, 1 point méthode (vérifier chaque valeur de clé), 1 point résultat (unicité confirmée), 1 point justification sur `doublon id_livre=1`.
### Question 3
- Capacité officielle : T-BDD-01C.
- Énoncé : à partir de `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`, contrôler Emprunt.id_livre.
- Réponse attendue : Emprunt(11,9,Sam) viole la contrainte de clé étrangère car id_livre=9 est absent de la table Livre — c'est une anomalie de référence.
- Barème : 1 point donnée, 1 point méthode (vérifier la clé étrangère contre la table cible), 1 point résultat (violation identifiée), 1 point justification sur `suppression référencée`.
### Question 4
- Capacité officielle : T-BDD-02.
- Énoncé : à partir de `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`, expliquer pourquoi le SGBD refuse l'insertion de Emprunt(11,9,Sam).
- Réponse attendue : le SGBD applique automatiquement le contrôle d'intégrité référentielle (un de ses services) et refuse l'insertion car id_livre=9 n'existe pas dans Livre. Autres services : persistance, concurrence, efficacité des requêtes.
- Barème : 1 point donnée, 1 point méthode (citer le service d'intégrité), 1 point résultat (refus expliqué), 1 point justification sur `service de persistance`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : schéma = Livre(id_livre, titre), Emprunt(id_emprunt, id_livre, nom) ; instance = les tuples donnés. id_livre est la clé primaire de Livre.
- Critère spécifique : identifier schéma et instance et éviter `attribut confondu avec valeur`.
### Corrigé question 2
- Résultat attendu : les valeurs de id_livre dans Livre sont 1 et 2 (distinctes) → unicité de la clé primaire respectée. La structure impose l'unicité, le contenu la confirme.
- Critère spécifique : vérifier unicité id_livre et éviter `clé étrangère supposée unique`.
### Corrigé question 3
- Résultat attendu : Emprunt(11,9,Sam) viole la clé étrangère car id_livre=9 est absent de Livre → anomalie de référence.
- Critère spécifique : contrôler Emprunt.id_livre et éviter `domaine ignoré`.
### Corrigé question 4
- Résultat attendu : le SGBD refuse l'insertion grâce au service d'intégrité référentielle ; les quatre services d'un SGBD sont persistance, concurrence, efficacité, sécurisation.
- Critère spécifique : identifier le service du SGBD qui refuse l'opération et éviter `service confondu avec contrainte`.

## Erreurs fréquentes et remédiation
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Cas limites travaillés
- clé primaire nulle.
- doublon id_livre=1.
- suppression référencée.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `Livre.id_livre identifie chaque livre`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T09 sur `bases_relationnelles_cles_contraintes`.

## Aménagement
- Version aménagée : `T09_version_amenagee_bases_relationnelles_cles_contraintes.md` ; consignes découpées et barème conservé.
