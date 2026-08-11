---
title: "T12 - evaluation - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "evaluation"
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

# T12 - Évaluation - routage RIP et OSPF

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ARCH-03.

## Questions
### Question 1
- Capacité officielle : T-ARCH-03.
- Énoncé : à partir de `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`, compter sauts RIP.
- Réponse attendue : RIP : A-B-D et A-C-D ont 2 sauts.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `égalité exacte`.
### Question 2
- Capacité officielle : T-ARCH-03.
- Énoncé : à partir de `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`, additionner coûts OSPF.
- Réponse attendue : OSPF : A-B-D coût 10, A-C-D coût 11.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `lien indisponible`.
### Question 3
- Capacité officielle : T-ARCH-03.
- Énoncé : à partir de `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`, choisir route en égalité documentée.
- Réponse attendue : panne B-D -> A-C-D coût 11.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `route inconnue`.
### Question 4
- Capacité officielle : T-ARCH-03.
- Énoncé : à partir de `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`, recalculer après panne.
- Réponse attendue : route inconnue -> rejet ou défaut.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `égalité exacte`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : RIP : A-B-D et A-C-D ont 2 sauts.
- Critère spécifique : compter sauts RIP et éviter `sauts et coûts mélangés`.
### Corrigé question 2
- Résultat attendu : OSPF : A-B-D coût 10, A-C-D coût 11.
- Critère spécifique : additionner coûts OSPF et éviter `choix visuel`.
### Corrigé question 3
- Résultat attendu : panne B-D -> A-C-D coût 11.
- Critère spécifique : choisir route en égalité documentée et éviter `panne non recalculée`.
### Corrigé question 4
- Résultat attendu : route inconnue -> rejet ou défaut.
- Critère spécifique : recalculer après panne et éviter `sauts et coûts mélangés`.

## Erreurs fréquentes et remédiation
- sauts et coûts mélangés.
- choix visuel.
- panne non recalculée.

## Cas limites travaillés
- égalité exacte.
- lien indisponible.
- route inconnue.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `RIP : A-B-D et A-C-D ont 2 sauts`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T12 sur `routage_rip_ospf`.

## Aménagement
- Version aménagée : `T12_version_amenagee_routage_rip_ospf.md` ; consignes découpées et barème conservé.
