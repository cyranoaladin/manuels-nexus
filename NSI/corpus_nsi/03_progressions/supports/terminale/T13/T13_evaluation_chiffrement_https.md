---
title: "T13 - evaluation - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "evaluation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "chiffrement et HTTPS"
notion: "chiffrement et HTTPS"
private_data: false
official_program:
  capacities:
    - "T-ARCH-04A"
    - "T-ARCH-04B"
---

# T13 - Évaluation - chiffrement et HTTPS

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ARCH-04A, T-ARCH-04B.

## Questions
### Question 1
- Capacité officielle : T-ARCH-04A.
- Énoncé : un navigateur se connecte à `https://boutique.example`. Nommez les trois objectifs de sécurité assurés par HTTPS et expliquez, pour chacun, ce que l'utilisation de HTTPS empêche un attaquant de faire.
- Réponse attendue : confidentialité (contenu illisible pour l'attaquant), intégrité (modification détectée), authentification du serveur (identité vérifiée via le certificat).
- Barème : 1 point par objectif nommé correctement, 1 point pour la justification d'au moins un cas limite (par exemple HTTP sans TLS).
### Question 2
- Capacité officielle : T-ARCH-04B.
- Énoncé : le serveur `boutique.example` possède une clé publique `Kpub` et une clé privée `Kpriv`. Le client génère une clé de session `Ksession`. Expliquez pourquoi `Ksession` est chiffrée avec `Kpub` pour l'échange, puis pourquoi les données applicatives sont chiffrées avec `Ksession` (symétrique) et non avec `Kpub` (asymétrique).
- Réponse attendue : `Ksession` chiffrée avec `Kpub` pour que seul le serveur puisse la déchiffrer ; symétrique ensuite pour la rapidité sur de grands volumes.
- Barème : 1 point donnée exacte, 1 point méthode (rôle de chaque clé), 1 point résultat vérifiable, 1 point justification sur `clé publique non vérifiée`.
### Question 3
- Capacité officielle : T-ARCH-04A.
- Énoncé : le certificat de `boutique.example` contient le domaine, la clé publique, l'émetteur Autorité-Test et une date de validité. Expliquez comment le navigateur vérifie ce certificat. Que se passe-t-il si le certificat est expiré ?
- Réponse attendue : vérification du domaine, de la validité, de la signature de l'autorité et de la chaîne de confiance ; certificat expiré entraîne un refus de connexion.
- Barème : 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification sur `certificat expiré`.
### Question 4
- Capacité officielle : T-ARCH-04B.
- Énoncé : associez chaque usage à l'outil cryptographique adapté : (a) vérifier qu'un fichier n'a pas été modifié, (b) transmettre `Ksession` au serveur de façon confidentielle, (c) prouver qu'un certificat a été émis par une autorité reconnue. Pour chaque cas, nommez la propriété de sécurité assurée.
- Réponse attendue : (a) hachage / intégrité, (b) chiffrement asymétrique / confidentialité, (c) signature numérique / authentification.
- Barème : 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification (distinction hachage / chiffrement).

## Corrigé question par question
### Corrigé question 1
- Donnée : connexion à `https://boutique.example` avec attaquant sur le réseau.
- Méthode : nommer chaque objectif et le relier à une menace concrète.
- Résultat attendu : confidentialité (contenu illisible pour l'attaquant), intégrité (modification détectée), authentification du serveur (identité vérifiée via le certificat).
- Contrôle : en HTTP sans TLS, aucun des trois objectifs n'est assuré ; éviter `clé publique supposée secrète`.
### Corrigé question 2
- Donnée : `Kpub`, `Kpriv` et `Ksession` pour `boutique.example`.
- Méthode : distinguer le rôle de l'asymétrique (échange de clé) et du symétrique (chiffrement des données).
- Résultat attendu : `Ksession` chiffrée avec `Kpub` pour que seul le serveur puisse la déchiffrer ; données chiffrées avec `Ksession` car le symétrique est plus rapide pour de grands volumes.
- Contrôle : utiliser uniquement l'asymétrique serait trop lent ; éviter `asymétrique utilisé partout`.
### Corrigé question 3
- Donnée : certificat de `boutique.example` émis par Autorité-Test avec domaine, clé publique et date de validité.
- Méthode : examiner chaque champ du certificat et son rôle dans la décision d'acceptation.
- Résultat attendu : vérification du domaine, de la validité, de la signature d'Autorité-Test et de la chaîne de confiance ; certificat expiré entraîne un refus.
- Contrôle : le certificat prouve l'identité du serveur, il ne chiffre pas les données ; éviter `certificat ignoré`.
### Corrigé question 4
- Donnée : trois cas — vérifier un fichier, transmettre `Ksession`, prouver l'émetteur d'un certificat.
- Méthode : associer chaque cas à l'outil cryptographique et à la propriété de sécurité.
- Résultat attendu : (a) hachage via SHA-256, intégrité ; (b) chiffrement asymétrique via `Kpub_serveur`, confidentialité ; (c) signature numérique via clé privée de l'autorité, authentification.
- Contrôle : le hachage n'est pas réversible et ne doit pas être confondu avec le chiffrement ; éviter `certificat ignoré`.

## Erreurs fréquentes et remédiation
- clé publique supposée secrète.
- asymétrique utilisé partout sans justifier la clé de session.
- certificat ignoré ou confondu avec le chiffrement.
- hachage confondu avec chiffrement.

## Cas limites travaillés
- certificat expiré.
- clé publique non vérifiée.
- HTTP sans TLS.

## Critères de réussite observables
- Les trois objectifs de sécurité sont nommés et reliés à des menaces.
- Le rôle de chaque clé est identifié dans l'échange HTTPS.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point par objectif nommé, 1 point justification cas limite (total 4 points).
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T13 sur `chiffrement_https`.

## Aménagement
- Version aménagée : `T13_version_amenagee_chiffrement_https.md` ; consignes découpées et barème conservé.
