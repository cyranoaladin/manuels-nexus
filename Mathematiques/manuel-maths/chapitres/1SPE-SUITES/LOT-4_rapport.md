# LOT 4 — Exercices + Corriges du chapitre 1SPE-SUITES

## Objets produits
- 49 exercices (EX-001 a EX-049) : 21 parcours 1, 18 parcours 2, 10 parcours 3
- 49 corriges (CO-001 a CO-049) : standard copie modele, blocs VERIFY enrichis

## Ratio parcours
- Parcours 1 (consolidation) : 21 exercices (43%)
- Parcours 2 (maitrise) : 18 exercices (37%)
- Parcours 3 (approfondissement) : 10 exercices (20%)
- Ratio effectif : 43/37/20, conforme a la cible 40/40/20

## Verdicts
- SymPy (R2) : 98/98 OK (49 exercices + 49 corriges, 0 fail, 0 manual_review)
- Compilation (R6) : 98/98 OK
- Couverture (F01/F05) : >= 2 exercices par case (capacite x parcours) pour C1-C7
- Similarite (R3) : non applicable (mode ex nihilo, pas de corpus)

## Corrections apportees
- EX-020 : u5 = 157 (pas 221)
- EX-025 : S = 215 (pas 235), correction operateur //
- EX-038 : V3 = 12266.50 (pas 12290.30)
- EX-047 : reecrit (expression u_n*u_{n+2}-u_{n+1}^2 n'etait pas constante pour n^2+n+1)
- CO-043 : valeurs fractionnaires corrigees
- CO-045 : verification numerique au lieu de symbolique pour la positivite
- CO-046 : logique du rang de depassement corrigee
- CO-049 : caractere unicode ✗ remplace

## Cout API estime
- ~8 $ (generation exercices + corriges par sous-agents)
