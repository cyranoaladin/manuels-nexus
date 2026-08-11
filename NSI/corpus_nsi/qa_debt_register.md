# Registre de dette QA

## Dettes indicatives encore ouvertes

| Fichier concerné | Gate concerné | Cause | Risque | Impact | Décision | Date cible | Responsable | Critère de fermeture |
|---|---|---|---|---|---|---|---|---|
| Doublon P08 (P08_TP_html_css_dom.md / P08_TP_http_get_post_formulaires.md) | duplicates_report.md | Deux TP couvrant le même thème classés "doublon non classé" | Confusion pédagogique, couverture imprécise | Revue humaine requise pour trancher (fusion, spécialisation ou retrait) | Item de CONTENU, hors scope tooling. Ne pas modifier sans revue pédagogique. | Lot 4+ | équipe NSI | Un seul TP par thème ou justification explicite de la coexistence |
| Provenance par signature de contenu (hash pipeline au save) | check_verdict_provenance | La garde monotone compare judged_at (timestamp) — elle ne prouve pas que le contenu vient du pipeline, seulement que le timestamp a avancé. Un hash du contenu généré par le pipeline permettrait une vérification cryptographique. | Édition manuelle indétectable si judged_at est rafraîchi artificiellement. | Déclencheur : 4e occurrence d'édition manuelle ou passe outillage post-flip. | Ajouter un champ `pipeline_content_hash` (SHA-256 du verdict sérialisé) dans le JSON, vérifié par la garde provenance. | Lot 5+ | équipe NSI | check_verdict_provenance vérifie le hash en plus du timestamp ; un verdict avec hash absent ou incorrect est rejeté. |

## Dettes fermées

| Fichier concerné | Gate concerné | Cause initiale | Action réalisée | Date de fermeture | Critère vérifié |
|---|---|---|---|---|---|
| Protection branche main | CI | main non protégée (push direct possible) | Protection activée : require PR + status check "quality" + enforce_admins | 2026-07-01 | (A) `gh api repos/cyranoaladin/NSI/branches/main/protection --jq '(.required_pull_request_reviews != null) and ((.required_status_checks.contexts // []) \| index("quality") != null)'` = `true` ET (B) `gh api repos/cyranoaladin/NSI/branches/main/protection/enforce_admins --jq '.enabled'` = `true`. Les DEUX doivent etre true. |
| `premiere/sequences/s01_representation_donnees/cours_eleve.md` | `scripts/check_required_sections.py` | Titres attendus absents : activité d'introduction, exemples corrigés, exercices intégrés, extension, aides progressives. | Sections ajoutées et adaptées depuis la ressource Drive `1_RdD_Entier naturel.pdf`, sans copie brute. | 2026-06-26 | `python scripts/check_required_sections.py` PASS. |
| `premiere/sequences/s01_representation_donnees/corrige.md` | `scripts/check_required_sections.py` | Libellé singulier `variante acceptable` absent. | Section renommée et critère explicite ajouté. | 2026-06-26 | `python scripts/check_required_sections.py` PASS. |
| `premiere/sequences/s01_representation_donnees/cours_eleve.md` | `scripts/check_document_depth.py` | Profondeur utile et définitions formelles insuffisantes. | Activité d'introduction, définitions formelles, repères d'exemples, extension et aides progressives ajoutés. | 2026-06-26 | `python scripts/check_document_depth.py` PASS. |

## Dettes release Drive

| Dette | Cause | Risque | Impact | Décision | Date cible | Responsable | Critère de fermeture |
|---|---|---|---|---|---|---|---|
| Drive partiellement intégré | 7 copies locales absentes, 3 ressources différées et 5 ressources sensibles rejetées restent classées dans `drive_inventory.csv`. | Publication fondée sur sources incomplètes ou non auditées. | `make release-audit` doit rester en échec. | Maintenir `FINAL_STATUS = NON_RELEASE_READY`; poursuivre les lots d'audit Drive ressource par ressource. | 2026-07-15 | équipe NSI | `scripts/check_drive_mapping_release.py` passe sans `missing_local_copy`, `deferred` ni `rejected_sensitive` bloquant. |
| Portabilité Drive | `source_clean.tar.gz` ne contient pas le miroir brut `Documents_DRIVE`. | Audit extrait non reproductible si un contrôle local déréférence les fichiers Drive. | L'audit extrait doit utiliser le contrôle portable. | Séparer `check_drive_enrichment_traceability.py` local et `check_drive_enrichment_traceability_portable.py` portable. | 2026-06-26 | équipe NSI | `timeout 180 make audit-extracted-source` passe sans miroir Drive. |
