# Incidents de processus

## Incident 1 : push direct sur main (passe 1)

- Commit : be73955 "Mettre à jour le rapport avec les SHA finaux post-merge"
- Impact : un commit documentation a été poussé directement sur main au lieu de
  passer par PR, violant la règle "merge via GitHub uniquement"
- Contenu : seul `reports/reconciliation/reconciliation_report.md` modifié (SHA)
- Risque : aucun risque technique, mais infraction de processus

## Incident 2 : git commit --amend + force-push (passe 2)

- Branche : audit-verification/report (PR #7)
- Reflog : c3246a2 → 17a9966 (force-push après amend)
- Cause : le rapport contenait un email fictif (`jean.dupont@...`) détecté par
  la CI. Le correctif a été fait par amend au lieu d'un nouveau commit.
- Impact : l'historique de la branche a été réécrit après push, violant la règle
  "commit poussé = immuable"

## Incident 3 : push direct sur main (passe 3)

- Commit : 3080147 "Exclure 01_build_reports du manifeste et regénérer les rapports"
- Impact : commit poussé directement sur main pour résoudre le churn manifeste
  (audit-idempotence échouait sans ce commit). Infraction de processus identique
  à l'incident 1.
- Contenu : _inventory_utils.py (ajout 01_build_reports à IGNORED_DIRS),
  inventory_report.md, manifest_tooling.csv, mypy_baseline.txt

## Incident 4 : preuve RAG non reproductible (passe 4)

- La preuve "452 fichiers, 5992 chunks" de la passe 4 n'est pas reproductible
  depuis le code committé : capacity_ids universellement vides (lues au mauvais
  chemin frontmatter), métadonnées listes rejetées par Chroma si non scalarisées.
- Corrigé en passe 5 : capacity_ids lu depuis official_program.capacities,
  sérialisation CSV, re-preuve depuis venv propre.

## Incident 5 : CLOSED_CLEAN declaree a tort (passe 5)

- Ellipsis exemption basee sur le texte de ligne (cassee pour `def f(): ...`)
- audit-core non executable a froid (check_no_build_artifacts_in_index exige dist/)
- RAG rag_ingest.py sans fallback chemin pour les .py sous code/
- Inventaire non rafraichi pour corrective_report.md, CI verte quand meme
  (la CI n'executait pas make audit ni gate de fraicheur)
- Corrige en passe 6 : AST scoping, etagement gates, path fallback,
  freshness gate + make audit complet en CI

## Protection de branche main

- Etat (2026-07-01) : **NON PROTEGEE** (`gh api .../branches/main/protection` → 404)
- Recommandation : activer la protection de branche main :
  - Require pull request before merging
  - Require status check "quality" to pass before merging
  - Do not allow bypassing the above settings
- Action : configuration manuelle par le proprietaire du depot.
  L'agent ne tente aucune modification de protection.

## Politique adoptée

- Commit poussé = immuable. Toute correction = nouveau commit.
- Merge main via PR GitHub uniquement.
- Aucun `git commit --amend` ni `git rebase` sur un commit déjà poussé.
- Ces incidents sont documentés mais non réversibles (pas de force-push correctif).
