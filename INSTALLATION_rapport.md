# Rapport d'installation — Connexion corpus + Adaptation pipeline

Date : 2026-07-15

## 1. Connexion au corpus (Phase A)

- **Lien symbolique** : `corpus_nsi -> ~/Documents/NSI-recovery-t10-p08-t17`
- **Variable d'environnement** : `NSI_CORPUS_ROOT` dans `.env` et `.env.example`
- **Scripts patches** : `common.py` (ajout `CORPUS_NSI`), `harvest_nsi.py`, `convert_programme_yaml.py` utilisent `CORPUS_NSI` au lieu de chemins en dur
- **Gitignore** : `corpus_nsi` ajoute (lien, pas contenu a versionner)
- **Lecture seule** : test `tests/test_corpus_readonly.py` passe — aucun script n'ecrit dans le corpus
- **Point de restauration** : commit `[INIT] noyau` avant toute modification

## 2. Synchronisation de la charte (Phase B)

- 4 fichiers tronc commun copies depuis `Mathematiques/manuel-maths/gabarits/` : nexus-manuel.cls, nexus-icons.tex, nexus-figures.tex, nexus-signatures.tex
- 2 docs copies : 06_charte_graphique.md, 07_ligne_editoriale.md
- `nexus-manuel.cls` : chargement des extensions via `\InputIfFileExists` (NSI-specifiques : nexus-code.tex, nexus-figures-nsi.tex)
- `nexus-figures-nsi.tex` : suppression des doublons (nxfig/nxfigure) deja definis dans le tronc commun
- `SYNC_CHARTE.md` cree a la racine de Manuels_Nexus/
- **Gate compilation** : PDF genere sans erreur, accents corrects

## 3. Adaptation du pipeline (Phase C)

### 3.1 Structure reelle du corpus constatee
- 15 sequences Premiere (P00-P14), 20 Terminale (T00-T19)
- 35 contrats dans `contracts/*.yml` avec capacites officielles
- Fichiers nommes `{ID}_{type}_{slug}.md` avec types : cours, trace, td, tp, corrige, evaluation, bareme, remediation, version_amenagee
- Code executable dans `code/` : starter, corrige_professeur, tests_attendus
- Fiches de cours dans `fiches_cours/{niveau}/{ID}/`
- 115 verdicts de substance dans `substance_reviews/campaign/`
- 2 sequences canon (s01) avec structure differente

### 3.2 Reecriture de harvest_nsi.py
- Decouverte par contrats (prioritaire) + scoring lexical en repli
- Matching par mapping explicite (docs/09) > capacites officielles > mots-cles
- Parsing insensible a la casse avec types connus (KNOWN_TYPES)
- Copie avec renommage clair : cours.md, cours_complement.md, etc.
- Recolte enrichie : fiches cours, contrat YAML, verdicts de substance, revue humaine
- Rapport de transposition avec tracabilite complete

### 3.3 Nouvelles exigences
- **F11** ajoute au CDC : declinaison version amenagee par chapitre
- Variante `amenagee` ajoutee a `assemble.py`
- Check-list LOT 7 enrichie

### 3.4 Mapping sequences <-> chapitres
- `docs/09_mapping_sequences_chapitres.md` : 10 chapitres Premiere, 12 Terminale
- Construit depuis les contrats reels + decisions documentees

## 4. Smoke tests (Phase D)

| Test | Resultat |
|---|---|
| `make referentiel` | 114 capacites generees, 0 non resolus |
| `make harvest CHAP=1NSI-TYPES-CONSTRUITS` | P04 recolte : 21 fichiers, 19 conversions pandoc, 0 echecs, 5/5 capacites couvertes |
| Tests Python P04 (corrige vs tests_attendus) | OK — import blocs VERIFY viable |
| Verdict substance P-DATA-CONSTR-02A | needs_review (human_review_required) — propage correctement |
| `make accents` | OK |
| `make test` | 8 passed |
| Compilation standalone (classe + exercice pilote) | PDF genere sans erreur |
