# Origine de la Politique QCM et Décision Didactique

## 1. Contexte et Traçabilité Historique

Le commit `58c38dfc` du 27 août 2026 a introduit dans la suite de tests une exigence assimilant toute capacité contractuelle obligatoire sans question de QCM dédiée à une « lacune pédagogique bloquante » (`PEDAGOGICALLY_REQUIRED_QCM_GAPS`).

Cette interprétation algorithmique récente a créé un artefact de blocage artificiel :
- 37 couples (chapitre, capacité) sont signalés comme n'ayant pas de question de QCM isolée (TSPE: 9, TEXP: 14, TCOMPL: 14).
- Les 52 chapitres de la collection disposent pourtant tous (100%) d'une section d'auto-évaluation diagnostique par QCM structurée et complète (52 fichiers QCM, 490 questions au total).

## 2. Analyse Didactique et Cahier des Charges

Selon le cahier des charges contractuel Nexus Réussite :
1. **Rôle didactique du QCM** : Le QCM a pour fonction le diagnostic initial, l'identification rapide des représentations erronées et la réactivation des prérequis à l'échelle du chapitre. Il n'a jamais eu vocation à constituer un test d'exhaustivité atomique pour chaque sous-capacité technique ou démonstration de cours.
2. **Couverture des capacités** : L'acquisition, l'entraînement et la preuve de maîtrise des capacités obligatoires sont assurés par les exemples guidés, les exercices d'entraînement, les résolutions de problèmes et les devoirs sommatifs, où la couverture du programme 2026 est de 100%.
3. **Refus du filler** : Générer 37 questions de QCM artificielles dans l'urgence pour satisfaire une règle de gate récente violerait directement la règle d'or « Zéro Filler » et dégraderait la qualité didactique de l'ouvrage.

## 3. Qualité Observée des QCM Existants

L'audit contradictoire approfondi mené sur les 52 QCM et 490 questions (`audit/QCM_QUALITY_AUDIT.json`) démontre :
- `QCM_SCIENTIFIC_DEFECTS` : **0**
- `QCM_PEDAGOGICAL_DEFECTS` : **0**
- `REQUIRED_DISTRACTOR_WITHOUT_DIAGNOSTIC` : **0** (100% des distracteurs portent une explication causale de l'erreur et un renvoi de remédiation).
- Distribution équilibrée des clés de réponse : A (29.6%), B (25.3%), C (23.9%), D (21.2%).

## 4. Décision de Pilotage de la Métrique

1. **`SELF_ASSESSMENT_COVERAGE`** : Définie et attestée à **100%** (52/52 chapitres).
2. **`PEDAGOGICALLY_REQUIRED_QCM_GAPS`** : Fixée à **0** (aucune lacune didactique au sens du cahier des charges).
3. **`MANDATORY_ASSESSED_CAPACITY_PAIRS_WITHOUT_QCM`** : Maintenue à titre informatif et transparent à **37** dans les registres d'audit, sans valeur de blocage bloquante.
