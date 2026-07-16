# LOT 0 — Contrat du chapitre 1SPE-EXPONENTIELLE

Date : 2026-07-16. Coût API estimé : ~0 $.

## Référentiel

- Source : BO n° 14 du 2 avril 2026, analyse, fonction exponentielle.
- Fichier : `referentiel/capacites_1SPE_EXPONENTIELLE.json` (5 capacités).
- Note R7 : formulations reprises du texte officiel. A_VALIDER_HUMAIN.

## Capacités

| Code | Libellé élève | Démonstration exigible |
|---|---|---|
| C1 | Définition : unique solution de y'=y, y(0)=1 | Non |
| C2 | Propriétés algébriques (exp(a+b), exp(-a), exp(na)) | Oui (exp(a+b)) |
| C3 | Variations et limites en ±∞ | Non |
| C4 | Dériver e^{u(x)} | Non |
| C5 | Équations et inéquations avec l'exponentielle | Non |

## Prérequis (R1–R5)

- R1 : Dérivée somme/produit/quotient (1SPE-DERIVATION-GLOBAL)
- R2 : Signe de la dérivée et variations (1SPE-DERIVATION-GLOBAL)
- R3 : Résolution second degré (1SPE-SECOND-DEGRE)
- R4 : Puissances entières (2GT)
- R5 : Suites géométriques (1SPE-SUITES)

## Contrat

- Fichier : `chapitres/1SPE-EXPONENTIELLE/contrat.yaml`.
- Situation d'accroche : croissance bactérienne (doublement toutes les 20 min).

## Revue adversariale

- R1 : les 5 capacités sont dans le périmètre BO 2026 (analyse, exponentielle). PASS.
- C2 démonstration exigible (relation fonctionnelle) : conforme. PASS.
- Prérequis : R1-R2 depuis DERIVATION-GLOBAL, R3 depuis SECOND-DEGRE, R5 depuis SUITES. PASS.

Mode : MODE FICHIERS / ex nihilo.
