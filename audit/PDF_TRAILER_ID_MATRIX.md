# Matrice des identités de trailer PDF (12 cibles)

Schéma `nexus-pdf-trailer-id/v1`, `producer_schema_version = 1`. Moteur : `This is LuaHBTeX, Version 1.17.0 (TeX Live 2023/Debian)`.

| Famille | Manuel/Livre | Variante | Identité de trailer | Sortie |
|---|---|---|---|---|
| Mathematiques | 1SPE | eleve | `2985EC8A5965D23ED43F20D5651BA6C6` | `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` |
| Mathematiques | 1SPE | professeur | `855D9F882AC39BC3BE5430A15B2D34F3` | `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` |
| Mathematiques | TSPE_2026_2027 | eleve | `F0012FA057C1C32708755CAC5BB00383` | `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf` |
| Mathematiques | TSPE_2026_2027 | professeur | `F861FB6C1C925657B11F3237C73DB2EB` | `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf` |
| Mathematiques | TCOMPL | eleve | `15478E22C252291748071D2F4642C9B7` | `Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_eleve.pdf` |
| Mathematiques | TCOMPL | professeur | `D246A1BE222AC6A320C4B103CA2163D3` | `Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.pdf` |
| Mathematiques | TEXPERTES | eleve | `147DEACB6037563C3DE325ED5AB04967` | `Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_eleve.pdf` |
| Mathematiques | TEXPERTES | professeur | `E1B7E071CEAB1825C81494450E9C99E1` | `Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.pdf` |
| NSI | 1NSI | eleve | `5280F069D2BC34CDDC3E17795762613E` | `NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.pdf` |
| NSI | 1NSI | professeur | `9F5B1E31E3F5A55E9922669A83975561` | `NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf` |
| NSI | TNSI | eleve | `CBCBCB82DA1A20ABF528850B2AF10B98` | `NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf` |
| NSI | TNSI | professeur | `250F6C6846F7BCA516AABF3EEE46E046` | `NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf` |

## Invariants mesurés

- TOTAL_TARGETS = **12**
- UNIQUE_TRAILER_IDS = **12**
- COLLISIONS = **0**

Les identités sont calculées **sans compiler** : elles sont lues dans le
master rendu par les points d'entrée de production (`render_master` côté
Mathématiques, `render_manual_master` après `select_book` côté NSI).
Élève et professeur d'un même manuel diffèrent parce que la variante et le
corps assemblé entrent tous deux dans le préimage.
