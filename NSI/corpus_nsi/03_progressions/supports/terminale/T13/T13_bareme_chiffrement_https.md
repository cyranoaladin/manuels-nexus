---
title: "T13 - bareme - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "bareme"
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

# T13 - Barème - chiffrement et HTTPS

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points : trois objectifs de sécurité nommés et reliés à des menaces.
- 3 points : justification de la combinaison asymétrique et symétrique.
- 3 points : vérification du certificat (domaine, validité, signature, chaîne de confiance).
- 2 points : cas limite `certificat expiré` décidé avec justification.

## Évaluation question par question
- Question 1 : 4 points sur T-ARCH-04A avec résultat `trois objectifs de sécurité nommés et justifiés`.
- Question 2 : 4 points sur T-ARCH-04B avec résultat `Ksession chiffrée avec Kpub pour l'échange, données chiffrées avec Ksession pour la rapidité`.
- Question 3 : 4 points sur T-ARCH-04A avec résultat `vérification du certificat sur domaine, validité, signature et chaîne de confiance`.
- Question 4 : 4 points sur T-ARCH-04B avec résultat `hachage / intégrité, chiffrement asymétrique / confidentialité, signature / authentification`.

## Critères observables
- Trace, table, valeur ou justification présente.
- Cas limite et erreur fréquente explicités.
