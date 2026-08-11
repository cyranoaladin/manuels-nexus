---
title: "P10 - evaluation - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "evaluation"
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

# P10 - Évaluation - réseaux, protocoles et paquets

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-ARCH-02A, P-ARCH-02B, P-ARCH-02C, P-ARCH-04A, P-ARCH-04B.

## Questions
### Question 1
- Capacité officielle : P-ARCH-02A.
- Énoncé : à partir de `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`, identifier champs de bout en bout.
- Réponse attendue : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `TTL devient 0`.
### Question 2
- Capacité officielle : P-ARCH-02B.
- Énoncé : à partir de `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`, distinguer MAC et IP.
- Réponse attendue : MAC change à chaque saut, IP reste de bout en bout.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `destination locale 192.168.1.34`.
### Question 3
- Capacité officielle : P-ARCH-02C.
- Énoncé : à partir de `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`, dérouler M0 ACK0 M1 perdu retransmission ACK1.
- Réponse attendue : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `ACK43 dupliqué`.
### Question 4
- Capacité officielle : P-ARCH-04A.
- Énoncé : à partir de `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`, décrémenter TTL avant retransmission.
- Réponse attendue : TTL=1 devient 0 et le paquet est détruit.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `TTL devient 0`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Critère spécifique : identifier champs de bout en bout et éviter `confondre MAC et IP`.
### Corrigé question 2
- Résultat attendu : MAC change à chaque saut, IP reste de bout en bout.
- Critère spécifique : distinguer MAC et IP et éviter `TTL pris pour une durée`.
### Corrigé question 3
- Résultat attendu : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Critère spécifique : dérouler M0 ACK0 M1 perdu retransmission ACK1 et éviter `réémettre un paquet TTL 0`.
### Corrigé question 4
- Résultat attendu : TTL=1 devient 0 et le paquet est détruit.
- Critère spécifique : décrémenter TTL avant retransmission et éviter `confondre MAC et IP`.

## Erreurs fréquentes et remédiation
- confondre MAC et IP.
- TTL pris pour une durée.
- réémettre un paquet TTL 0.

## Cas limites travaillés
- TTL devient 0.
- destination locale 192.168.1.34.
- ACK43 dupliqué.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P10 sur `reseaux_protocoles_paquets`.

## Aménagement
- Version aménagée : `P10_version_amenagee_reseaux_protocoles_paquets.md` ; consignes découpées et barème conservé.
