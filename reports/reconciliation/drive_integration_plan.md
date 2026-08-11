# Backlog Drive — Plan d'intégration

## Résumé

| Catégorie | Nombre | Statut |
|-----------|--------|--------|
| deferred | 3 | Planifiés pour lots ultérieurs |
| missing_local_copy | 7 | URL connue, fichier local absent |
| rejected_sensitive | 5 | Bloqués pour raison de confidentialité |
| **Total** | **15** | release-audit en échec attendu |

## Détail par item

### Deferred (3)

| Identifiant | Fichier | Raison | Action suivante | Bloquant |
|-------------|---------|--------|-----------------|----------|
| D-01 | Algo_Premiere/Cours.pdf | Contenu partiel, lot P12 tri/complexité | Intégrer lors du Lot 4 P12 | Non |
| D-02 | Algo_Premiere/2_TP.pdf | TP associé au cours, même lot | Intégrer avec D-01 | Non |
| D-03 | gestion_dossier_nsi/dossier.pdf | Document administratif | Évaluer pertinence Lot 4+ | Non |

### Missing local copy (7)

| Identifiant | Fichier | Raison | Action suivante | Bloquant |
|-------------|---------|--------|-----------------|----------|
| M-01 | reprise_nsi/Classeur-NSI.pdf | Fichier Drive non téléchargé | Télécharger et trier | Non |
| M-02 | reprise_nsi/Classeur-NSI.tex | Source LaTeX du PDF | Télécharger avec M-01 | Non |
| M-03 | reprise_nsi/Classeur-NSI.log | Log de compilation | Ignorer (artefact build) | Non |
| M-04 | eval_nsi_corrige.pdf | Corrigé évaluation | Télécharger et auditer PII | Non |
| M-05 | eval_nsi.pdf | Sujet évaluation | Télécharger et auditer PII | Non |
| M-06 | eval_nsi.tex | Source LaTeX évaluation | Télécharger avec M-05 | Non |
| M-07 | complement_algo.pdf | Complément algorithmique | Télécharger et trier | Non |

### Rejected sensitive (5)

| Identifiant | Fichier | Raison | Action suivante | Bloquant |
|-------------|---------|--------|-----------------|----------|
| R-01 | rendus_eleves/ | Dossier de rendus élèves | Interdit — données personnelles | Oui (si intégré) |
| R-02 | .git/ | Historique Git Drive | Interdit — hors périmètre | Non |
| R-03 | .venv/ | Environnement virtuel Drive | Interdit — artefact technique | Non |
| R-04 | NotesEleves.csv | Notes d'élèves | Interdit — données personnelles | Oui (si intégré) |
| R-05 | Fichier_Eleves.csv | Données élèves | Interdit — données personnelles | Oui (si intégré) |

## Décision

Le release-audit reste en échec attendu tant que les items M-01 à M-07 et D-01 à D-03
ne sont pas résolus. Les items R-01 à R-05 ne seront JAMAIS intégrés.
