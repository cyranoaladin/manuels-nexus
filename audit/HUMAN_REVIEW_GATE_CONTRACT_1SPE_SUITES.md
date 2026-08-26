# HUMAN REVIEW GATE CONTRACT — 1SPE-SUITES

- Source de revue figée : `c667f12b1792f31981b6b5894c8c604df1bce634`
- Digest du set des 161 objets : `sha256:67d8006298299b44029de8ba8f85b500d9b3619997a0c596e63c20e1cffeee2d`
- Verdict : **GOVERNANCE_CONTRACT_INCOMPLETE**
- Matérialisation d'une approbation : **INTERDITE**
- Transition de statut, promotion FULL et clôture de dette : **INTERDITES**

## Ce que le dépôt impose

Deux revues de rôles par chapitre : expert mathématique et expert programme/pédagogie. Aucun élément ne peut être auto-approuvé par l'agent qui l'a produit. Toute décision humaine doit être datée, justifiée et attribuée.

## Sémantiques non définies

| Sémantique | État |
|---|---|
| `distinct_human_reviewers` | `UNKNOWN` |
| `one_human_may_satisfy_two_roles` | `UNKNOWN` |
| `identity_authentication_requirements` | `UNKNOWN` |
| `canonical_receipt_schema` | `UNKNOWN` |
| `canonical_allowed_approval_verdicts` | `UNKNOWN` |
| `approval_scope_granularity` | `UNKNOWN` |
| `source_sha_binding` | `UNKNOWN` |
| `render_pdf_binding` | `UNKNOWN` |
| `shared_dependency_staleness_policy` | `UNKNOWN` |
| `bulk_status_transition_authority` | `UNKNOWN` |

## Gate humain QCM

- `QCM_HUMAN_GATE_OWNER = UNKNOWN`
- `QCM_HUMAN_GATE_GRANULARITY = UNKNOWN`
- `QCM_HUMAN_GATE_CURRENT_STATE = HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL`
- Aucune preuve ne permet de choisir entre couverture par le rôle mathématique, couverture par le rôle programme/pédagogie ou campagne distincte.

## Autorités et limites

| ID | Source | Établit | N'établit pas |
|---|---|---|---|
| `CAHIER_TRACEABILITY` | `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md:71-79` | `human_decision_must_be_dated_justified_attributed` | `identity_authentication`, `receipt_schema` |
| `CAHIER_DOUBLE_REVIEW` | `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md:614-623` | `two_role_reviews_per_chapter`, `role_expert_mathématique`, `role_expert_programme_pédagogie`, `no_agent_self_approval` | `two_distinct_human_identities`, `dual_role_policy` |
| `CAHIER_ARCHIVAL` | `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md:1067-1070` | `double_disciplinary_review`, `human_validations_archived` | `archive_format`, `receipt_schema` |
| `README_RELEASE_INDEPENDENCE` | `README.md:193-214` | `science_programme_editorial_pdf_reviews_are_independent`, `final_human_manual_approval_is_separate` | `chapter_receipt_schema` |
| `README_REVIEW_CHAIN` | `README.md:779-802` | `scientific_then_programme_then_editorial_variant_then_pdf_review`, `final_human_approver_is_user`, `visual_baseline_change_requires_explicit_approval` | `chapter_content_receipt_schema`, `qcm_gate_owner` |
| `GENERIC_VALIDATION_SCHEMA` | `Mathematiques/manuel-maths/schemas/validation.schema.json:6-13` | `generic_per_object_validation_shape`, `generic_verdicts_pass_fail_warning_manual_review`, `reviewer_field_optional` | `human_role`, `reviewer_identity_verification`, `source_sha_binding`, `approval_semantics` |
| `GENERIC_VALIDATION_DATABASE` | `Mathematiques/manuel-maths/db/schema.sql:64-73` | `generic_per_object_validation_storage`, `reviewer_nullable` | `campaign_scope`, `receipt_signature`, `staleness` |
| `LEGACY_OBJECT_RECEIPT_CONVENTION` | `Mathematiques/manuel-maths/docs/03_architecture_technique.md:22-26` | `manual_per_object_revue_humaine_filename_convention` | `receipt_content_semantics`, `chapter_campaign_semantics` |
| `QCM_MACHINE_AUDIT` | `scripts/build_qcm_scientific_answer_key_audit.py:165-195,234-258` | `qcm_machine_rows_are_pending_human_approval`, `machine_audit_cannot_infer_human_approval` | `qcm_human_owner`, `qcm_human_granularity`, `qcm_closure_receipt` |

## Cinq dettes residual13 du chapitre

| Fingerprint | Objet | Statut | Machine | Binding sunset périmé | Condition restante |
|---|---|---|---|---:|---|
| `e8ac154947fefcdb` | `1SPE-SUITES-CO-051` | `generated` | `MACHINE_PASS` | OUI | `ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED` |
| `4b9a00c4ef815951` | `1SPE-SUITES-CR-017` | `generated` | `MACHINE_PASS` | OUI | `ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED` |
| `85454c002c0a1d6a` | `1SPE-SUITES-EX-051` | `generated` | `MACHINE_PASS` | OUI | `ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED` |
| `d6985b17d7cab316` | `1SPE-SUITES-ME-008` | `generated` | `MACHINE_PASS` | NON | `ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED` |
| `8ca4f3f2a9212e39` | `1SPE-SUITES-RE-C8` | `generated` | `MACHINE_PASS` | OUI | `ALL_REQUIRED_REVIEWS_COMPLETE_AND_HUMAN_APPROVAL_RECORDED` |

`PREVIOUS_89 ∩ 1SPE-SUITES = 0`.

Les deux revues de contenu ne valent ni revue éditoriale/variante, ni revue PDF, ni D7, ni approbation print/release. Les packets peuvent seulement fournir des entrées neutres aux humains; ils ne constituent pas des receipts exécutables.
