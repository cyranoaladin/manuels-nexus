# Lot 1 - Phase 0 - Cartographie du dépôt

Date: 2026-06-28
Base ratifiée: `05fa3c8e4dae5b92ec4dc8ca106290ec26887960`
Branche de travail: `lot1/substance-gouvernance`

## Ratification de la base

`HEAD` et `origin/main` coïncident sur `05fa3c8e4dae5b92ec4dc8ca106290ec26887960`.

Le run GitHub Actions associé (`28334022625`) est terminé avec `conclusion=success`.

Le commit `05fa3c8` est signé par l'humain:

- auteur: `humain mainteneur`
- co-auteur: `agent de génération`
- message: `Ajuster la config après restructuration du dépôt distant`

Le diff de `05fa3c8` est confiné à `scrapping_NSI/.coveragerc` et
`scrapping_NSI/ruff.toml`, hors périmètre du lot corpus/QA. Aucun fichier
d'autorité, aucun fichier pédagogique, aucun fichier doctrinal et aucun contrat
du juge de substance n'est modifié par ce commit.

Le commit intermédiaire `de66350` est également signé par l'humain et confiné à
`scrapping_NSI/`. Il ne touche aucun fichier d'autorité ni pédagogique du lot.

## Carte des fichiers d'autorité

| Élément | Chemin réel actuel | État | Note |
|---|---|---|---|
| Vérificateur d'ancres System A | `scripts/check_substance_anchors.py` | présent | Autorité mécanique existante. |
| Proposeur System B | `scripts/substance_judge.py` | présent | À réconcilier en Phase 3. |
| Schéma verdict substance | `substance_verdict.schema.json` | présent | Format cible de System A. |
| Gates qualité | `scripts/check_quality_gates.py` | présent | Point d'intégration futur des gardes. |
| CI GitHub Actions | `.github/workflows/ci.yml` | présent | Workflow principal. |
| Makefile | `Makefile` | présent | Aucune cible `judge` n'est actuellement définie. |
| Politique des gates | `qa_gate_policy.md` | présent | À enrichir en Phase 2B. |
| Politique d'arbre canonique | `content_tree_policy.md` | présent | Inchangée par la restructuration. |
| Index des revues substance | `substance_reviews_index.md` | présent | Doit rester doctrinalement vrai. |
| Verdict adverse | `substance_reviews/_adversarial/poisoned.verdict.json` | présent | Garde adverse existant. |

## Fichiers de statut / rapports suivis

| Élément | Chemin réel actuel | État |
|---|---|---|
| Couverture programme | `coverage.md` | présent |
| Index général | `INDEX.md` | présent |
| Manifest | `manifest.csv` | présent |
| Rapports `substance_report*.md` | aucun fichier suivi hors historique reverté | absent dans l'arbre courant |
| Revues `substance_review*.json` | aucun fichier suivi hors verdict adverse | absent dans l'arbre courant |

## Arborescence pédagogique

La comparaison `180fb69..05fa3c8` ne montre aucune modification dans:

- `03_progressions/`
- `premiere/`
- `terminale/`
- `02_modeles_documents/`

La restructuration distante observée concerne `scrapping_NSI/`, explicitement hors
périmètre de ce lot.

## Preuve de contenu de `05fa3c8`

- `scrapping_NSI/.coveragerc`: retrait d'une entrée liée à `organizer_nsi`,
  sans signature publique, sans format de sortie, sans fonction System A/B.
- `scrapping_NSI/ruff.toml`: retrait d'une entrée liée à `organizer_nsi`,
  sans signature publique, sans format de sortie, sans fonction System A/B.

Conclusion Phase 0: base ratifiée exploitable pour la suite, sous réserve de la
forensique Drive de Phase 1A.
