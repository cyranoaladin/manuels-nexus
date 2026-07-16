# LOT 0 — Referentiel du chapitre 1NSI-TYPES-CONSTRUITS

## Contrat

- Fichier : `contrat.yaml`
- 5 capacites (C1-C5) avec libelles eleves
- Prerequis : R1-R4 (variables, boucles, fonctions, chaines)
- Situation d'accroche : classement tournoi e-sport

## Referentiel

- Source : `programme_nsi_2019.yaml` (corpus_nsi/00_programmes_officiels/)
- 114 capacites generees au total
- Capacite officielle associee : P-DATA-CONSTR-02A
- Libelles BO : p-uplets, types construits, tableaux, dictionnaires

## Verification R7

- Programme NSI : BO special n1 du 22 janvier 2019, arrete du 17 janvier 2019
- Verification en ligne non realisee (reseau non disponible) — consigne dans A_VALIDER_HUMAIN.md
- Aucune modification connue du programme NSI depuis 2019 a la date de connaissance (mai 2025)

## Validation adversariale

- Contrat conforme au schema `contrat_chapitre.schema.json` (test passe)
- 5 capacites couvrent le domaine "types construits" du BO : p-uplets (C1), tableaux (C2),
  grilles (C3), dictionnaires (C4), mutabilite (C5)
- Aucune capacite inventee : toutes correspondent a des items du programme officiel

## LOT R (recolte T0)

- Sequence P04 recoltee : 21 fichiers, 19 conversions pandoc, 0 echecs
- 5/5 capacites couvertes par des sources T0
- Verdict substance P-DATA-CONSTR-02A : needs_review (human_review_required)
- Tests Python : corrige passe les tests_attendus (3/3 tests OK)
- Rapport complet : `rapport_transposition.json`
