# BUILD_MANIFEST Semantics Specification (Lot A1)

Formal semantic classification and operational rules for `audit/BUILD_MANIFEST.json`.

> Corrigé le 2026-08-18 (`audit/PROVENANCE_CORRECTION_1361cf37.md`). La
> version précédente déclarait le manifeste « synchronized with current
> repository HEAD SHA » — sémantique auto-référentielle qui a entretenu une
> boucle de dizaines de commits `final head_sha alignment` sans point fixe
> (un fichier suivi ne peut pas attester le SHA du commit qui le contient).

## Semantic Classification

- **manifest_type**: `CURRENT_EMPTY_REGISTRY` (`builds: []` valide).
- **provenance.head_sha semantics**: `OBSERVED_BUILD_SOURCE_SHA` — le SHA du
  commit source observé lors de la dernière attestation de build. Ce n'est
  PAS le HEAD courant. Contrat vérifié par le code
  (`_require_git_ancestor`) : `provenance.head_sha` doit être un **ancêtre**
  de HEAD (`git merge-base --is-ancestor`). Aucune égalité exigée, donc
  **aucun réalignement manuel** n'est nécessaire ni autorisé après de
  nouveaux commits.
- **digest semantics**: `source_digest`/`model_digest` attestent l'état
  observé au moment de l'attestation. Pour un registre vide
  (`builds: []`), une divergence de digests est tolérée par le pipeline
  (capacité `empty_manifest_refresh`) ; pour des builds observés
  (`builds` non vide), les digests doivent correspondre exactement.
- **branch semantics**: `provenance.branch` doit correspondre à la branche
  courante (rebind autorisé uniquement pour un registre vide via la capacité
  dédiée).
- **artifact_required**: `NO`.
- **staleness_semantics**: `NOT_STALE` pour le registre vide valide.
- **may_track_current_head**: **NO** — interdiction de la boucle
  d'auto-attestation `modifier head_sha → commit → nouveau HEAD → …`.
  `provenance.head_sha` n'est mis à jour que lors d'une nouvelle attestation
  de build réelle.
- **release_authority**: registre vide valide pour l'état courant ; aucune
  décision de gouvernance ne peut s'appuyer sur un manifeste dont les
  invariants (schéma, ancêtre, propreté, branche) ne sont pas vérifiés.

## État courant attesté

- `provenance.head_sha = 31c99587a1c071e211ff77e1302c84f0b309396a`
  (ancêtre du HEAD scellé, commit de la dernière attestation).
- `builds = []`, `dirty = false`,
  `branch = audit/adversarial-reconciliation-2026`.
