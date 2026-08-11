---
title: "T13 - version_amenagee - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "version_amenagee"
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

# T13 - Version aménagée - chiffrement et HTTPS

## Aides intégrées
- Donnée fournie : le serveur `banque.example` possède une clé publique `Kpub_serveur` et une clé privée `Kpriv_serveur`. Le client génère une clé de session `Ksession`.
- Mots utiles : chiffrement symétrique, chiffrement asymétrique, clé publique, clé privée, certificat, autorité de certification.
- Méthode guidée : d'abord identifier les objectifs de sécurité, puis expliquer l'échange de clé, puis vérifier le certificat.

## Exercice guidé
1. Nommer les trois objectifs de sécurité d'HTTPS : confidentialité, intégrité, authentification du serveur.
2. Choisir la capacité : T-ARCH-04A ou T-ARCH-04B.
3. Compléter : « Ksession est chiffrée avec ________________ pour que seul le serveur puisse la déchiffrer. »
4. Compléter : « Les données sont ensuite chiffrées avec ________________ car le chiffrement symétrique est plus rapide. »
5. Cocher le cas limite : certificat expiré — le navigateur doit-il accepter ou refuser la connexion ? Justifier.
6. Identifier le rôle de l'autorité de certification : elle signe le certificat pour garantir que la clé publique appartient bien au bon serveur.

## Repères enseignant — réponses de référence
- Réponse 1 : confidentialité (contenu illisible), intégrité (modification détectée), authentification (identité vérifiée).
- Réponse 2 : Ksession est chiffrée avec Kpub_serveur.
- Réponse 3 : les données sont chiffrées avec Ksession (symétrique).
- Réponse 4 : certificat expiré → refus, car la clé peut être compromise.
- Réponse 5 : Autorité-Test signe le certificat de banque.example pour attester que Kpub_serveur appartient bien à ce domaine.
