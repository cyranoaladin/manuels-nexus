# MISSION LOG — Manuels NSI

## 2026-07-15 — Installation + Bootstrap

- Installation : connexion corpus, adaptation pipeline, smoke tests (commit 2bca1c2)
- PHASE 0 bootstrap : referentiel genere (114 capacites), LOT R pilote recolte (P04, 21 fichiers, 5/5 capacites)
- Cout LLM : 0 $ (redaction locale)

## 2026-07-16 — Intégrité E.2-E.4

- verify_pdf branché dans `scripts/assemble.py` (import depuis `scripts/pdf_integrity.py`)
- Pilote recompilé via le chemin verify_pdf : 34 p., 213 Ko, polices embarquées
- Rapprochement `NSI/validations/E2_rapprochement_pilote_nsi.md` : 0 écart objet
- Gates : `make test` 214 pass, `gates-corpus-strict` tout VERT, `check_charte_sync` 6/6
