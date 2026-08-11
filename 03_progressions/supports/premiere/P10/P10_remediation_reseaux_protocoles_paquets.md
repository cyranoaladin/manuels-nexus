---
title: "P10 - remediation - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "remediation"
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

# P10 - Remédiation - réseaux, protocoles et paquets

## Diagnostic
- confondre MAC et IP.
- TTL pris pour une durée.
- réémettre un paquet TTL 0.

## Activités correctives
1. Annoter `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
2. Refaire la tâche `identifier champs de bout en bout` et comparer avec `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
3. Traiter le cas limite `TTL devient 0`.
4. Relier la réponse à P-ARCH-02A.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
