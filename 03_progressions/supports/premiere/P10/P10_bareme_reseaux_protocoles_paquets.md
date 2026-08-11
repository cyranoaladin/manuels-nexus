---
title: "P10 - bareme - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "réseaux, protocoles et paquets"
notion: "réseaux, protocoles et paquets"
private_data: false
official_program:
  capacities:
    - "P-ARCH-02A"
    - "P-ARCH-02B"
    - "P-ARCH-02C"
    - "P-ARCH-04A"
    - "P-ARCH-04B"
---

# P10 - Barème - réseaux, protocoles et paquets

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- 3 points tâche `identifier champs de bout en bout`.
- 3 points résultat `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
- 2 points cas limite `TTL devient 0`.

## Évaluation question par question
- Question 1 : 4 points sur P-ARCH-02A avec résultat `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
- Question 2 : 4 points sur P-ARCH-02B avec résultat `MAC change à chaque saut, IP reste de bout en bout`.
- Question 3 : 4 points sur P-ARCH-02C avec résultat `M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1`.
- Question 4 : 4 points sur P-ARCH-04A avec résultat `TTL=1 devient 0 et le paquet est détruit`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
