---
title: "T12 - corrige - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - Corrigé - routage RIP et OSPF

## Corrigé du TD
### Exercice 1
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Méthode : compter sauts RIP.
- Cas limite : égalité exacte.
### Exercice 2
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Méthode : additionner coûts OSPF.
- Cas limite : lien indisponible.
### Exercice 3
- Réponse attendue : panne B-D -> A-C-D coût 11.
- Méthode : choisir route en égalité documentée.
- Cas limite : route inconnue.
### Exercice 4
- Réponse attendue : route inconnue -> rejet ou défaut.
- Méthode : recalculer après panne.
- Cas limite : égalité exacte.
### Exercice 5
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Méthode : compter sauts RIP.
- Cas limite : lien indisponible.
### Exercice 6
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Méthode : additionner coûts OSPF.
- Cas limite : route inconnue.
### Exercice 7
- Réponse attendue : panne B-D -> A-C-D coût 11.
- Méthode : choisir route en égalité documentée.
- Cas limite : égalité exacte.
### Exercice 8
- Réponse attendue : route inconnue -> rejet ou défaut.
- Méthode : recalculer après panne.
- Cas limite : lien indisponible.

## Corrigé du TP
- Donnée : `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
- Résultat principal : RIP : A-B-D et A-C-D ont 2 sauts.
- Résultat secondaire : OSPF : A-B-D coût 10, A-C-D coût 11.

## Corrigé de l évaluation
- Question 1 : RIP : A-B-D et A-C-D ont 2 sauts.
- Question 2 : OSPF : A-B-D coût 10, A-C-D coût 11.
- Question 3 : panne B-D -> A-C-D coût 11.
- Question 4 : route inconnue -> rejet ou défaut.
