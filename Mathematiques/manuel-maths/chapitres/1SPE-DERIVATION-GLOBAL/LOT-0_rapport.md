# LOT 0 — Contrat du chapitre 1SPE-DERIVATION-GLOBAL

Date : 2026-07-16. Coût API estimé : ~0 $.

## Référentiel

- Source : BO n° 14 du 2 avril 2026, analyse, dérivation applications aux variations.
- Fichier : `referentiel/capacites_1SPE_DERIVATION_GLOBAL.json` (5 capacités).
- Note R7 : les formulations reprennent le texte officiel. Incertitudes → A_VALIDER_HUMAIN.

## Capacités

| Code | Libellé élève | Démonstration exigible |
|---|---|---|
| C1 | Dériver les fonctions de référence ($x^n$, $1/x$, $\sqrt{x}$) | Non |
| C2 | Règles de dérivation (somme, produit, quotient) | Oui (somme + produit scalaire) |
| C3 | Signe de la dérivée → tableau de variations | Non |
| C4 | Extremums d'un polynôme de degré 3 | Non |
| C5 | Problème d'optimisation | Non |

## Prérequis (R1–R5)

| Code | Libellé | Origine |
|---|---|---|
| R1 | Taux de variation et nombre dérivé | 1SPE-DERIVATION-LOCAL |
| R2 | Équation de la tangente | 1SPE-DERIVATION-LOCAL |
| R3 | Calcul littéral (développer, factoriser, signe) | 2GT |
| R4 | Second degré (racines, signe, tableau de signes) | 1SPE-SECOND-DEGRE |
| R5 | Sens de variation (définition) | 2GT |

## Contrat

- Fichier : `chapitres/1SPE-DERIVATION-GLOBAL/contrat.yaml`.
- Situation d'accroche : boîte de conserve cylindrique, optimisation du métal pour 500 mL.
- Temps estimés : ◆ 12 h, ◆◆ 10 h, ◆◆◆ 8 h.

## Revue adversariale

- Conformité R1 : les 5 capacités sont dans le périmètre du BO 2026 (analyse, dérivation). PASS.
- Couverture : les opérations sur les dérivées (C2), le lien dérivée-variations (C3), extremums (C4) et optimisation (C5) couvrent la section « Applications de la dérivation ». PASS.
- Prérequis : R1-R2 renvoient à DERIVATION-LOCAL (chapitre précédent), R4 à SECOND-DEGRE. PASS.
- Schéma contrat : format conforme au modèle de DERIVATION-LOCAL. PASS.

## Mode

MODE FICHIERS / ex nihilo. Réseau non utilisé.
