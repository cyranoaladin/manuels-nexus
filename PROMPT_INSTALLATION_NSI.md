# PROMPT INSTALLATION — Mise en place de l'arborescence Manuels_Nexus et connexion au corpus NSI

Tu es Claude Code. Tu travailles dans `~/Documents/Manuels_Nexus/`. Ce dossier contient :
- `Mathematiques/manuel-maths/` : projet du manuel de maths, 3 chapitres produits, **charte Nexus v2 aboutie** (nexus-manuel.cls, nexus-icons.tex, nexus-figures.tex, nexus-signatures.tex, docs/06 et 07) — c'est le TRONC COMMUN de la collection.
- `NSI/` : noyau du projet manuels NSI (CLAUDE.md, CDC, scripts, prompts, pilote 1NSI-TYPES-CONSTRUITS amorcé).

Le corpus source NSI (tier T0) vit dans un dossier FRÈRE de Manuels_Nexus :
`~/Documents/NSI-recovery-t10-p08-t17/` — dépôt propriétaire certifié (contrats de séquences, supports P00–P14 et T00–T19, code testé, revues de substance).

Ta mission dans CE prompt : **installer l'arborescence définitive, connecter le corpus, adapter le pipeline à la structure RÉELLE du corpus, valider l'installation par des smoke tests, puis enchaîner sur la mission de production** (`NSI/PROMPT_MISSION_AUTONOME.md`). Régime : celui de `NSI/CLAUDE.md` §0 — aucun arrêt, aucun « dois-je continuer ? », rapport + commit + tâche suivante. Coche chaque phase dans `NSI/DIRECTIVES_EN_COURS.md` (ajoute-y la check-list INSTALLATION ci-dessous en tête).

---

## PHASE A — CONNEXION AU CORPUS (le point le plus important)

Le noyau NSI supposait un submodule GitHub. La réalité est un dossier local frère. Mets en place la connexion ainsi :

1. Dans `NSI/` : `git init` si nécessaire, commit `[INIT] noyau` de l'état actuel AVANT toute modification (point de restauration).
2. Remplace le contenu de `NSI/corpus_nsi/` par un **lien symbolique** :
   ```bash
   cd ~/Documents/Manuels_Nexus/NSI
   rm -rf corpus_nsi
   ln -s ~/Documents/NSI-recovery-t10-p08-t17 corpus_nsi
   ```
