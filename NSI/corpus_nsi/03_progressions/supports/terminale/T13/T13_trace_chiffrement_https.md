---
title: "T13 - trace - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "trace"
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

# T13 - Trace - chiffrement et HTTPS

## Trace courte
- Donnée : le serveur `banque.example` possède `Kpub_serveur` et `Kpriv_serveur` ; le client génère `Ksession` ; le certificat est signé par Autorité-Test.
- Vocabulaire : chiffrement symétrique, chiffrement asymétrique, clé publique, clé privée, clé de session, certificat, autorité de certification, TLS.
- Étape 1 : identifier les trois objectifs de sécurité (confidentialité, intégrité, authentification).
- Étape 2 : protéger Ksession par asymétrique (chiffrer avec Kpub_serveur).
- Étape 3 : utiliser symétrique pour les données applicatives (chiffrer avec Ksession).
- Résultat de référence : la connexion HTTPS combine asymétrique pour l'échange de clé et symétrique pour les données.

## Cas limites à mémoriser
- certificat expiré.
- clé publique non vérifiée.
- HTTP sans TLS.
- certificat auto-signé.

## Erreurs fréquentes
- clé publique supposée secrète.
- asymétrique utilisé partout sans justifier la clé de session.
- certificat ignoré ou confondu avec le chiffrement.
- hachage confondu avec chiffrement.

## Critères de réussite observables
- Capacité : T-ARCH-04A, T-ARCH-04B.
- Résultat final : les trois objectifs de sécurité sont nommés ; le rôle de chaque clé est identifié.
- Cas limite : certificat expiré entraîne un refus de connexion.

## Repères enseignant — résultats attendus
- Résultat de référence : Ksession chiffrée avec Kpub_serveur pour l'échange sécurisé.
- Résultat final : données applicatives chiffrées avec Ksession (symétrique) pour la rapidité.
