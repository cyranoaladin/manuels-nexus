---
title: "P10 - corrige - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "corrige"
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

# P10 - Corrigé - réseaux, protocoles et paquets

## Corrigé du TD
### Exercice 1
- Réponse attendue : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Méthode : identifier champs de bout en bout.
- Cas limite : TTL devient 0.
### Exercice 2
- Réponse attendue : MAC change à chaque saut, IP reste de bout en bout.
- Méthode : distinguer MAC et IP.
- Cas limite : destination locale 192.168.1.34.
### Exercice 3
- Réponse attendue : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Méthode : dérouler M0 ACK0 M1 perdu retransmission ACK1.
- Cas limite : ACK43 dupliqué.
### Exercice 4
- Réponse attendue : TTL=1 devient 0 et le paquet est détruit.
- Méthode : décrémenter TTL avant retransmission.
- Cas limite : TTL devient 0.
### Exercice 5
- Réponse attendue : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Méthode : identifier champs de bout en bout.
- Cas limite : destination locale 192.168.1.34.
### Exercice 6
- Réponse attendue : MAC change à chaque saut, IP reste de bout en bout.
- Méthode : distinguer MAC et IP.
- Cas limite : ACK43 dupliqué.
### Exercice 7
- Réponse attendue : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Méthode : dérouler M0 ACK0 M1 perdu retransmission ACK1.
- Cas limite : TTL devient 0.
### Exercice 8
- Réponse attendue : TTL=1 devient 0 et le paquet est détruit.
- Méthode : décrémenter TTL avant retransmission.
- Cas limite : destination locale 192.168.1.34.

### Exercice 9
- Capacité mobilisée : P-ARCH-04A.
- Réponse attendue : capteurs (température, humidité) mesurent des grandeurs physiques ; actionneurs (ventilateur, arrosage) produisent des actions. Pseudo-code boucle avec seuils. Valeur aberrante filtrée.
- Méthode : classification capteur/actionneur, boucle de contrôle avec seuils, filtrage des valeurs aberrantes par moyenne ou rejet hors plage.
- Cas limite : deux seuils atteints simultanément → deux actionneurs actifs en parallèle.

### Exercice 10
- Capacité mobilisée : P-ARCH-04B.
- Réponse attendue : formulaire HTML avec 2 inputs + bouton + affichage. JavaScript split(".") et comparaison des 3 premiers octets avec validation des entrées. Tests : même réseau (/24) et réseaux différents.
- Méthode : construction formulaire HTML, récupération getElementById, découpage split("."), validation longueur, comparaison octets.
- Cas limite : champ vide → split renvoie un tableau trop court → afficher message d'erreur.

## Corrigé du TP
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Résultat principal : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Résultat secondaire : MAC change à chaque saut, IP reste de bout en bout.

## Corrigé de l évaluation
- Question 1 : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Question 2 : MAC change à chaque saut, IP reste de bout en bout.
- Question 3 : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Question 4 : TTL=1 devient 0 et le paquet est détruit.
