---
title: "T13 - remediation - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "remediation"
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

# T13 - Remédiation - chiffrement et HTTPS

## Diagnostic
- clé publique supposée secrète.
- asymétrique utilisé partout sans justifier la clé de session.
- certificat ignoré ou confondu avec le chiffrement des données.
- hachage confondu avec chiffrement.

## Activités correctives
1. Nommer les trois objectifs de sécurité d'HTTPS (confidentialité, intégrité, authentification) et relier chacun à une menace concrète.
2. Expliquer pourquoi `Ksession` est chiffrée avec `Kpub_serveur` et pourquoi les données sont chiffrées avec `Ksession`, en précisant le rôle de chaque clé.
3. Vérifier un certificat : identifier le domaine, la validité, la signature de l'autorité et la chaîne de confiance.
4. Traiter le cas limite `certificat expiré` en expliquant le risque.
5. Relier chaque réponse à T-ARCH-04A ou T-ARCH-04B.

## Critères de sortie
- Les trois objectifs de sécurité sont nommés.
- Le rôle de chaque clé est identifié.
- Cas limite décidé avec justification.
