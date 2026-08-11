---
title: "T12 - version_amenagee - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - Version aménagée - routage RIP et OSPF

## Aides intégrées
- Donnée fournie : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
- Mots utiles : route, RIP, nombre de sauts, OSPF, coût.
- Méthode guidée : compter sauts RIP puis additionner coûts OSPF.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-ARCH-03 ou T-ARCH-03.
3. Compléter le résultat : RIP : A-B-D et A-C-D ont 2 sauts.
4. Cocher le cas limite : égalité exacte.

## Réponses rapides
- Réponse 1 : RIP : A-B-D et A-C-D ont 2 sauts.
- Réponse 2 : OSPF : A-B-D coût 10, A-C-D coût 11.
- Réponse 3 : panne B-D -> A-C-D coût 11.
