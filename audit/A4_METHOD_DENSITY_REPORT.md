# A4 — Rapport de densité éditoriale des fiches méthodes (§10 clôture)

Sources : comptages de mots sur les 89 fiches (corps hors META/VERIFY),
similarité textuelle par paires (difflib, corps normalisé), pages mesurées sur
builds réels from scratch — « avant » = build du clone au SHA pré-campagne
`2852cb67`, « après » = build au HEAD de clôture.

## Table par chapitre

| Chapitre | Capacités | Méthodes avant | après | ajoutées | réécrites | mots min | méd | max |
|---|---|---|---|---|---|---|---|---|
| 1NSI-ALGO-DICHO-GLOUTON-KNN | 3 | 1 | 3 | 2 | 1 | 360 | 372 | 426 |
| 1SPE-TRIGONOMETRIE | 5 | 2 | 5 | 3 | 0 | 339 | 352 | 369 |
| TCOMPL-CALCULS-AIRES | 6 | 1 | 6 | 5 | 1 | 318 | 339 | 404 |
| TCOMPL-CORRELATION-CAUSALITE | 5 | 1 | 5 | 4 | 1 | 270 | 299 | 347 |
| TCOMPL-ECHANTILLONNAGE | 6 | 1 | 6 | 5 | 1 | 251 | 313 | 329 |
| TCOMPL-INEGALITES | 5 | 1 | 5 | 4 | 1 | 272 | 277 | 297 |
| TCOMPL-INFERENCE-BAYESIENNE | 5 | 1 | 5 | 4 | 1 | 319 | 337 | 365 |
| TCOMPL-LOGARITHME-HISTORIQUE | 5 | 1 | 5 | 4 | 1 | 288 | 311 | 364 |
| TCOMPL-MODELES-EVOLUTION | 5 | 1 | 5 | 4 | 1 | 309 | 316 | 338 |
| TCOMPL-MODELES-FONCTION | 7 | 1 | 7 | 6 | 1 | 287 | 313 | 332 |
| TCOMPL-TEMPS-ATTENTE | 6 | 1 | 6 | 5 | 1 | 293 | 327 | 350 |
| TEXP-ARITHMETIQUE | 9 | 1 | 9 | 8 | 1 | 256 | 315 | 332 |
| TEXP-COMPLEXES-ALGEBRE-GEOMETRIE | 5 | 1 | 5 | 4 | 1 | 239 | 305 | 326 |
| TEXP-COMPLEXES-TRIGO-POLYNOMES | 7 | 1 | 7 | 6 | 1 | 292 | 317 | 380 |
| TEXP-GRAPHES | 5 | 1 | 5 | 4 | 1 | 285 | 339 | 446 |
| TEXP-MATRICES-MARKOV | 7 | 1 | 7 | 6 | 1 | 281 | 296 | 348 |
## Pages (variante élève, builds réels)

| Manuel | Pages avant | Pages après | Croissance | Fiches ajoutées au manuel | Pages/fiche |
|---|---|---|---|---|---|
| 1SPE | 373 | 375 | +2 | 3 (TRIGO) | ≈0,67 |
| TCOMPL | 133 | 164 | +31 | 43 | ≈0,72 |
| TEXPERTES | 90 | 109 | +19 | 28 | ≈0,68 |

Croissance homogène (≈0,7 page/fiche sur les trois manuels).

## Signalements

| Contrôle | Résultat |
|---|---|
| OUTLIER_PAGE_GROWTH | **0** (0,67–0,72 page/fiche, uniforme) |
| METHOD_TOO_SHORT (<55 % de la médiane 321 mots) | **0** (min 239) |
| METHOD_TOO_LONG (>160 % de la médiane) | **0** (max 446) |
| NEAR_DUPLICATE_METHODS (ratio difflib > 0,60 sur corps normalisé, 3 916 paires) | **0 paire** |
| DUPLICATED_TEXT_PATTERN | néant au-delà du squelette de gabarit commun (sections imposées) |

Les 15 anciennes fiches M1 partageaient un contenu strictement identique
(« Dériver une fonction composée ») ; après campagne, plus aucune paire de
fiches ne dépasse 0,60 de similarité — chaque capacité a un contenu propre
(exemples numériques distincts, vérifiés par SymPy).
