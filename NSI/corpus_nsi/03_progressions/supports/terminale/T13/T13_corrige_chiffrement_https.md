---
title: "T13 - corrige - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "corrige"
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

# T13 - Corrigé - chiffrement et HTTPS

## Corrigé du TD

### Exercice 1

- Réponse attendue : confidentialité (l'attaquant ne lit pas le contenu), intégrité (les données ne sont pas modifiées sans détection), authentification du serveur (le client vérifie l'identité de `banque.example`).
- Méthode : nommer chaque objectif et le relier à une menace concrète sur le réseau.
- Cas limite : en HTTP sans TLS, aucun de ces trois objectifs n'est assuré.

### Exercice 2

- Réponse attendue : en HTTP, l'URL, le cookie et la réponse sont lisibles par l'attaquant ; en HTTPS, seuls les métadonnées TLS sont visibles, le contenu est chiffré.
- Méthode : comparer les deux captures pour identifier ce qui est exposé.
- Cas limite : HTTP sans TLS expose le cookie de session.

### Exercice 3

- Réponse attendue : `Ksession` est chiffrée avec `Kpub_serveur` (asymétrique) pour un échange sécurisé ; les données sont ensuite chiffrées avec `Ksession` (symétrique) pour la rapidité.
- Méthode : justifier la combinaison des deux types de chiffrement par les performances et la sécurité.
- Cas limite : clé publique non vérifiée — si le client ne vérifie pas le certificat, un attaquant pourrait substituer sa propre clé publique.

### Exercice 4

- Réponse attendue : le navigateur vérifie le domaine, la date de validité, la signature d'Autorité-Test et la présence d'Autorité-Test dans sa liste de confiance.
- Méthode : examiner chaque champ du certificat et son rôle dans la décision.
- Cas limite : certificat expiré — la date actuelle hors de la période de validité entraîne un refus.

### Exercice 5

- Réponse attendue : A — refusé (domaine incorrect), B — refusé (certificat expiré), C — refusé (auto-signé), D — refusé (autorité inconnue).
- Méthode : identifier le champ défaillant et le risque associé pour chaque scénario.
- Cas limite : certificat expiré, auto-signé, domaine incorrect, autorité inconnue.

### Exercice 6

- Réponse attendue : ordre 2-5-1-4-6-3 (ClientHello, ServerHello, certificat, vérification, échange de Ksession, échanges chiffrés).
- Méthode : classer chaque étape selon son rôle (négociation, authentification, échange de clé, chiffrement).
- Cas limite : clé publique non vérifiée — si l'étape 4 est omise, un attaquant peut injecter sa clé publique.

### Exercice 7

- Réponse attendue : S1 — hachage / intégrité, S2 — chiffrement asymétrique / confidentialité, S3 — signature numérique / authentification.
- Méthode : associer chaque situation à l'outil cryptographique correct et à la propriété de sécurité visée.
- Cas limite : confondre hachage et chiffrement conduit à croire qu'une empreinte peut être déchiffrée.

### Exercice 8

- Réponse attendue : F1 — HTTPS prouve la connexion chiffrée, pas l'honnêteté du site ; F2 — le certificat prouve l'identité, il ne chiffre pas les données ; F3 — la clé publique est diffusable, c'est la clé privée qui est secrète ; F4 — le cadenas indique un certificat vérifié, pas l'absence d'arnaque.
- Méthode : identifier la confusion précise et reformuler avec le vocabulaire technique.
- Cas limite : clé publique non vérifiée — croire que la clé publique est secrète empêche de comprendre l'asymétrique.

## Corrigé du TP

- Donnée : `Ksession, clé publique serveur Kpub, certificat signé par Autorité-Test`.
- Résultat principal : `Ksession` est chiffrée avec `Kpub_serveur` pour transmission sécurisée ; seul le serveur peut la déchiffrer avec `Kpriv_serveur`.
- Résultat secondaire : les données applicatives sont ensuite chiffrées avec `Ksession` (symétrique) pour la rapidité.

## Corrigé de l'évaluation

- Question 1 : les trois objectifs de sécurité sont nommés et reliés à des menaces concrètes (confidentialité, intégrité, authentification).
- Question 2 : `Ksession` est chiffrée avec `Kpub_serveur` ; les données sont chiffrées avec `Ksession` ; la combinaison est justifiée par les performances.
- Question 3 : le certificat est vérifié sur le domaine, la validité, la signature et la chaîne de confiance.
- Question 4 : chaque outil cryptographique est associé à sa propriété de sécurité ; hachage et chiffrement ne sont pas confondus.
