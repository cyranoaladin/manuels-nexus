---
title: "T11 - version_amenagee - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "version_amenagee"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "SoC, processus, ordonnancement et interblocage"
notion: "SoC, processus, ordonnancement et interblocage"
private_data: false
official_program:
  capacities:
    - "T-ARCH-01"
    - "T-ARCH-02A"
    - "T-ARCH-02B"
    - "T-ARCH-02C"
---

# T11 - Version aménagée - SoC, processus, ordonnancement et interblocage

## Aides intégrées
- Donnée fournie : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Mots utiles : système sur puce, processus, état prêt, état bloqué, ordonnancement.
- Méthode guidée : identifier CPU mémoire interfaces puis décrire création de processus.

## Exercice guidé
1. Recopier la donnée utile.
2. Choisir la capacité : T-ARCH-01 ou T-ARCH-02A.
3. Compléter le résultat : P1 20 ms, P2 20 ms, P1 20 ms.
4. Cocher le cas limite : un seul processus prêt.

## Réponses rapides
- Réponse 1 : P1 20 ms, P2 20 ms, P1 20 ms.
- Réponse 2 : P1 attend journal et P2 attend camera.
- Réponse 3 : CPU + mémoire + contrôleur caméra intégrés.
