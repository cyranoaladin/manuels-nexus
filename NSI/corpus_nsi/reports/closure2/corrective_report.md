# Rapport correctif (passe 5)

## Statut : CLOSED_CLEAN

## main

- SHA HEAD : eb01b477f15973487a56aeca43a76325558696b1
- CI RUN_ID : 28444084300, headSha=eb01b47, conclusion=**success**

## RAG pipeline corrige (PR #12)

### Bugs corriges

1. **capacity_ids universellement vides** : lu depuis `meta.get("capacity_ids")`
   (top-level) alors que le frontmatter reel est `official_program.capacities`.
   Corrige : lecture `meta.get("official_program", {}).get("capacities", [])`.

2. **Metadata listes rejetees par Chroma** : capacity_ids stocke comme liste
   Python. Chroma n'accepte que des scalaires. Corrige : serialisation CSV
   (`",".join(capacity_ids)`). Vide = `""` (pas `"none"`).

3. **adapt_metadata round-trip** : fonction ajoutee pour reconvertir CSV en liste.
   Test `test_adapt_metadata_roundtrip` : `["P-TABLE-01","P-TABLE-02"]` ->
   `"P-TABLE-01,P-TABLE-02"` -> `["P-TABLE-01","P-TABLE-02"]`.

4. **level/theme/sequence_id par regex** : remplace par lecture frontmatter directe.

### Affirmation passe 4 RETIREE

La preuve "452 fichiers, 5992 chunks" de la passe 4 n'est pas reproductible
depuis le code committe : capacity_ids etaient vides, metadata listes rejetees
par Chroma sans scalarisation. L'incident est documente dans process_incidents.md.

### RE-PREUVE depuis le code committe (venv propre, apres PR #12)

```
python -m scripts.rag_ingest --db /tmp/chroma_eph
{
  "files_seen": 452,
  "files_ingested": 452,
  "files_skipped_pii": 0,
  "chunks_upserted": 5992,
  "errors": [],
  "dry_run": false
}
```

Requetes :
```
Query: CSV import
hit[0] capacity_ids(stored CSV)='P-TABLE-01,P-TABLE-02'
       capacity_ids(adapted list)=['P-TABLE-01', 'P-TABLE-02']
       level=premiere theme=Traitement de tables seq=P05

Filter: level=terminale → only terminale hits
Non-empty capacity_ids: 197/200 (98.5%)
```

Chroma ephemere detruit apres la preuve. Aucune mutation prod.

## Runbook corrige (PR #12)

Flag `--reindex` inexistant supprime. Comptes marques "a verifier au cutover".
Seul `python -m scripts.rag_ingest` est utilise (ingesteur unifie).

## Cliquet mypy non vacuant (PR #12)

Guard ajoute : assert `"no issues found"` OU `": error:"` dans stdout.
Prouve : VERT (normal), ROUGE (regression +1 erreur), ROUGE (vacuant : stdout
vide => guard echoue).

## audit-core : 4 gates nommes (PR #12 + PR #13)

Ajoutes dans Makefile audit-core :
- check_metadata
- check_links
- check_no_build_artifacts_in_index
- check_uploaded_archive_policy

check_makefile_audit_policy bidirectionnel : PASS.

Ellipsis dans annotations de type (PR #13) : `tuple[Any, ...]` autorise par
heuristique ligne, check_no_placeholders_code : PASS.

## process_incidents.md : complet

4 incidents documentes :
1. Push direct be73955 (passe 1)
2. Amend + force-push PR #7 (passe 2)
3. Push direct 3080147 (passe 3)
4. Preuve RAG non reproductible (passe 4)

## Verification finale (venv propre)

| Check | Resultat |
|-------|----------|
| pytest | 340 passed |
| ruff | All checks passed |
| mypy --strict | Success: no issues found in 209 source files |
| check_no_private_data | PASS |
| audit-core | PASS |
| audit-metrics | PASS |
| audit-idempotence | PASS |
| deliver-pedagogical-archive | PASS |
| deliver-source-zip | PASS |
| package-audit | PASS |
| audit-extracted-source | PASS |
| verify-delivery-archive | PASS |
| rag-smoke-required | echec attendu (prod inchangee) |
| release-audit | echec = backlog Drive (deferred=3, missing=7, rejected=5) |

## Invariants reprouves

```
covered : 0
absent : 22
published : 0
validated_* : 0
FINAL_STATUS = NON_RELEASE_READY
```

## Dette residuelle

Aucune dette technique. mypy=0, ruff=clean, audit-core complet, cliquet
non-vacuant, privacy corrige, manifeste idempotent, RAG pipeline prouve.

## Lot 4 contenu : non
