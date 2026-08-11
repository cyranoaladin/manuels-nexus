---
title: "P10 - version_amenagee - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "version_amenagee"
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

# P10 - Version aménagée - réseaux, protocoles et paquets

## Aides intégrées
- Donnée fournie : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Mots utiles : IP source, IP destination, MAC locale, TCP, port 443.
- Méthode guidée : identifier champs de bout en bout puis distinguer MAC et IP.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : P-ARCH-02A ou P-ARCH-02B.
3. Compléter le résultat : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
4. Cocher le cas limite : TTL devient 0.

## Réponses rapides
- Réponse 1 : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Réponse 2 : MAC change à chaque saut, IP reste de bout en bout.
- Réponse 3 : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
