---
title: "P08 - Référentiel de barème - Web"
level: "premiere"
sequence_id: "P08"
document_type: "bareme"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "HTML, CSS, DOM, HTTP et formulaires"
notion: "Orientation vers les barèmes disciplinaires"
private_data: false
official_program:
  capacities:
    - "P-IHM-01A"
    - "P-IHM-01B"
    - "P-IHM-02"
    - "P-IHM-03A"
    - "P-IHM-03B"
    - "P-IHM-03C"
    - "P-IHM-04A"
    - "P-IHM-04B"
    - "P-IHM-04C"
---

# P08 - Référentiel de barème - Web

## Barèmes d'évaluation à utiliser

- Sujet HTML, CSS et DOM : `P08_bareme_html_css_dom.md`.
- Sujet HTTP, formulaires et confidentialité : `P08_bareme_http_get_post_formulaires.md`.

Ces barèmes ne sont pas interchangeables. Le premier observe l'organisation des nœuds, la portée des sélecteurs, la trace d'événement et une modification du gestionnaire. Le second observe l'encodage des paramètres, le corps POST, l'ordre client-serveur, la retransmission des données et le choix motivé de GET, POST et HTTPS.

## Observables formatifs pour les TD et TP

### Famille HTML, CSS et DOM

1. L'élément ciblé existe dans le document fourni.
2. Le sélecteur désigne exactement l'ensemble demandé.
3. L'événement et la fonction associée sont distingués.
4. La trace contient valeur lue, condition, branche et effet sur le DOM.
5. La modification proposée reste testable sur un cas valide et un cas vide.

### Famille HTTP et formulaires

1. Les paramètres utilisent les attributs `name` du formulaire.
2. La route, l'URL ou le corps sont écrits explicitement.
3. Les actions du client et du serveur sont attribuées et ordonnées.
4. Stockage côté client et retransmission automatique sont distingués.
5. Le choix GET/POST/HTTPS est justifié par URL, historique, corps ou chiffrement.

## Règles de correction partielle

- Une bonne opération avec une justification vague conserve le point de choix, pas celui du raisonnement.
- Une trace correcte malgré une erreur de syntaxe locale conserve les points d'états intermédiaires.
- Une réponse qui affirme que POST chiffre, ou que `localStorage` est envoyé automatiquement, ne reçoit pas le point scientifique correspondant.
- Une modification de code qui fonctionne seulement sur le cas nominal ne reçoit pas le point de cas limite.