3. Robustesse : ajoute dans `.env.example` et `.env` la variable `NSI_CORPUS_ROOT=~/Documents/NSI-recovery-t10-p08-t17`, et patche `scripts/common.py` pour définir `CORPUS_NSI = Path(os.getenv("NSI_CORPUS_ROOT", ROOT / "corpus_nsi")).expanduser()` — tous les scripts (harvest, convert_programme_yaml, similarity) utilisent `CORPUS_NSI`, jamais un chemin en dur.
4. Ajoute `corpus_nsi` à `.gitignore` (c'est un lien, pas du contenu à versionner).
5. **Discipline lecture seule absolue** : aucun script, aucune commande n'écrit à travers ce lien. Vérifie que `harvest_nsi.py` copie TOUJOURS vers `chapitres/*/_harvest/` et jamais l'inverse. Ajoute un test `tests/test_corpus_readonly.py` qui vérifie qu'aucun script du dépôt n'ouvre un chemin sous `CORPUS_NSI` en écriture (analyse statique simple : grep de `open(` / `write_text` / `shutil.copy` avec destination sous corpus).

## PHASE B — SYNCHRONISATION DE LA CHARTE (tronc commun depuis les maths)

La charte du manuel maths est plus avancée que celle copiée dans NSI (v2 : accents corrigés, icônes TikZ, signatures de chapitres, figures). Synchronise :

1. Copie depuis `../Mathematiques/manuel-maths/gabarits/` vers `NSI/gabarits/` : `nexus-manuel.cls`, `nexus-icons.tex`, `nexus-figures.tex`, `nexus-signatures.tex` (ÉCRASE les versions NSI de ces fichiers — le tronc commun fait foi). Conserve intacts les fichiers d'extension NSI : `nexus-code.tex`, `nexus-figures-nsi.tex`.
2. Vérifie que la fin de `nexus-manuel.cls` charge bien les extensions via `\InputIfFileExists` pour : nexus-icons, nexus-figures, nexus-signatures, nexus-code, nexus-figures-nsi (ajoute les lignes manquantes ; l'absence d'un fichier ne doit pas casser la compilation côté maths).
3. Copie `docs/06_charte_graphique.md` et `docs/07_ligne_editoriale.md` depuis le projet maths vers `NSI/docs/`.
4. Crée `SYNC_CHARTE.md` à la racine de `Manuels_Nexus/` : procédure de synchronisation (source de vérité = manuel-maths ; commande rsync des 4 fichiers du tronc + les 2 docs ; règle : toute évolution de charte se fait côté maths puis se propage, les extensions NSI ne touchent jamais au tronc).
5. Gate : compile un objet de test avec la classe synchronisée (`objet_standalone.tex` sur l'exercice pilote 1NSI-TC-EX-001) — la compilation doit passer, accents inclus (`make accents`).

## PHASE C — ADAPTATION DU PIPELINE À LA STRUCTURE RÉELLE DU CORPUS

C'est le chantier central de l'installation : `harvest_nsi.py` a été écrit pour le canon théorique (`cours_eleve.md`, `td.md`...) du README, mais la structure réelle est différente. Commence par un inventaire réel (`ls`, lecture d'échantillons), puis adapte.

### C.1 — Structure réelle constatée (à vérifier et compléter par ton inventaire)

- **Supports par séquence** : `corpus_nsi/03_progressions/supports/premiere/P00..P14/` et `terminale/T00..T19/`, fichiers nommés `{ID}_{type}_{slug}.md` avec `type ∈ {cours, td, tp, trace, corrige, corrige_professeur (dans code/), evaluation, bareme, remediation, version_amenagee}`. Certaines séquences ont plusieurs sous-thèmes (ex. P02, P03, P08 : deux slugs) et des doublons de casse (`P07_tp_*` ET `P07_TP_*`) : dédoublonne par (ID, type, slug) insensible à la casse, en préférant le fichier le plus récent/le plus long.
- **Code exécutable** : `{PXX}/code/` avec `{ID}_starter_{slug}.py` (squelette élève), `{ID}_corrige_professeur_{slug}.py` (référence), `{ID}_tests_attendus_{slug}.py` (jeux de tests) — l'actif le plus précieux pour les blocs VERIFY et les sujets ECE.
- **Contrats de séquences** : `03_progressions/supports/contracts/{ID}_contract.yml` — capacités visées par séquence, avec les identifiants de substance (type `P-DATA-CONSTR-01`).
- **Fiches de cours** : `03_progressions/fiches_cours/{niveau}/{ID}/*.md` — synthèses par notion (alimentent la strate 1/2).
- **Certification** : `substance_reviews/campaign/{CAPA-ID}_substance_review.json` — verdict par capacité ; `human_review_register.csv` — statuts de revue humaine.
- **Programme** : `00_programmes_officiels/programme_nsi_2019.yaml` (+ PDF/txt officiels).
- **Séquences pilotes canon 11 fichiers** : `premiere/sequences/s01_*` et `terminale/sequences/s01_*` (avec `aides_progressives.md`, `qcm.json`, `projet_associe.md`, `guide_professeur.md`) — seules ces deux-là suivent le canon du README ; les traiter comme sources supplémentaires.
- **LaTeX existant** : `latex/packs/premiere/P13/` + `02_modeles_documents/*.tex` + `nsi-preamble.sty` — RÉFÉRENCE de conversion Markdown→LaTeX réussie, mais la charte Nexus fait foi pour la forme finale.

### C.2 — Réécriture de `scripts/harvest_nsi.py`

1. La découverte des séquences se fait par `contracts/*.yml` (source structurée), plus les deux séquences canon. Le matching capacité↔séquence utilise les contrats (identifiants de substance) EN PRIORITÉ, le scoring lexical en repli.
2. La récolte copie vers `_harvest/{ID}/` : tous les `.md` de la séquence (renommés en clair : `cours.md`, `td.md`, `remediation.md`, `version_amenagee.md`, `evaluation.md`, `bareme.md`, `trace.md`, `tp.md`, `corrige.md`), le dossier `code/` tel quel, la fiche de cours correspondante depuis `fiches_cours/`, le contrat YAML, et le verdict de substance + la ligne du `human_review_register.csv` (héritage F08).
3. Conversion pandoc + `md2nexus.lua` inchangée (`.candidate.tex`).
4. Rapport de transposition enrichi : pour chaque capacité du chapitre → séquences sources, fichiers récoltés, verdict de substance, statut de revue humaine, angle mort éventuel.

### C.3 — Mise à jour de la table de transposition (`docs/08` §3.2) selon la réalité

| Source réelle | Objet manuel |
|---|---|
| `{ID}_cours_*.md` + `{ID}_trace_*.md` + `fiches_cours/{ID}/*` | Cours strates 1–2 (trace = essentiel, cours = développement) |
| `{ID}_td_*.md` | Exercices ◆◆ (découpage atomique) |
| `{ID}_tp_*.md` | Exercices ⌨ ◆/◆◆ + matière du Mini-projet |
| `{ID}_remediation_*.md` | Remédiation (mapping direct) |
| `{ID}_evaluation_*.md` + `{ID}_bareme_*.md` | Évaluation A + barème par compétences |
| `{ID}_version_amenagee_*.md` | **NOUVELLE déclinaison « version aménagée »** (voir C.4) |
| `code/{ID}_tests_attendus_*.py` | Blocs VERIFY (import direct des asserts) |
| `code/{ID}_corrige_professeur_*.py` | `\codereference` du cours + corrigés |
| `code/{ID}_starter_*.py` | Squelettes des sujets ECE (exercice 2 : code à compléter) |
| `{ID}_contract.yml` + substance_review + human_review_register | Métadonnées, traçabilité, statuts hérités |
| séquences canon s01 (`aides_progressives.md`, `qcm.json`, `projet_associe.md`, `guide_professeur.md`) | Coups de pouce / QCM / Mini-projet / livret professeur |

### C.4 — Nouvelle exigence issue du corpus : la déclinaison « version aménagée »

Le corpus contient des `version_amenagee` systématiques (élèves à besoins particuliers). Intègre-le au produit : ajoute `F11` au CDC (« déclinaison version aménagée par chapitre : énoncés allégés, consignes séquencées, mise en page aérée, générée depuis les mêmes objets avec les sources `version_amenagee` transposées »), une variante `amenagee` dans `assemble.py`, et la ligne correspondante dans la check-list du LOT 7.

### C.5 — Mapping séquences ↔ chapitres du manuel

Écris `docs/09_mapping_sequences_chapitres.md` : table faisant autorité, construite depuis les contrats et les progressions (`03_progressions/progression_*.md`). Point de départ à vérifier contre les contenus réels :
- Première : TYPES-BASE ← P01+P02+P03 ; TYPES-CONSTRUITS ← P04 ; TABLES ← P05+P06 ; LANGAGE ← P00+P07 ; WEB-IHM ← P08 ; ARCHITECTURE-OS ← P09 ; RESEAUX ← P10 ; ALGO-PARCOURS-TRIS ← P11+P12 ; ALGO-DICHO-GLOUTON-KNN ← P13 ; PROJET-METHODES ← P14.
- Terminale : STRUCTURES-LINEAIRES ← T01+T03 ; POO ← T02 (+T14 modularité) ; RECURSIVITE ← T04 ; ARBRES ← T05+T06 ; GRAPHES ← T07+T08 ; BDD-SQL ← T09+T10 ; PROCESSUS-SOC ← T11 ; RESEAUX-SECURITE ← T12+T13 ; CALCULABILITE-PARADIGMES ← T15 (+T14 pour paradigmes) ; DIVISER-REGNER ← T16 ; PROG-DYNAMIQUE-TEXTE ← T17+T18 ; PREPA-ECE/ECRIT/GRAND-ORAL ← T19 + T00 (diagnostic → bilan d'entrée annuel du manuel).
Ajuste ce mapping d'après ta lecture réelle des contrats ; toute décision divergente est documentée dans le fichier.

## PHASE D — SMOKE TESTS DE L'INSTALLATION (gates bloquants)

1. `make referentiel` : le YAML programme se convertit ; les items non résolus partent dans `_a_verifier.json` sans invention.
2. `make harvest CHAP=1NSI-TYPES-CONSTRUITS` : le rapport de transposition doit montrer P04 récolté (cours, complement, td, tp, code/, remediation, version_amenagee, contrat, verdict de substance) et **≥ 4 des 5 capacités C1–C5 couvertes par des sources T0**. Sinon : corrige le matching avant de continuer.
3. Exécute réellement `code/P04_tests_attendus_types_construits.py` contre `code/P04_corrige_professeur_types_construits.py` en sandbox : doit passer (preuve que l'import des tests comme blocs VERIFY est viable). Consigne le résultat.
4. `make verify CHAP=1NSI-TYPES-CONSTRUITS` (pilote existant), `make accents`, `make test`, compilation standalone de l'exercice pilote : tout vert.
5. Rapport `INSTALLATION_rapport.md` à la racine de `NSI/` : connexion, synchronisation charte, adaptations du pipeline, résultats des smoke tests, mapping. Commit `[INSTALL] connexion corpus + adaptation pipeline structure réelle`.

## PHASE E — ENCHAÎNEMENT SUR LA MISSION

Sans t'arrêter, ouvre `NSI/PROMPT_MISSION_AUTONOME.md` et exécute-le depuis la PHASE 0 (en sautant ce qui vient d'être fait), en intégrant les amendements décidés ici : LOT R basé sur les contrats réels, déclinaison aménagée (F11), mapping docs/09. Premier objectif : le chapitre pilote `1NSI-TYPES-CONSTRUITS` complet (LOT 0 → 7), qui aboutit à l'arrêt planifié unique de validation humaine (`PILOTE_A_VALIDER.md` + PDF, incluant un extrait de la version aménagée pour jugement).

Rappels non négociables : corpus en lecture seule ; toute sortie de programme vérifiée par exécution (R2) ; les statuts `needs_review` du registre de revue humaine se propagent (F08) ; commits exacts (R8) ; accents (R10) ; densité et coups de pouce séparés (DIRECTIVES_EN_COURS).

COMMENCE MAINTENANT : Phase A, étape 1.
