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

## 5. Gates corpus transposes (Addendum C.6)

| Script source | Gate manuel | Statut |
|---|---|---|
| check_eleve_no_corrige.py | gates_corpus/check_eleve_no_corrige.py | adapte — patterns affines pour LaTeX |
| check_td_corrige_alignment.py | gates_corpus/check_td_corrige_alignment.py | adapte — compare exercices/*.tex vs corriges/*.tex |
| check_no_placeholders.py | gates_corpus/check_no_placeholders.py | adapte — scan production (excl docs/prompts) |
| check_differentiation_quality.py | gates_corpus/check_differentiation_quality.py | adapte — ratio parcours 40/40/20 |
| check_qcm_schema.py | gates_corpus/check_qcm_schema.py | adapte — compte questions, verifie couverture capacites |
| check_sql_query_result_consistency.py | gates_corpus/check_sql_query_result_consistency.py | differe (Terminale BDD-SQL) |
| check_boyer_moore_trace_consistency.py | gates_corpus/check_boyer_moore_trace_consistency.py | differe (Terminale PROG-DYNAMIQUE-TEXTE) |
| check_no_teacher_content_in_student_export.py | (integre dans check_eleve_no_corrige) | adapte |

Cible Makefile : `make gates-corpus CHAP=...`

## 6. Verification R7 hors ligne (Addendum Point 2)

- 94 contenus du referentiel confrontes aux textes officiels par mots-cles
- 1 ecart significatif (paraphrase YAML, pas erreur de programme)
- Consigne dans referentiel/_a_verifier.json
- Verification web du BO reste due quand le reseau repond

## 7. Scrapers corpus (Addendum Point 3)

- Scrapers identifies : scraper_eduscol.py, scraper_nsi_v2.py + netpolicy/provenance
- Import direct impossible (couplage fort avec le depot source)
- Repli documente sur scripts/crawl.py (generique)
- Reference : docs/10_scrapers_corpus.md

## 8. MCP-corpus RAG (Addendum Point 4)

- RAG corpus joignable (rag-api.nexusreussite.academy repond 405 GET)
- Cle API absente : mode RAG distant non configurable
- PostgreSQL/pgvector non installe : mode DB locale non disponible
- **Mode retenu : MODE FICHIERS** (recherche directe dans corpus_nsi/ via scripts)
- Le RAG reste configurable via .env si la cle devient disponible
