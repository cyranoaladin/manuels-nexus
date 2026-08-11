---
title: "P08 - Barème - HTTP, formulaires et confidentialité"
level: "premiere"
sequence_id: "P08"
document_type: "bareme"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "human_review_remediation"
theme: "Interaction client-serveur"
notion: "Critères observables GET, POST, HTTPS et stockage client"
private_data: false
official_program:
  capacities:
    - "P-IHM-03A"
    - "P-IHM-03B"
    - "P-IHM-03C"
    - "P-IHM-04A"
    - "P-IHM-04B"
    - "P-IHM-04C"
---

# P08 - Barème - HTTP, formulaires et confidentialité

## Principes

- Total : 20 points.
- Les points de choix GET/POST et les points de justification sont séparés.
- Dire seulement « plus sécurisé » ne vaut pas une justification : l'élève doit nommer URL, corps, historique, retransmission ou chiffrement.
- Les formes d'encodage équivalentes sont acceptées si les noms et valeurs transmis sont conservés.

### Barème question 1 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Construit `/catalogue?q=python&niveau=debutant` | 1,5 | 0,5 route ; 0,5 par paramètre correct |
| Situe les valeurs dans URL, barre d'adresse et historique potentiel | 1 | 0,5 pour l'URL seule |
| Justifie GET par la recherche partageable/non sensible | 0,75 | 0,25 si GET est choisi sans critère d'usage |
| Donne le cas vide avec `q=` et le niveau conservé | 0,75 | 0,5 si seul le paramètre de niveau est conservé |

### Barème question 2 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Identifie la route `/connexion` | 0,5 | aucun pour `/catalogue` |
| Écrit les deux paires du corps avec les attributs `name` | 1,25 | 0,5 par paire, 0,25 pour `&` |
| Indique que le mot de passe n'est pas dans l'URL mais dans le corps | 0,75 | 0,25 pour « non visible » sans emplacement |
| Explique que `type=password` masque seulement l'affichage | 0,75 | aucun si le chiffrement lui est attribué |
| Exige HTTPS pour chiffrer le transport | 0,75 | 0,25 pour HTTPS cité sans rôle |

### Barème question 3 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Ordonne correctement les quatre actions | 2 | 0,5 par position correcte |
| Attribue requête et affichage au client | 0,5 | 0,25 pour une seule attribution |
| Attribue vérification et construction de réponse au serveur | 0,5 | 0,25 pour une seule attribution |
| Justifie que données et autorisation ne doivent pas dépendre du seul client | 1 | 0,5 pour « sécurité » sans contournement ou responsabilité |

### Barème question 4 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Cookie : client, session, retransmission automatique compatible avec `Path` | 1,25 | 0,25 par propriété correcte, plafond 1,25 |
| localStorage : client, persistant, non retransmis | 0,75 | 0,25 par propriété |
| sessionStorage : client, durée de l'onglet/session, non retransmis | 0,75 | 0,25 par propriété |
| Explique `Secure` | 0,625 | 0,25 pour « sécurisé » sans HTTPS |
| Explique `HttpOnly` | 0,625 | 0,25 pour « caché » sans JavaScript |

### Barème question 5 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Recherche : GET justifié par URL partageable | 0,75 | 0,25 pour GET seul |
| Connexion : POST + HTTPS, avec rôles distincts | 1,25 | 0,5 pour POST, 0,5 pour HTTPS, 0,25 pour la distinction |
| Thème local : localStorage et aucune transmission nécessaire | 0,75 | 0,25 pour stockage client non nommé |
| Explique que GET expose le secret dans URL/historique malgré HTTPS | 1,25 | 0,5 URL, 0,5 historique/logs, 0,25 rôle limité de HTTPS |

**Total : 4 + 4 + 4 + 4 + 4 = 20 points.**
