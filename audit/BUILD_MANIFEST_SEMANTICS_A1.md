# BUILD_MANIFEST Semantics Specification (Lot A1)

Formal semantic classification and operational rules for `audit/BUILD_MANIFEST.json`.

## Semantic Classification

- **manifest_type**: `CURRENT_EMPTY_REGISTRY`
- **source_sha_semantics**: Synchronized with current repository HEAD SHA and static model digest (`_model_digest`)
- **artifact_required**: `NO` (Valid empty build registry containing `builds: []`)
- **staleness_semantics**: `NOT_STALE` (Valid empty registry state; must not be termed "stale")
- **may_track_current_head**: `YES`
- **release_authority**: Valid authority for empty build registry at current repository state
