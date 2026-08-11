---
title: "P10 - tp - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "tp"
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

# P10 - TP - réseaux, protocoles et paquets

## Statut du TP
TP exécutable : le livrable élève est un fichier Python de simulation réseau simplifiée vérifié par tests.

## Donnée fournie
`src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : identifier champs de bout en bout.
3. Réaliser : distinguer MAC et IP.
4. Tester le cas limite `TTL=1` : après décrément, `TTL=0`, le paquet est supprimé.
5. Produire le livrable : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
6. Programmer la décision de route par préfixe : destination `192.168.1.34`, préfixe `192.168.1.0/24`, décision `locale` ; sinon passer par la passerelle `192.168.1.1`.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
- 2 points : cas limite `TTL devient 0`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
### Corrigé question 2
Résultat attendu : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
### Corrigé question 3
Résultat attendu : MAC change à chaque saut, IP reste de bout en bout.
### Corrigé question 4
Résultat attendu : avec `TTL=1`, le routeur calcule `TTL=0` après décrément et supprime le paquet.
### Corrigé question 5
Résultat attendu : destination `192.168.1.34`, préfixe `192.168.1.0/24`, route locale ; destination `172.16.0.8`, même préfixe local, route passerelle `192.168.1.1`.

## Liens
- TD lié : `P10_TD_reseaux_protocoles_paquets.md`.
- Évaluation liée : `P10_evaluation_reseaux_protocoles_paquets.md`.

## Cas limites travaillés
- TTL devient 0.
- destination locale 192.168.1.34 dans le préfixe 192.168.1.0/24 ; si la destination n est pas locale, utiliser la passerelle 192.168.1.1.
- ACK43 dupliqué.

## Erreurs fréquentes
- confondre MAC et IP.
- TTL pris pour une durée.
- réémettre un paquet TTL 0.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4`.
- Au moins un cas limite de la section précédente est décidé.

## Assets Python
- Starter élève : `code/P10_starter_reseaux_protocoles_paquets.py`.
- Tests attendus : `code/P10_tests_attendus_reseaux_protocoles_paquets.py`.
- Corrigé professeur : `code/P10_corrige_professeur_reseaux_protocoles_paquets.py`.
- Fonctions à compléter : `decrementer_ttl`, `decision_route`, `port_service`.
- Cas testés : TTL nominal, TTL tombant à zéro, destination locale, passerelle, HTTP/HTTPS.
