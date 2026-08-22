# Unattributed PDFs Ledger

Audit historique des 22 anomalies `unattributed_pdfs`.

L'ancienne version de ce document affirmait que les 22 PDF étaient des
fixtures de test situées sous `tests/fixtures/` ou `audit/fixtures/`. Aucun
des 22 chemins réels ne satisfaisait cette description ; l'affirmation était
fausse et n'a jamais constitué une preuve valide.

## Attribution technique réelle

L'attribution versionnée et vérifiable des 22 PDF vit désormais dans
`audit/PDF_ARTIFACT_REGISTRY.yaml` (schéma
`audit/schemas/v1/pdf-artifact-registry.schema.json`), chargée
inconditionnellement par `scripts/inventory_collection.py`. Le design complet
et la matrice de preuve (chemins, SHA-256, commits, blobs) sont archivés dans
`docs/superpowers/specs/2026-08-21-pdf-artifact-attribution-design.md`.

Le registre emploie exactement trois rôles, sans `UNKNOWN`, `FIXTURE` ni
`generated` :

- **`HISTORICAL_PUBLICATION_SNAPSHOT`** (12 fichiers, `MANUELS_PDF_PUBLICATION/`) —
  introduits ensemble au commit `e630c5adcff0a8993bbf565edfb98b7820038ab3`,
  blob identique à leur origine canonique de build à ce commit. Ce ne sont pas
  des builds observés actuels ; leur `release_state` est
  `STALE_UNDECIDED`.
- **`OFFICIAL_PROGRAM_AUTHORITY`** (2 fichiers,
  `NSI/corpus_nsi/00_programmes_officiels/`) — copies locales officielles des
  programmes NSI Première/Terminale (BO 2019), vérifiées par code, SHA-256 et
  URL de domaine officiel contre `docs/programmes/PROGRAMMES_2026_2027.yaml`.
  Ce rôle établit provenance et authenticité, pas l'applicabilité à l'édition
  2026-2027 (réservée à l'audit réglementaire T2).
- **`HARVEST_NON_PUBLISHABLE_HISTORICAL_RENDER`** (8 fichiers,
  `NSI/corpus_nsi/latex/packs/premiere/P13/`) — rendus historiques hors
  graphe de release, provenance
  `REPOSITORY_HISTORY_WITHOUT_BUILD_RECEIPT` (coexistence PDF/`build.sh`
  déclaré au commit d'import `10a15746bdbb043c44d461eac40fa4041d23988e`, sans
  preuve de compilation). `compilation_evidence=false` pour les 22 records.

Aucun des 22 PDF n'est une preuve de compilation ni un build canonique.
Aucune allowlist opaque ni inférence par basename n'a été utilisée : le
lookup du registre est un chemin exact, `registry[path]`.

## Dette release distincte de l'attribution technique

L'attribution technique (`unattributed_pdfs=0`) ne décide pas du sort des 12
instantanés de publication historiques. Cette dette reste une raison release
explicite et agrégée :

```text
COLLECTION:publication_snapshots:stale_undecided:12
```

Elle n'entre dans aucune anomalie, qualification ou baseline ; elle exige une
décision humaine ultérieure et n'est jamais fermée automatiquement par une
égalité future avec le PDF canonique courant.

De même, la correction technique des 10 sources `.tex` P13 (faute
`siheader{...}` → `\nsiheader{...}`) ne tranche pas le cycle de vie des 8
rendus historiques : conserver, archiver hors dépôt, ou supprimer avec preuve
d'absence de contenu unique reste une décision humaine séparée, tracée hors
de ce ledger.

## État avant régénération de l'inventaire

Ce document décrit l'attribution technique telle que codée dans le registre
et le loader. La valeur `unattributed_pdfs=0` n'est effective dans
l'inventaire géré (`ETAT_COLLECTION.md`, `audit/INVENTAIRE_COLLECTION.json`)
qu'après régénération depuis un arbre propre (lot suivant de la campagne
T1.2), pas à la lecture de ce seul ledger.
