# RAG — Architecture cible

## Collections

| Collection | Rôle | Sources | Preuve couverture |
|-----------|------|---------|-------------------|
| nsi_corpus | Corpus pédagogique interne | 03_progressions/supports/, 03_progressions/fiches_cours/ | Oui (status-gated) |
| rag_education | Inspiration externe, Drive audité | sources_catalog.yml type=inspiration | Non |
| nsi_golden_examples | Pilotes historiques | premiere/sequences/, terminale/sequences/ | Non (style_reference_only) |
| nsi_official | Textes officiels | 00_programmes_officiels/ | Non (reference_only) |
| nsi_annales | Annales publiques | À cataloguer | Non |

Justification : level/theme sont des métadonnées filtrables (pas des collections
distinctes) car le volume par thème est faible et la recherche cross-thème est
utile en conception pédagogique.

## Schéma de métadonnées canonique (contrat unique)

Chaque chunk DOIT porter :
- section_anchor (str) : slug du titre ## ou ### découpant le chunk
- capacity_ids (list[str]) : ["P-TABLE-01", ...] depuis le frontmatter
- level (str) : premiere | terminale
- theme (str), notion (str), sequence_id (str)
- document_type (str) : cours_eleve | td | tp | corrige | evaluation | ...
- status (str) : needs_review | draft | needs_content
- path (str) : chemin relatif
- sha256 (str) : hash du fichier source (idempotence)
- collection (str) : nsi_corpus
- source_type (str) : nsi_corpus
- private_data (bool) : false (vérifié à l'ingestion)

Mapping legacy :
- anchor → section_anchor (renommage)
- capacities (str csv) → capacity_ids (list[str]) via split(",")

Le retrieval_contract_adapter (RAG dépôt) retourne le schéma canonique.

## Arborescence d'ingestion

Ingérés :
- 03_progressions/supports/** (corpus principal)
- 03_progressions/fiches_cours/** (fiches de cours)

Exclus :
- premiere/sequences/, terminale/sequences/ → nsi_golden_examples uniquement
- AUDIT/, dist/, .git/, Documents_DRIVE/, rendus_eleves/
- Tout fichier avec private_data: true ou failing check_no_private_data
- NotesEleves.csv, Fichier_Eleves.csv

## Statut

Le RAG indexe needs_review mais EXPOSE le statut : jamais présenté comme validé.
covered reste 0. FINAL_STATUS=NON_RELEASE_READY.
