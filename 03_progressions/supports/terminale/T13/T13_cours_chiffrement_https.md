---
title: "T13 - cours - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "cours"
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

# T13 - Cours - chiffrement et HTTPS

## Objectifs spécifiques
- Identifier les objectifs de sécurité d'une connexion HTTPS : confidentialité, intégrité, authentification du serveur.
- Employer le vocabulaire : chiffrement symétrique, chiffrement asymétrique, clé publique, clé privée, clé de session, certificat, autorité de certification, TLS.
- Distinguer chiffrement, hachage et signature numérique et associer chaque outil à sa propriété de sécurité.

## Capacités officielles
- T-ARCH-04A.
- T-ARCH-04B.

## Situation-problème
Un navigateur se connecte à `https://banque.example`. Le serveur possède une paire de clés (Kpub_serveur, Kpriv_serveur) et un certificat signé par Autorité-Test. Le client génère une clé de session Ksession pour chiffrer les échanges.

## À savoir
- chiffrement symétrique : une seule clé partagée, rapide, utilisé pour les données applicatives.
- chiffrement asymétrique : paire clé publique / clé privée, plus lent, utilisé pour l'échange sécurisé de la clé de session.
- clé publique : diffusable, sert à chiffrer ou vérifier une signature.
- clé privée : secrète, sert à déchiffrer ou signer.
- certificat : document liant un domaine à une clé publique, signé par une autorité de certification.
- autorité de certification : tiers de confiance qui signe les certificats.
- échange de clé : le client chiffre Ksession avec Kpub_serveur ; seul le serveur peut la déchiffrer.
- HTTPS : HTTP protégé par TLS, sur le port 443.
- TLS : protocole entre TCP et HTTP qui assure confidentialité, intégrité et authentification.
- hachage : fonction à sens unique qui produit une empreinte fixe pour vérifier l'intégrité.
- signature numérique : chiffrement d'une empreinte avec une clé privée pour garantir l'authenticité.

## Méthodes
- identifier les trois objectifs de sécurité (confidentialité, intégrité, authentification).
- comparer ce qui est visible en HTTP et ce qui est protégé en HTTPS.
- protéger Ksession par asymétrique puis utiliser symétrique pour données.
- vérifier un certificat : domaine, validité, signature de l'autorité, chaîne de confiance.
- distinguer chiffrement, hachage et signature.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : connexion à `https://banque.example` avec un attaquant sur le réseau.
- Méthode : nommer les trois objectifs de sécurité.
- Résultat attendu : confidentialité (contenu illisible), intégrité (modification détectée), authentification (identité du serveur vérifiée).
- Contrôle : capacité T-ARCH-04A ; en HTTP sans TLS, aucun objectif n'est assuré.
### Exemple corrigé 2
- Donnée : `Kpub_serveur`, `Kpriv_serveur`, `Ksession`.
- Méthode : protéger Ksession par asymétrique puis utiliser symétrique pour données.
- Résultat attendu : Ksession chiffrée avec Kpub_serveur pour l'échange, puis données chiffrées avec Ksession pour la rapidité.
- Contrôle : capacité T-ARCH-04B ; si la clé publique n'est pas vérifiée via le certificat, un attaquant peut la substituer.
### Exemple corrigé 3
- Donnée : certificat de `banque.example` émis par Autorité-Test.
- Méthode : vérifier domaine, validité, signature de l'émetteur, chaîne de confiance.
- Résultat attendu : le navigateur accepte si tous les champs sont valides ; il refuse en cas de certificat expiré, domaine incorrect ou autorité inconnue.
- Contrôle : capacité T-ARCH-04A ; le certificat ne chiffre pas les données.
### Exemple corrigé 4
- Donnée : trois situations (empreinte SHA-256, chiffrement de Ksession, signature de certificat).
- Méthode : distinguer hachage, chiffrement asymétrique et signature numérique.
- Résultat attendu : hachage = intégrité, chiffrement asymétrique = confidentialité, signature = authentification.
- Contrôle : capacité T-ARCH-04A ; le hachage n'est pas réversible et ne doit pas être confondu avec le chiffrement.

## Cas limites
- certificat expiré.
- clé publique non vérifiée.
- HTTP sans TLS.
- certificat auto-signé.
- domaine ne correspondant pas au certificat.

## Erreurs fréquentes
- clé publique supposée secrète.
- asymétrique utilisé partout sans justifier la clé de session.
- certificat ignoré ou confondu avec le chiffrement des données.
- hachage confondu avec chiffrement.

## Exercices intégrés
1. Nommer les trois objectifs de sécurité d'HTTPS à partir d'un scénario d'interception.
2. Comparer ce qu'un attaquant voit en HTTP et en HTTPS.
3. Expliquer pourquoi Ksession est chiffrée avec Kpub_serveur et pourquoi les données sont chiffrées avec Ksession.
4. Décider le cas limite `certificat expiré` en examinant les champs du certificat.

## Critères de réussite observables
- Les trois objectifs de sécurité sont nommés et reliés à des menaces concrètes.
- Le rôle de chaque clé (publique, privée, de session) est identifié dans l'échange HTTPS.
- Le cas limite `certificat expiré` est tranché avec justification.

## Lien avec la progression
- Séance : T13-S1 à T13-S4.
- TD : `T13_TD_chiffrement_https.md`.
- TP : `T13_tp_chiffrement_https.md`.
- Évaluation : `T13_evaluation_chiffrement_https.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur chiffrement et HTTPS. La notion ne se réduit pas à une liste de mots : on part d'une situation observable (connexion HTTPS), on nomme les objets manipulés (clés, certificat, autorité), puis on applique une méthode vérifiable (vérification du certificat, échange de clé, chiffrement des données) avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : clé publique, clé privée, clé de session, certificat, TLS, port 443, empreinte, autorité de certification, hachage, signature numérique.
- Capacités reliées : T-ARCH-04A, T-ARCH-04B.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- expliquer le rôle du certificat serveur et de la chaîne de confiance.
- distinguer chiffrement symétrique et asymétrique et justifier leur combinaison.
- repérer le port 443 et le protocole TLS dans un échange HTTPS.
- distinguer chiffrement, hachage et signature numérique.

### Erreurs fréquentes spécifiques
- Un élève peut confondre hachage et chiffrement ; la correction consiste à reprendre la définition (le hachage n'est pas réversible) puis à vérifier sur un exemple.
- Un élève peut faire transiter une clé privée ; la correction consiste à rappeler que seule la clé publique est diffusée.
- Un élève peut croire que HTTPS garantit l'honnêteté du site ; la correction consiste à distinguer chiffrement de la connexion et fiabilité du contenu.

### Cas limites à contrôler
- Cas minimal : certificat expiré, domaine incorrect.
- Cas ambigu : certificat auto-signé, autorité de certification inconnue.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de chiffrement et HTTPS et leurs propriétés de sécurité.
- Savoir-faire : appliquer une méthode contrôlable (vérification de certificat, échange de clé) à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre (négociation, authentification, échange de clé, chiffrement), puis vérifier par un cas limite.
