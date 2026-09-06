# Dossier Scellé d'Acceptation par Lots — Décision Release Owner

## 1. Synthèse du Portefeuille et Métriques de Clôture

- Manuels de la collection : `6` (12 variantes : 6 élèves + 6 professeurs)
- Chapitres audités : `52` (38 STRONG, 14 ADEQUATE, 0 WEAK, 0 UNUSABLE)
- Objets du corpus partitionnés en lots : `2120` (couverture 100.0%, 0 collision)
- Nombre de lots sémantiques : `8`
- Cellules d'alignement sémantique auditées (double aveugle) : `371` (`371` alignées, 0 désaccord)
- Questions de QCM auditées : `490` (0 défaut scientifique, 0 défaut pédagogique, 100% diagnostics)
- Dettes Produit P0 / P1 / P2 : `0` / `0` / `0`
- `ALL_PRODUCT_DEBTS_ZERO` : `True`
- Empreinte cryptographique consolidée (`CONTENT_SOURCE_CLOSURE_DIGEST`) : `sha256:9b3ccf9a81c5520fbb7e03b7b2d3e7bf2057a02834b6d908bf3be5f49f3b553f`
- Statut de gouvernance : `SINGLE_HUMAN_RELEASE_DECISION_REQUIRED`

## 2. Lots Sémantiques d'Objets Soumis à Décision Unique

| Lot | Manuel | Objets | Digest Contenu | Méthode de Validation | Statut Pré-Audit |
|---|---|---|---|---|---|
| `BATCH-1SPE-COURS-METHODES` | `1SPE` | `111` | `sha256:c4071f47f774...` | Vérification formelle des définitions et théo... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-1SPE-EXERCICES-CORRIGES` | `1SPE` | `1169` | `sha256:db096cb43f50...` | Calcul formel SymPy des solutions, étayage di... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-1SPE-EVAL-REMEDIATION-QCM` | `1SPE` | `137` | `sha256:c4dd25f5bf09...` | Audit qualitatif QCM (distracteurs didactique... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-TSPE-CORPUS` | `TSPE_2026_2027` | `56` | `sha256:31a39f116d3f...` | Vérification des preuves mathématiques, confo... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-TCOMPL-CORPUS` | `TCOMPL` | `200` | `sha256:b393b8e5f1f9...` | Vérification didactique adaptée aux profils n... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-TEXP-CORPUS` | `TEXPERTES` | `126` | `sha256:7c53072ef83f...` | Exactitude formelle des démonstrations arithm... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-NSI-1RE-CORPUS` | `1NSI` | `210` | `sha256:b5c58f18f2f2...` | Exécution Python 3.12 des codes sources, typa... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |
| `BATCH-NSI-TLE-CORPUS` | `TNSI` | `111` | `sha256:14d4e5603f39...` | Vérification des structures de données (arbre... | `AUDITED_VALIDATED_AWAITING_RELEASE_OWNER_BATCH_ACCEPTANCE` |

## 3. Candidats PDF Certifiés (build/certified_unsigned_release_candidates/)

| Cible | Pages | SHA256 | Chemin Stagé |
|---|---|---|---|
| `1SPE_eleve` | `371` | `sha256:f3b8ec66584b...` | `build/certified_unsigned_release_candidates/1SPE_eleve.pdf` |
| `1SPE_professeur` | `645` | `sha256:31c99efdca57...` | `build/certified_unsigned_release_candidates/1SPE_professeur.pdf` |
| `TSPE_2026_2027_eleve` | `205` | `sha256:e6e0bb31f0b2...` | `build/certified_unsigned_release_candidates/TSPE_2026_2027_eleve.pdf` |
| `TSPE_2026_2027_professeur` | `309` | `sha256:eaecf91d489e...` | `build/certified_unsigned_release_candidates/TSPE_2026_2027_professeur.pdf` |
| `TCOMPL_eleve` | `138` | `sha256:d23883877f8f...` | `build/certified_unsigned_release_candidates/TCOMPL_eleve.pdf` |
| `TCOMPL_professeur` | `216` | `sha256:0a38540e1587...` | `build/certified_unsigned_release_candidates/TCOMPL_professeur.pdf` |
| `TEXPERTES_eleve` | `92` | `sha256:c713fcf1a8ea...` | `build/certified_unsigned_release_candidates/TEXPERTES_eleve.pdf` |
| `TEXPERTES_professeur` | `144` | `sha256:d98fb2614475...` | `build/certified_unsigned_release_candidates/TEXPERTES_professeur.pdf` |
| `1NSI_eleve` | `119` | `sha256:9920613cb473...` | `build/certified_unsigned_release_candidates/1NSI_eleve.pdf` |
| `1NSI_professeur` | `209` | `sha256:3c16053f183f...` | `build/certified_unsigned_release_candidates/1NSI_professeur.pdf` |
| `TNSI_eleve` | `56` | `sha256:3aae5fab5c8b...` | `build/certified_unsigned_release_candidates/TNSI_eleve.pdf` |
| `TNSI_professeur` | `85` | `sha256:0bce2214e0ce...` | `build/certified_unsigned_release_candidates/TNSI_professeur.pdf` |

## 4. Chaîne de Preuves Cryptographiques Vérifiées

- `BLOCKER_TAXONOMY` : `sha256:7c15386109654523f1b64da5ecaf9d1677aa4e5870e18be41cff68c6f377b330`
- `CERTIFIED_UNSIGNED_RELEASE_CANDIDATES` : `sha256:88edb8c3b13d6ed88d61afcbc99dda482d6f5e871d8b3e716b63fc26ba198441`
- `CHAPTER_PEDAGOGICAL_QUALITY` : `sha256:b6a4b7361993139c7fa9a82d3046c9b0f99416fdc85450f4eb9be871f8603515`
- `EDITORIAL_QUALITY_AUDIT` : `sha256:d2a2084a19231038dd757c089f83cd0bece59a0e70f2c57ad83f1182f73bf1f9`
- `FIGURES_QUALITY_AUDIT` : `sha256:40dcfb914a629806ef4fe7b739c488f2227f0f57adaf5d984494cf05e253c951`
- `QCM_QUALITY_AUDIT` : `sha256:4d2a772e7751476989ac11ac5149fd6af5c02827ce16d21bc1dac7821f2dafe3`
- `RELEASE_OBJECT_BATCH_AUDIT` : `sha256:3357a6770932dd305279adaf0481012ec51f9ac628ecafc1dec2f3800fd60cf2`
- `SEMANTIC_ALIGNMENT_AUDIT` : `sha256:56fb0223953c4627223664794c2cb43e9d07205d7328299fe0849d2c128351c7`
- `SOLUTIONS_COMPLETENESS_AUDIT` : `sha256:0c35db390668526a54ca1b2649f3daa9db58ba43ead594c758e16468ee81a8e6`

## 5. Décision Requise du Release Owner

> [!IMPORTANT]
> Ce dossier est cryptographiquement lié à `CONTENT_SOURCE_CLOSURE_DIGEST`.
> Conformément aux règles de gouvernance, aucun agent ne s'auto-approuve.
> La signature unique du Release Owner humain valide simultanément les 8 lots,
> l'alignement sémantique et autorise la promotion atomique des 12 PDF vers MANUELS_PDF_PUBLICATION/.
