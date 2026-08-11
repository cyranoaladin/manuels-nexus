---
title: "T12 - trace - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "trace"
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

# T12 - Trace - routage RIP et OSPF

## Trace courte
- Donnée : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
- Vocabulaire : route, RIP, nombre de sauts, OSPF, coût.
- Étape 1 : compter sauts RIP.
- Étape 2 : additionner coûts OSPF.
- Résultat de référence : RIP : A-B-D et A-C-D ont 2 sauts.

## Cas limites à mémoriser
- égalité exacte.
- lien indisponible.
- route inconnue.

## Erreurs fréquentes
- sauts et coûts mélangés.
- choix visuel.
- panne non recalculée.

## Critères de réussite observables
- Capacité : T-ARCH-03.
- Résultat final : OSPF : A-B-D coût 10, A-C-D coût 11.
- Cas limite : égalité exacte.
