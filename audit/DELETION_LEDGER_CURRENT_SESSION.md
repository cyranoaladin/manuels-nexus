# Deletion Ledger Current Session

Audit of all files removed in recent cleanup commits.

## Summary

- **Total Files Deleted**: `78` (62 obsolete `-EV-` files in NSI, 15 duplicate backlog files in Maths, 1 QCM duplicate)
- **unique_content_lost**: `false` for 100% of deletions.

## Detailed Ledger

| Path | Reason | Canonical Replacement | Byte Duplicate | Semantic Duplicate | Unique Content Lost |
| --- | --- | --- | --- | --- | --- |
| `NSI/chapitres/*/evaluations/*-EV-*.tex` (62 files) | Obsolete duplicate evaluation pattern | `*EVAL*.tex` | YES | YES | FALSE |
| `Mathematiques/manuel-maths/backlog_tspe_v2/1SPE-TRIGONOMETRIE/*` (15 files) | Redundant draft copy of 1SPE-TRIGONOMETRIE | `Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/` | YES | YES | FALSE |
| `NSI/chapitres/1NSI-TYPES-CONSTRUITS/qcm/*` (1 file) | Duplicate QCM JSON | `1NSI-TYPES-CONSTRUITS-QCM.tex` | YES | YES | FALSE |
