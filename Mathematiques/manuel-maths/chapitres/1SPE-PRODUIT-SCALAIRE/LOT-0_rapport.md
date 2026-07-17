# LOT 0 — Contrat du chapitre 1SPE-PRODUIT-SCALAIRE

Date : 2026-07-17. Cout API estime : ~0 $.

## Referentiel

- Source : BO n 14 du 2 avril 2026, geometrie, produit scalaire.
- Fichier : `referentiel/capacites_1SPE_PRODUIT_SCALAIRE.json` (5 capacites).
- Note R7 : formulations reprises du texte officiel. A_VALIDER_HUMAIN.

## Capacites

| Code | Libelle eleve | Demonstration exigible |
|---|---|---|
| C1 | Produit scalaire : definition geometrique, projection, expression analytique | Non |
| C2 | Proprietes : bilinearite, symetrie, norme, ||u||^2 = u.u | Oui (expression analytique) |
| C3 | Orthogonalite (u.v=0), calcul d'angles | Non |
| C4 | Applications geometriques : mediatrice, hauteurs, aires | Non |
| C5 | Formule d'Al-Kashi a^2=b^2+c^2-2bc cos(A) | Oui |

## Prerequis (R1-R5)

- R1 : Vecteurs et coordonnees (2GT)
- R2 : Norme d'un vecteur (2GT)
- R3 : Trigonometrie (1SPE-TRIGONOMETRIE)
- R4 : Calcul litteral (2GT)
- R5 : Theoreme de Pythagore (2GT)

## Contrat

- Fichier : `chapitres/1SPE-PRODUIT-SCALAIRE/contrat.yaml`.
- Situation d'accroche : randonneur, calcul de distance et d'angle entre trajets.

## Revue adversariale

- R1 : les 5 capacites sont dans le perimetre BO 2026 (geometrie, produit scalaire). PASS.
- C2 demonstration exigible (expression analytique) : conforme. PASS.
- C5 demonstration exigible (Al-Kashi) : conforme. PASS.
- Prerequis : R1-R2 depuis 2GT, R3 depuis TRIGONOMETRIE, R4-R5 depuis 2GT. PASS.

Mode : MODE FICHIERS / ex nihilo.
