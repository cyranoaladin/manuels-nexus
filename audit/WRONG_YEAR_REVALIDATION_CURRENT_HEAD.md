# WRONG YEAR — revalidation au HEAD courant

Base d’intégration : `10cb5f07772842d6630d2a2f78531f6900371023`.

## WRONG_YEAR #1

- Candidate : `SRC-BO2026-TSPE-R2027`
- Manuel : `TSPE`; chapitre : aucun
- Source : `docs/programmes/PROGRAMMES_2026_2027.yaml`
- Autorité candidate : `MENE2602919A`
- Autorité correcte 2026-2027 : `MENE1921246A`
- Contenu affecté : **NO**
- Classification : `AUDIT_METADATA_ONLY`
- État courant : déjà neutralisé; le texte 2026 est explicitement hors périmètre jusqu’en 2027-2028.

## WRONG_YEAR #2

- Candidate : alias A5 `MENE2602920A`
- Manuel : `TCOMPL`; chapitre : aucun
- Source : `audit/OFFICIAL_PROGRAM_AUTHORITY_2026_2027.yaml`
- Autorité candidate : `MENE2602920A`
- Autorité correcte 2026-2027 : `MENE1921265A`; futur NOR exact `MENE2902920A`, applicable en 2027-2028
- Contenu affecté : **NO**
- Classification : `AUDIT_METADATA_ONLY`
- État courant : déjà neutralisé; la matrice TCOMPL utilise le programme 2019.

Les deux cas demandés sont donc fermés au HEAD courant sans correction de contenu.

## Findings réglementaires distincts encore ouverts

- `1SPE-TRIGONOMETRIE-C3/C4/C5` : trois lignes `WRONG_YEAR`, avec contenu encore présent dans des méthodes, exercices et évaluations. Classification `CONTENT_DERIVED_FROM_WRONG_PROGRAMME`, décision humaine requise entre retrait et approfondissement explicitement non exigible.
- `1SPE-VARIABLES-ALEATOIRES-C3/C4` : deux lignes `UNSUPPORTED_CLAIM` relatives à la loi binomiale, absente comme notion nommée du programme 1SPE 2026. Décision éditoriale humaine requise.
