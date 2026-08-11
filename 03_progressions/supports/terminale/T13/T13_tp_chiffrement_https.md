---
title: "T13 - tp_papier - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "tp_papier"
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

# T13 - TP - chiffrement et HTTPS

## Statut du TP
TP papier : ce support n attend aucune ressource Python ; le livrable est une trace écrite vérifiable.

## Donnée fournie
Le serveur `banque.example` possède une clé publique `Kpub_serveur` et une clé privée `Kpriv_serveur`. Le client génère une clé de session `Ksession`. Le certificat est signé par `Autorité-Test`.

## Travail demandé
1. Nommer les trois objectifs de sécurité d'HTTPS et relier chacun à une menace concrète.
2. Expliquer pourquoi `Ksession` est chiffrée avec `Kpub_serveur` (asymétrique) avant d'être envoyée.
3. Expliquer pourquoi les données applicatives sont ensuite chiffrées avec `Ksession` (symétrique) et non avec `Kpub_serveur`.
4. Vérifier le certificat de `banque.example` : domaine, validité, signature d'Autorité-Test.
5. Traiter le cas limite `certificat expiré` : décider si le navigateur accepte ou refuse, et justifier.

## Barème associé
- 2 points : les trois objectifs de sécurité nommés et reliés à des menaces.
- 3 points : justification de la combinaison asymétrique (échange de clé) et symétrique (données).
- 3 points : vérification du certificat avec les quatre champs (domaine, validité, signature, chaîne de confiance).
- 2 points : cas limite `certificat expiré` décidé avec justification.

## Corrigé question par question
### Corrigé question 1
- Donnée : connexion à `https://banque.example` avec attaquant sur le réseau.
- Méthode : nommer chaque objectif de sécurité et le relier à une menace concrète.
- Résultat attendu : confidentialité (contenu illisible pour l'attaquant), intégrité (modification détectée), authentification du serveur (identité vérifiée via le certificat).
- Contrôle : en HTTP sans TLS, aucun des trois objectifs n'est assuré.
### Corrigé question 2
- Donnée : `Kpub_serveur`, `Kpriv_serveur`, `Ksession`.
- Méthode : expliquer le rôle de l'asymétrique dans l'échange de la clé de session.
- Résultat attendu : `Ksession` est chiffrée avec `Kpub_serveur` pour que seul le serveur (détenteur de `Kpriv_serveur`) puisse la déchiffrer.
- Contrôle : sans vérification du certificat, un attaquant pourrait substituer sa propre clé publique.
### Corrigé question 3
- Donnée : données applicatives volumineuses à chiffrer après l'échange de clé.
- Méthode : justifier le choix du symétrique pour les données par la rapidité.
- Résultat attendu : les données sont chiffrées avec `Ksession` car le chiffrement symétrique est plus rapide que l'asymétrique pour de grands volumes.
- Contrôle : utiliser uniquement l'asymétrique serait trop lent pour un échange HTTPS complet.
### Corrigé question 4
- Donnée : certificat de `banque.example` émis par Autorité-Test.
- Méthode : examiner chaque champ du certificat (domaine, validité, signature, chaîne de confiance).
- Résultat attendu : le navigateur vérifie que le domaine correspond à `banque.example`, que la date est dans la période de validité, que la signature d'Autorité-Test est valide et qu'Autorité-Test figure dans sa liste de confiance.
- Contrôle : le certificat prouve l'identité du serveur, il ne chiffre pas les données.
### Corrigé question 5
- Donnée : certificat dont la date de validité est dépassée.
- Méthode : décider si le navigateur accepte ou refuse la connexion.
- Résultat attendu : `certificat expiré` → refus de connexion, car la clé peut avoir été compromise depuis l'expiration.
- Contrôle : le refus protège l'utilisateur contre une clé potentiellement compromise.

## Liens
- TD lié : `T13_TD_chiffrement_https.md`.
- Évaluation liée : `T13_evaluation_chiffrement_https.md`.

## Cas limites travaillés
- certificat expiré.
- clé publique non vérifiée.
- HTTP sans TLS.

## Erreurs fréquentes
- clé publique supposée secrète.
- asymétrique utilisé partout sans justifier la clé de session.
- certificat ignoré ou confondu avec le chiffrement des données.

## Critères de réussite observables
- Les trois objectifs de sécurité sont nommés.
- Le rôle de chaque clé est identifié dans l'échange.
- Au moins un cas limite est décidé avec justification.
