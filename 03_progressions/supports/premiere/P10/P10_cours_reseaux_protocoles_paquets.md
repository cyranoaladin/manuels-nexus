---
title: "P10 - cours - réseaux, protocoles et paquets"
level: "premiere"
sequence_id: "P10"
document_type: "cours"
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

# P10 - Cours - réseaux, protocoles et paquets

## Objectifs spécifiques
- Identifier les données utiles de la situation : src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24.
- Employer le vocabulaire : IP source, IP destination, MAC locale, TCP, port 443, TTL.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-ARCH-02A.
- P-ARCH-02B.
- P-ARCH-02C.
- P-ARCH-04A.
- P-ARCH-04B.

## Situation-problème
src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24

## À savoir
- IP source.
- IP destination.
- MAC locale.
- TCP.
- port 443.
- TTL.
- bit alterné.
- passerelle.

## Méthodes
- identifier champs de bout en bout.
- distinguer MAC et IP.
- dérouler M0 ACK0 M1 perdu retransmission ACK1.
- décrémenter TTL avant retransmission.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Méthode : identifier champs de bout en bout.
- Résultat attendu : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Contrôle : capacité P-ARCH-02A et cas limite `TTL devient 0`.
### Exemple corrigé 2
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Méthode : distinguer MAC et IP.
- Résultat attendu : MAC change à chaque saut, IP reste de bout en bout.
- Décision locale/passerelle : si `dst` appartient au préfixe `192.168.1.0/24`, l’hôte résout la MAC locale ; sinon il envoie le paquet à la passerelle.
- Contrôle : capacité P-ARCH-02B et cas limite `destination locale 192.168.1.34`.
### Exemple corrigé 3
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Méthode : dérouler M0 ACK0 M1 perdu retransmission ACK1.
- Résultat attendu : M0 -> ACK0 -> M1 perdu -> M1 retransmis -> ACK1.
- Contrôle : capacité P-ARCH-02C et cas limite `ACK43 dupliqué`.
### Exemple corrigé 4
- Donnée : `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
- Méthode : décrémenter TTL avant retransmission.
- Résultat attendu : TTL=1 devient 0 et le paquet est détruit.
- Contrôle : capacité P-ARCH-02A et cas limite `TTL devient 0`.

## Cas limites
- TTL devient 0.
- destination locale 192.168.1.34.
- ACK43 dupliqué.

## Erreurs fréquentes
- confondre MAC et IP.
- TTL pris pour une durée.
- réémettre un paquet TTL 0.

## Exercices intégrés
1. Identifier les données utiles dans `src=192.168.1.20, dst=172.16.0.8, TCP, port dst=443, TTL=4, LAN 192.168.1.0/24`.
2. Appliquer : identifier champs de bout en bout.
3. Appliquer : distinguer MAC et IP.
4. Décider le cas limite `TTL devient 0`.

## Critères de réussite observables
- Une capacité parmi P-ARCH-02A, P-ARCH-02B, P-ARCH-02C, P-ARCH-04A, P-ARCH-04B est citée et utilisée.
- Le résultat attendu est explicite : src=192.168.1.20 dst=172.16.0.8 TCP port 443 TTL 4.
- Le cas limite `destination locale 192.168.1.34` est tranché.

## Lien avec la progression
- Séance : P10-S1 à P10-S4.
- TD : `P10_TD_reseaux_protocoles_paquets.md`.
- TP : `P10_tp_reseaux_protocoles_paquets.md`.
- Évaluation : `P10_evaluation_reseaux_protocoles_paquets.md`.

## Identifier le rôle des capteurs et actionneurs

La capacité P-ARCH-04A demande d'identifier le rôle des capteurs et actionneurs dans un système informatique. Les objets connectés et systèmes embarqués illustrent cette capacité.

### Capteur

Un **capteur** mesure une grandeur physique (température, luminosité, pression, distance) et la convertit en signal numérique exploitable par un programme. Exemples :
- capteur de température (thermistance) → renvoie une valeur en degrés Celsius ;
- capteur de luminosité (photorésistance) → renvoie une valeur entre 0 (obscurité) et 1023 (lumière maximale) ;
- capteur ultrasonique → renvoie une distance en centimètres.

### Actionneur

Un **actionneur** reçoit une commande numérique et produit une action physique. Exemples :
- LED → s'allume ou s'éteint selon un signal binaire (0 ou 1) ;
- moteur → tourne à une vitesse proportionnelle à une valeur numérique ;
- buzzer → émet un son à une fréquence donnée.

### Chaîne capteur → traitement → actionneur

Un système embarqué typique suit le schéma : le capteur mesure une grandeur, le programme la traite (seuil, moyenne, comparaison), puis commande un actionneur en réponse.

Exemple concret : un capteur de température renvoie 32°C ; le programme compare au seuil 30°C ; l'actionneur (ventilateur) est activé.

```python
temperature = lire_capteur_temperature()   # capteur → valeur numérique
if temperature > 30:
    activer_ventilateur()                   # commande → actionneur
