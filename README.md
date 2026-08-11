# NSI-enseignement

## 1) Philosophie pédagogique

Corpus pédagogique versionné pour la spécialité NSI (Première/Terminale), structuré par séquences annuelles et reposant sur :

- conformité officielle BO 2019 (1re/Terminale),
- séparation claire des rôles (élèves/professeur/corrigé),
- répétabilité (scripts de compilation, tests et contrôles),
- production d’artefacts exploitables sans mélange de données privées.

## 2) Organisation du dépôt

- `00_programmes_officiels/` : sources institutionnelles et références du programme.
- `01_charte_graphique_et_pedagogique/` : charte visuelle + schéma de métadonnées.
- `02_modeles_documents/` : modèles réutilisables (cours, TD, TP, évaluation, corrigé, guide prof, qcm, séquence).
- `03_progressions/supports/` : canon de production du corpus.
- `premiere/`, `terminale/` : pilotes et références de style, pas cible des nouvelles productions.
- `scripts/` : scripts de build, contrôle qualité, tests.

## 2.1) Sources locales Drive

Les ressources Drive déjà extraites doivent être consultées hors dépôt dans le miroir local
`Documents_DRIVE` placé à côté du dépôt, ou dans le dossier indiqué par
`NSI_DOCUMENTS_DRIVE_ROOT`. Les passes d’inventaire et de rédaction doivent chercher
d’abord dans ce dossier local, puis noter le chemin consulté dans les métadonnées ou les
registres. Cette source locale ne change pas les statuts : une ressource adaptée depuis
`Documents_DRIVE` reste `needs_review` tant qu’elle n’a pas été auditée.

## 3) Progressions annuelles

- Première : `03_progressions/progression_premiere.md`
- Terminale : `03_progressions/progression_terminale.md`

## 4) Compilation / production des livrables

Depuis la racine du dépôt :

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ruff check .
pytest
```

1. Vérifier l’arborescence.
2. Mettre à jour le `manifest.csv` si de nouvelles ressources sont ajoutées.
3. Lancer :

```bash
python -m scripts.build_all
python -m scripts.check_metadata
python -m scripts.check_links
python -m scripts.check_program_coverage
python -m scripts.generate_index
```

4. Vérifier les sorties :
- `01_build_reports/build_index.md`
- `01_build_reports/build_report.md`
- `coverage.md`
- `INDEX.md`

## 5) Ajouter une séquence

1. Créer ou modifier les supports dans `03_progressions/supports/`.
   Les dossiers `premiere/sequences/` et `terminale/sequences/` restent des pilotes de style.
2. Créer les fichiers obligatoires :
   - `cours_eleve.md`
   - `trace_ecrite.md`
   - `td.md`
   - `tp.md`
   - `fiche_methode.md`
   - `aides_progressives.md`
   - `corrige.md`
   - `guide_professeur.md`
   - `evaluation.md`
   - `qcm.json`
   - `projet_associe.md`
   - dossier `python/` avec au moins un module
   - dossier `tests/` avec tests unitaires
3. Ajouter les répertoires miroir dans `banques/` (facultatif selon stratégie locale).
4. Ajouter une ligne dans `manifest.csv`.

## 6) Produire versions élève/professeur/corrigé

- `cours_eleve.md` = version élève.
- `guide_professeur.md` = version enseignant.
- `corrige.md` = corrigé.

Les documents QCM/corrigé/tests restent dans les fichiers dédiés.

## 7) Vérifier la conformité programme

- Exécuter `check_program_coverage.py` (associant `manifest.csv` et `00_programmes_officiels/programme_nsi_2019.yaml`).
- Compléter les rubriques `sequence_possible`, `notion`, `source`, `objectifs`.

## 8) Publier les ressources

- Ne publier que les ressources:
  - sans données personnelles,
  - avec métadonnées complètes,
  - ayant des tests exécutables,
  - présentes dans l’inventaire et la couverture.

## 9) Commandes de vérification complètes

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ruff check .
pytest
make audit
```

Le dépôt est orienté vers une revue continue : chaque ajout doit être répercuté dans `manifest.csv`, `coverage.md` et `inventory_report.md`.

## 10) Substance et statuts

Le pipeline de substance est conservateur :

- `scripts/run_substance_judge.py` et `scripts/check_substance_anchors.py` produisent et vérifient les verdicts au format `substance_verdict.schema.json`.
- `scripts/substance_judge.py` peut proposer des preuves depuis le RAG/LLM, mais ne constitue pas une validation humaine.
- `covered`, `validated_*` et `published` restent à `0` tant qu’une revue humaine pédagogique et scientifique n’est pas tracée.

Le smoke RAG est optionnel et séparé des tests pytest :

```bash
python -m scripts.rag_smoke_test
```
