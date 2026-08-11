---
title: "P14 - cours - synthèse, projet et oral"
level: "premiere"
sequence_id: "P14"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "synthèse, projet et oral"
notion: "synthèse, projet et oral"
private_data: false
official_program:
  capacities:
    - "P-HIST-01"
---

# P14 - Cours - synthèse, projet et oral

## Objectifs spécifiques
- Identifier les données utiles de la situation : projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives.
- Employer le vocabulaire : cadrage de projet, dépôt propre, jeu de données fictif, démonstration, argumentation orale, repère historique.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- P-HIST-01.

## Situation-problème
projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives

## À savoir
- cadrage de projet.
- dépôt propre.
- jeu de données fictif.
- démonstration.
- argumentation orale.
- repère historique.
- limite.

## Méthodes
- formuler une question mesurable.
- définir entrée traitement sortie.
- préparer une démonstration.
- relier au Web ou aux bases de données.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives`.
- Méthode : formuler une question mesurable.
- Résultat attendu : question : pays fictifs dépassant 50% solaire.
- Contrôle : capacité P-HIST-01 et cas limite `donnée absente`.
### Exemple corrigé 2
- Donnée : `projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives`.
- Méthode : définir entrée traitement sortie.
- Résultat attendu : charger solaire.csv -> filtrer >50 -> tableau.
- Contrôle : capacité P-HIST-01 et cas limite `résultat vide`.
### Exemple corrigé 3
- Donnée : `projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives`.
- Méthode : préparer une démonstration.
- Résultat attendu : oral : problème, choix technique, résultat, limite.
- Contrôle : capacité P-HIST-01 et cas limite `question trop large`.
### Exemple corrigé 4
- Donnée : `projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives`.
- Méthode : relier au Web ou aux bases de données.
- Résultat attendu : repère historique cité avec source.
- Contrôle : capacité P-HIST-01 et cas limite `donnée absente`.

## Cas limites
- donnée absente.
- résultat vide.
- question trop large.

## Erreurs fréquentes
- code montré sans objectif.
- données personnelles.
- source historique non vérifiée.

## Exercices intégrés
1. Identifier les données utiles dans `projet énergie solaire fictive ; README, programme, solaire.csv, diaporama 4 diapositives`.
2. Appliquer : formuler une question mesurable.
3. Appliquer : définir entrée traitement sortie.
4. Décider le cas limite `donnée absente`.

## Critères de réussite observables
- Une capacité parmi P-HIST-01 est citée et utilisée.
- Le résultat attendu est explicite : question : pays fictifs dépassant 50% solaire.
- Le cas limite `résultat vide` est tranché.

## Lien avec la progression
- Séance : P14-S1 à P14-S4.
- TD : `P14_TD_synthese_projet_oral.md`.
- TP : `P14_tp_synthese_projet_oral.md`.
- Évaluation : `P14_evaluation_synthese_projet_oral.md`.

## Principaux événements de l'histoire de l'informatique

La capacité P-HIST-01 demande de situer dans le temps les principaux événements de l'histoire de l'informatique et leurs protagonistes.

### Frise chronologique structurée

| Date | Événement | Acteur(s) | Rupture technique |
|------|-----------|-----------|-------------------|
| 1936 | Machine de Turing (modèle théorique de calcul) | Alan Turing | Fondation théorique : tout calcul est une suite d'opérations élémentaires sur une bande |
| 1945 | Architecture von Neumann (programme stocké en mémoire) | John von Neumann | Le programme et les données partagent la même mémoire — un seul ordinateur peut exécuter n'importe quel programme |
| 1946 | ENIAC (premier calculateur électronique généraliste) | John Mauchly, J. Presper Eckert | Passage du mécanique (relais) à l'électronique (tubes à vide) — vitesse multipliée par 1000 |
| 1958-59 | Circuit intégré (Kilby 1958, Noyce 1959) | Jack Kilby (Texas Instruments), Robert Noyce (Fairchild) | Plusieurs transistors sur une seule puce de silicium — miniaturisation et fiabilité |
| 1971 | Microprocesseur Intel 4004 | Ted Hoff, Federico Faggin | Un processeur complet sur une seule puce — naissance de la micro-informatique |
| 1977 | Micro-ordinateurs personnels : Apple II (Jobs, Wozniak), TRS-80 (Tandy), Commodore PET (Peddle) | Jobs/Wozniak, Leininger/French, Chuck Peddle | Trois machines la même année — l'ordinateur entre dans les foyers |
| 1989 | Invention du World Wide Web | Tim Berners-Lee (CERN) | Hypertexte + HTTP + URL : l'information est liée et accessible universellement |
| 1991 | Ouverture publique du Web | Tim Berners-Lee | Premier navigateur et serveur Web publics — début de l'Internet grand public |

### Machine de Turing (1936)

Alan Turing propose un modèle abstrait de calcul : une machine lit et écrit des symboles sur une bande infinie selon des règles fixes. Ce modèle démontre qu'il existe des problèmes non calculables (problème de l'arrêt). La thèse de Church-Turing affirme que toute fonction calculable peut être calculée par une machine de Turing.

### Architecture von Neumann (1945)

John von Neumann décrit une architecture où le programme est stocké en mémoire avec les données. Avant cela, les calculateurs étaient câblés pour une tâche unique. L'architecture von Neumann (unité de contrôle, unité arithmétique, mémoire, entrées/sorties) reste le modèle dominant des ordinateurs actuels.

### Du circuit intégré au microprocesseur (1958-1971)

Le circuit intégré (Kilby 1958, Noyce 1959) regroupe plusieurs transistors sur une puce. En 1971, Intel produit le 4004 : un processeur complet (2300 transistors) sur une seule puce. La loi de Moore (1965) prédit le doublement du nombre de transistors tous les deux ans — elle s'est vérifiée pendant plus de 50 ans.

### Internet et le Web (1989-1991)

Tim Berners-Lee invente le Web au CERN en 1989 : il combine l'hypertexte (liens entre documents), le protocole HTTP et les URL. En 1991, le premier site Web est accessible publiquement. Le Web n'est pas Internet (réseau physique, années 1960-70) mais une application qui fonctionne sur Internet.

### Cas limites

- L'ENIAC (1946) n'est pas le premier ordinateur : le Colossus (1943, Bletchley Park) et le Z3 de Konrad Zuse (1941) le précèdent, mais l'ENIAC est le premier généraliste et entièrement électronique.
- Le Web (1991) n'est pas Internet (1969, ARPANET) : Internet est le réseau, le Web est un service qui utilise ce réseau.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur synthèse, projet et oral. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : problématique, démonstration, preuve de test, architecture, choix technique, carnet de bord.
- Capacités reliées : P-HIST-01.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- relier chaque fonctionnalité à une preuve de test.
- préparer une démonstration reproductible.
- expliquer un choix technique avec une contrainte.

### Erreurs fréquentes spécifiques
- Un élève peut présenter une interface sans expliquer l’algorithme ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut oublier la preuve de fonctionnement ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut confondre journal de bord et rapport final ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de synthèse, projet et oral.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