```

### Cas limites

- Un capteur peut renvoyer une valeur aberrante (bruit) : il faut filtrer (moyenne sur plusieurs mesures).
- Un actionneur sans capteur ne réagit pas à l'environnement : le programme fonctionne en boucle ouverte.

## Réaliser une IHM par programmation

La capacité P-ARCH-04B demande de réaliser par programmation une interface homme-machine (IHM) répondant à un cahier des charges. L'activité est bornée et reliée aux interactions Web ou objets.

### Qu'est-ce qu'une IHM ?

Une **interface homme-machine** est le moyen par lequel un utilisateur interagit avec un programme : saisir des données, cliquer sur un bouton, lire un résultat affiché. En Première NSI, on utilise des formulaires HTML ou des interfaces Python simples.

### Exemple : formulaire HTML pour calculer un prix TTC

Cahier des charges : l'utilisateur saisit un prix HT et un taux de TVA, clique sur « Calculer », et voit le résultat.

```html
<form id="ttc">
  <label>Prix HT : <input type="number" id="prixHT" step="0.01"></label>
  <label>Taux TVA : <input type="number" id="taux" step="0.01" value="0.20"></label>
  <button type="button" onclick="calculer()">Calculer</button>
  <p id="resultat"></p>
</form>

<script>
function calculer() {
    var ht = parseFloat(document.getElementById("prixHT").value);
    var taux = parseFloat(document.getElementById("taux").value);
    if (isNaN(ht) || isNaN(taux)) {
        document.getElementById("resultat").textContent = "Erreur : saisir des nombres valides.";
        return;
    }
    var ttc = ht * (1 + taux);
    document.getElementById("resultat").textContent = "Prix TTC : " + ttc.toFixed(2) + " €";
}
</script>
```

### Éléments d'un cahier des charges IHM

1. **Entrées** : quels champs l'utilisateur remplit (type, format, contraintes).
2. **Traitement** : quel calcul ou action le programme effectue.
3. **Sorties** : quel résultat est affiché et où.
4. **Validation** : que se passe-t-il si l'utilisateur entre une valeur invalide.

### Cas limites

- Champ vide : le programme doit afficher un message d'erreur, pas un résultat `NaN`.
- Valeur négative : selon le cahier des charges, soit rejeter soit traiter.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur réseaux, protocoles et paquets. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : adresse IP, adresse MAC, passerelle, TTL, paquet, protocole, port, routage.
- Capacités reliées : P-ARCH-02A, P-ARCH-02B, P-ARCH-02C, P-ARCH-04A, P-ARCH-04B.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- décrémenter le TTL à chaque routeur traversé.
- choisir la passerelle quand l’adresse de destination n’est pas locale.
- distinguer IP de bout en bout et MAC locale.

### Erreurs fréquentes spécifiques
- Un élève peut confondre MAC et IP ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier de supprimer un paquet dont le TTL devient 0 ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut choisir une route sans comparer les préfixes ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de réseaux, protocoles et paquets.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
