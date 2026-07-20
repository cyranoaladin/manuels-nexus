# ÉTAT COLLECTION — Nexus Réussite

Dernière consolidation : 16 juillet 2026 (post E.2-E.4).

| Manuel | Livré | En cours | Reste / pause |
|---|---|---|---|
| Mathématiques Première | Suites (LOT 0–7, PDF 77 p., rapprochement 0 écart) ; Second degré (LOT 0–7, PDF 61 p., rapprochement 0 écart) ; Dérivation locale LOT 0–4 partiel (30 exercices, 5 capacités) | Intégrité E.2-E.4 clôturée ; verify_pdf et make specimen en CI ; Dérivation locale : compléter le seuil E5 de 50 exercices | LOT 5–7 du chapitre actif, Dérivation globale et chapitres suivants jusqu'à Variables aléatoires, puis lots finaux |
| Mathématiques Terminale | Aucun bootstrap de production attesté | — | J4 : référentiel officiel, architecture puis 13 chapitres TSPE et blocs d'épreuve |
| NSI Première | Installation ; pilote Types construits LOT 0–7 ; charte v3.2 ; PDF 34 p. verify_pdf OK ; rapprochement 0 écart | — | Validation humaine conjointe pilote/charte, non bloquante ; puis chapitres 2 à 10 |
| NSI Terminale | Aucun chapitre attesté | — | J6 : chapitres 1 à 12, ECE et écrit |

## Preuves consultées

- Mathématiques : rapprochements `validations/E2/rapprochement_suites.md` et
  `rapprochement_second_degre.md` ; addendums datés dans LOT-7_rapport.md ;
  `make test` 341 pass, `make specimen` 0, `check_charte_sync` 6/6.
- NSI : rapprochement `NSI/validations/E2_rapprochement_pilote_nsi.md` ;
  `make test` 214 pass, `gates-corpus-strict` tout VERT, verify_pdf branché.
- Assertion amsthm : `test_nexus_class_loads_amsthm_after_amsmath_for_qed` PASS.
- Défaut fermé : sous-titre couverture paramétré via `\matiere`/`\niveau` (charte v4).

## Prochaine action

J3 — reprendre Mathématiques Première sur le chapitre `1SPE-DERIVATION-LOCAL`, dont le
seuil de 50 exercices précède son LOT 5.
