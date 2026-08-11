# Rapport de réorganisation — anomalies préexistantes

Date : 2026-07-10. Branche : `chore/reorg-latex-kit`.

## 1. nsi-enseignement/ (copie imbriquée du dépôt)

| Métrique | Valeur |
|----------|--------|
| Fichiers | 5 810 |
| Taille | 159 Mo |
| `.git` propre | Oui (même remote `cyranoaladin/NSI`) |
| Tracké par le dépôt parent | Non (0 fichiers dans `git ls-files`) |
| HEAD | `eb602f5` (branche `remediation/p13-coherence`) |

**Diagnostic** : clone complet imbriqué du même dépôt, sur une branche de travail différente
(`remediation/p13-coherence` vs `main`/`chore/reorg-latex-kit` pour le parent). Ce n'est ni un
submodule ni un worktree git — c'est un dossier git indépendant. Le contenu est un doublon
quasi-total de la racine ; seules les branches diffèrent.

**Vérification commits non poussés** (2026-07-10) :
```
$ git -C nsi-enseignement log --oneline --branches --not --remotes
(aucun résultat — toutes les branches locales sont poussées sur origin)
```

8 branches locales, toutes trackent leur remote et sont à jour :
`main`, `remediation/p13-coherence`, `remediation/pr-a2-scope`, `remediation/pr-a3-variants`,
`remediation/pr-a4-symmetry`, `remediation/pr-a5-enum`, `remediation/pr-b-purge`,
`substance/9-partial-to-needs-review`.

Contient aussi un `.venv/` de 117 Mo (3 255 fichiers) inutile.

**Action effectuée (2026-07-10)** : `nsi-enseignement/` supprimé (`rm -rf`).
Aucun commit local non poussé (vérifié), doublon complet, jamais tracké par le dépôt parent.

---

## 2. scrapping_NSI/ (~22 000 fichiers, 15 Go)

| Métrique | Valeur |
|----------|--------|
| Fichiers | 22 983 |
| Taille | 15 Go |
| Trackés par git | 14 fichiers (scripts + config) |

**Diagnostic** : corpus de ressources NSI extraites du web. Seuls 14 fichiers de scripts/config
sont trackés par git. Les ~23 000 ressources (PDF, DOC, HTML, ZIP) ne le sont pas.

**Proposition** : sortir `scrapping_NSI/` du dépôt git (ajouter à `.gitignore`). Les 14 fichiers
trackés peuvent rester, ou être migrés dans un dépôt/dossier dédié. Les 15 Go de données brutes
ne doivent pas être committés.

---

## 3. Documents_DRIVE/

| Métrique | Valeur |
|----------|--------|
| Existence | **Absent** (aucun fichier ou dossier de ce nom trouvé) |

**Diagnostic** : le dossier n'existe pas sur cette machine. Soit il a été supprimé, soit il
n'a jamais été cloné localement. Aucune action requise pour l'instant.

---

## 4. premiere/ et terminale/ (racine)

| Métrique | premiere/ | terminale/ |
|----------|-----------|------------|
| Fichiers .md | 26 | 25 |
| Trackés par git | Oui (59 fichiers total) |

**Diagnostic** : ce ne sont PAS des doublons de `03_progressions/`. Ce sont des structures
distinctes :
- `premiere/banques/` et `terminale/banques/` : index de banques (évaluations, exercices, projets, QCM, sujets pratiques, TP)
- `premiere/sequences/s01_representation_donnees/` : séquence pilote (cours_eleve, corrige, tp, trace, revue)

Ces fichiers sont trackés par git et ont un rôle différent de `03_progressions/supports/`.
`03_progressions/` contient les supports par séquence (P00-P14, T00-T19).
`premiere/`/`terminale/` contiennent les banques transversales et une séquence pilote rendue.

**Proposition** : conserver en l'état. Pas de doublon détecté.

---

## 5. Rapports racine (~54 fichiers .md/.csv)

| Métrique | Valeur |
|----------|--------|
| Fichiers .md à la racine | 50 |
| Fichiers .csv à la racine | 4 |
| Total | 54 |

**Classification** :

| Catégorie | Fichiers | Proposition |
|-----------|----------|-------------|
| Gouvernance projet | AGENTS.md, SKILLS.md, README.md, INDEX.md | Conserver racine |
| Politique QA | qa_gate_policy.md, qa_report.md, quality_checklist.md, delivery_policy.md, content_tree_policy.md | Conserver racine (référencés par scripts) |
| Pipeline substance | substance_pipeline.md, substance_reviews_index.md | Conserver racine |
| Manifests/inventaire | manifest.csv, inventory_report.md, duplicates_report.md | Conserver racine (générés par scripts) |
| Couverture programme | coverage.md, coverage_sources.md, missing_capabilities.md, programme_matrix_*.md | Grouper sous `reports/` |
| Rapports d'audit | *_report.md, *_audit.md (25+ fichiers) | Grouper sous `reports/` |
| Planification | project_plan_*.md, calendar_*.md, carnet_de_bord.md | Grouper sous `reports/` |
| Revue humaine | human_review_*.md, human_review_*.csv | Grouper sous `reports/` |
| Drive | drive_*.md, drive_*.csv, drive_*.yml | Grouper sous `reports/` ou `drive_quarantine/` |
| Hors-scope | Cahier des charges*.md/pdf, audit_03_07_26.md, METHODE_PRODUCTION_REELLE.md | Conserver racine ou docs/ |

**Proposition** : regrouper les ~30 rapports d'audit/couverture/planification sous `reports/`
(le dossier existe déjà). Conserver en racine les fichiers référencés par les scripts
(`manifest.csv`, `qa_gate_policy.md`, etc.) et les fichiers de gouvernance.

⚠️ **Attention** : de nombreux fichiers racine sont référencés par des scripts Python
(`check_*`, `generate_*`). Tout déplacement nécessite une mise à jour coordonnée des imports.
Ne pas déplacer sans audit préalable des dépendances.

---

## Résumé des actions proposées

| Item | Action | Risque | Requiert confirmation |
|------|--------|--------|----------------------|
| nsi-enseignement/ | Supprimer (doublon complet) | Perte de branches locales non poussées | **OUI** |
| scrapping_NSI/ | Ajouter à .gitignore | Aucun (déjà non tracké) | **OUI** |
| Documents_DRIVE/ | Aucune (absent) | — | Non |
| premiere/ + terminale/ | Conserver (pas un doublon) | — | Non |
| Rapports racine | Regrouper sous reports/ | Casse de scripts | **OUI** (audit dépendances requis) |
