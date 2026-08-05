# LOT 0 — Contrat du chapitre TSPE-SUITES-LIMITES

## Date : 18 juillet 2026

## Referentiel
- Source : `referentiel/capacites_TSPE_SUITES_LIMITES.json`
- BO : special n 8 du 25 juillet 2019, section Analyse / Suites
- 7 capacites, 4 demonstrations exigibles (C4, C5, C6, C7)

## Capacites
- C1 : Convergence/divergence d'une suite
- C2 : Raisonnement par recurrence
- C3 : Modelisation par suites
- C4 : Suite croissante non majoree -> +infini (demo exigible)
- C5 : Inegalite de Bernoulli et limite de q^n (demo exigible)
- C6 : Theoreme de comparaison (demo exigible)
- C7 : Limites de l'exponentielle (demo exigible)

## Specificites Terminale
- 4 demonstrations exigibles (environnement \demonstration)
- Preparation epreuve ecrite : sujets type bac dans les evaluations
- Piste Grand Oral : modelisation de phenomenes d'evolution (C3)

## Cout API estime : ~0 $

## Audit de reprise — 2026-08-05 (branche `terminale/collection-v1`)

Contrat repris tel quel (pas de reecriture) apres verification :
- **Couverture referentiel** : 7/7 capacites de `referentiel/capacites_TSPE_SUITES_LIMITES.json`
  presentes dans `contrat.yaml`, correspondance id a id (C1..C7 <-> TSPE-SUITLIM-C1..C7),
  aucune capacite inventee, aucune omission (R1/R7 respectes).
- **Demonstrations exigibles** : 4 (C4, C5, C6, C7) — coherent entre referentiel,
  contrat et rapport.
- **BO reference** : "BO special n8 du 25 juillet 2019, Analyse/Suites" — coherent
  avec `sources/txt/BO2019_TSPE_specialite.txt` et le perimetre TSPE corrige
  (`docs/10_perimetre_terminale.md`, chapitre 1/11).
- **Prerequis** : R1-R5 pointent vers des chapitres 1SPE existants dans ce depot
  (1SPE-SUITES, 1SPE-EXPONENTIELLE, 1SPE-DERIVATION-GLOBAL) — coherent.
- **Point ouvert non bloquant pour LOT 0** : `LOT-2_rapport.md` (curation) est
  absent du dossier alors que LOT-1/3/4/5/6/7 sont presents et que `validations/`
  contient deja ~100 fichiers (exercices, QCM, evaluations A/B, remediation).
  A investiguer au moment de la reprise du LOT 1/2 (le contrat lui-meme n'est
  pas affecte par ce point).

**Statut LOT 0** : contrat conforme, propose pour validation humaine
(transition `statut: draft -> valide`). Non applique automatiquement (mode
strict LOT-par-LOT).
