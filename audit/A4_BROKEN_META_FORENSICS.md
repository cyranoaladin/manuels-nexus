# A4 — FORENSIQUE DES BROKEN_META_REFERENCES (AVANT CORRECTION)

`START_SHA = 9c832d6324274c25c8526b3ce3d64616454d40b0` (PRE-A4 scellé).
**A4_BROKEN_META_START = 2730** (mesuré par régénération fraîche, pas repris
d'un rapport). Version machine (2730 enregistrements structurés, fingerprints
100 % mappés, champs §5 complets) : `audit/A4_BROKEN_META_FORENSICS.json`.

## Namespaces de référence (§6)

| reference_field | namespace attendu | résolution |
| --- | --- | --- |
| `capacites[*]` | CAPACITY_ID | code `C{n}` du contrat, ref programme (`ref_capacite`), ou ID scopé chapitre `{CHAPTER_ID}-C{n}` |
| `capacites_codes[*]` | CAPACITY_ID (code) | code du contrat, ref, ou prérequis |
| `methodes[*]` | METHOD_ID | alias `M{n}` (index par chapitre) ou ID complet de méthode du même chapitre |

Une capacité n'est jamais résolue contre un exercice ; un alias de méthode
n'est résolu que dans son chapitre. Aucun pool d'IDs global.

## Clusters (somme = 2730, zéro UNKNOWN/OTHER opaque)

| cluster | count | namespace | cause racine | stratégie |
| --- | --- | --- | --- | --- |
| CAP-SCOPED-ID | 1478 | CAPACITY_ID | **analyzer_defect** : les objets référencent l'ID scopé chapitre `{CHAPTER_ID}-C{n}` dont le code EST au contrat (ex. `TNSI-STRUCTURES-DONNEES-C3` ↔ contrat C3/`T-STRUCT-01C`) ; le resolver ne modélise pas ce namespace | A4.1 : resolver accepte le préfixe EXACT du chapter_id + mapping code→ref (injectif, zéro fuzzy) |
| MET-PHANTOM | 476 | METHOD_ID | **META sur-déclarée** : références M2..M6 vers des méthodes jamais créées (chapitres TCOMPL/TEXP/NSI à 1 méthode) ; aucun contrat n'exige ces méthodes | A4.7 : corriger les références META (WRONG_REFERENCE / TARGET_NEVER_CREATED) |
| MET-LEGACY-SUFFIX | 452 | METHOD_ID | **analyzer/schema** : 14 chapitres NSI ont leur unique méthode au schéma legacy `-METH-01` ; `METHOD_ID_SUFFIX_RE` ne dérive pas d'alias → toutes les références `M1` cassent (438) + 14 flags sur les méthodes elles-mêmes | A4.2 : étendre la dérivation d'alias au schéma `METH-0n` (stricte) |
| MET-LEGACY-DUP | 240 | METHOD_ID | **doublon legacy** : 6 chapitres TSPE gardent `{CHAPTER}-METH-01` byte-identique (hors ligne id) au `…-ME-001` migré → alias M1 ambigu | A4.3 : dry-run, preuve d'identité, suppression des 6 doublons, régénération des masters TSPE |
| CAPCODES-ABSENT | 48 | CAPACITY_ID | code (`C3`, `C6`…) absent du contrat validé | A4.7 : corriger les références META (contrat = autorité) |
| CAP-LEGACY-ADGK | 19 | CAPACITY_ID | slug legacy `1NSI-ADGK-*` (migration ADGK→APT documentée : `audit/ID_MIGRATION_1NSI_ADGK_TO_APT.*`) | A4.3 : mapping de migration avec dry-run |
| CAP-CODE-ABSENT | 17 | CAPACITY_ID | capacité scopée/nue absente du contrat (ex. `1SPE-TRIGONOMETRIE-C3` vs contrat C1-C2 ; `C6` TCOMPL/TEXP) | A4.7 : corriger les références META |

Récapitulatif par nature : analyzer/schema = 1930 (70,7 %) ; legacy = 259 ;
références réellement fausses (cibles jamais créées / hors contrat) = 541.

## Preuves clés

- CAP-SCOPED-ID : contrat `TNSI-STRUCTURES-DONNEES` = 14 capacités
  (C1..C14, refs `T-STRUCT-*`) ; les objets référencent exactement
  `TNSI-STRUCTURES-DONNEES-C1..C14` → 100 % valides sémantiquement.
- MET-LEGACY-DUP : `diff` de `TSPE-CALCUL-INTEGRAL-METH-01.tex` vs
  `TSPE-INTEG-ME-001.tex` = UNE ligne (l'id META). Chapitres concernés :
  TSPE-CALCUL-INTEGRAL, TSPE-COMBINATOIRE, TSPE-GEOMETRIE-ESPACE,
  TSPE-LOGARITHME, TSPE-PRIMITIVES-EQDIFF, TSPE-PROBABILITES. Références
  entrantes des fichiers legacy : masters générés
  `build/MANUEL_TSPE_2026-2027_{eleve,professeur}.tex`.
- MET-PHANTOM : ex. `TCOMPL-AIR-EX-009` déclare `"methodes": ["M1","M5"]`,
  le chapitre n'a que ME-001 ; aucun fichier M5 n'existe.
- CAP-CODE-ABSENT : `1SPE-TRIGONOMETRIE` contrat = C1, C2 ; 3 objets
  référencent C3.

## Ordre d'exécution (§9)

A4.1 (analyzer capacités) → A4.2 (schema alias METH) → A4.3 (doublons
legacy + migration ADGK) → A4.7 (références réellement fausses, avec
dry-run, garde anti-corruption LaTeX et invalidation des reviews).
Chaque sous-lot suit le protocole §14 (test rouge → fix → delta exact →
fail-on-new → commit atomique). Aucune modification de source avant le
scellement de cette forensique.
