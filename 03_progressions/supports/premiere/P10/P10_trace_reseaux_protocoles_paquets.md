---
title: "P10 - trace - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "trace"
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

# P10 - Trace - réseaux, protocoles et paquets

## Trace courte
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Vocabulaire : IP source, IP destination, MAC locale, TCP, port 443.
- Étape 1 : identifier champs de bout en bout.
- Étape 2 : distinguer MAC et IP.
- Résultat de référence : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.

## Cas limites à mémoriser
- TTL devient 0.
- destination locale 192.168.1.34.
- ACK43 dupliqué.

## Erreurs fréquentes
- confondre MAC et IP.
- TTL pris pour une durée.
- réémettre un paquet TTL 0.

## Critères de réussite observables
- Capacité : P-ARCH-02A.
- Résultat final : MAC change à chaque saut, IP reste de bout en bout.
- Cas limite : TTL devient 0.
