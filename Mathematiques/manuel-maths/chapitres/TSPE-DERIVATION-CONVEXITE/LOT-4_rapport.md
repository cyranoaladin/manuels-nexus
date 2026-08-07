# LOT 4 — Exercices et corrigés du chapitre TSPE-DERIVATION-CONVEXITE

## Date : 23 juillet 2026

## Contenu produit

### 52 exercices (3 parcours, 6 capacités)

| Capacité | ◆ | ◆◆ | ◆◆◆ | Total |
|----------|---|----|-----|-------|
| C1 (dérivée composée) | 4 | 4 | 2 | 10 |
| C2 (étude complète) | 4 | 4 | 2 | 10 |
| C3 (inégalités convexité) | 3 | 3 | 2 | 8 |
| C4 (esquisse courbe) | 3 | 3 | 2 | 8 |
| C5 (lecture graphique) | 3 | 3 | 2 | 8 |
| C6 (démonstration tangentes) | 3 | 3 | 2 | 8 |
| **Total** | **20** | **20** | **12** | **52** |

Ratio parcours : 38,5 % / 38,5 % / 23 % (objectif 40/40/20).

### 52 corrigés (copie modèle 10–20 lignes)

Chaque corrigé suit le standard « copie modèle » : rédaction complète attendue d'un élève,
théorèmes cités, hypothèses vérifiées, commentaires de marge (\commentaireMarge).

### 16 coups de pouce (fichiers -CDP séparés)

Répartis sur les exercices ◆ (parcours 1) et certains ◆◆ pour les capacités C1–C6.

## Gates

### R2 — Vérification SymPy (verify_sympy.py)
- **106 OK / 0 FAIL** (52 exercices + 52 corrigés + 2 cours/méthodes avec VERIFY)
- 21 REVIEW : fichiers CDP et cours/méthodes sans bloc VERIFY (revue humaine, normal)
- Règle VERIFY respectée : aucune assertion supprimée, toutes les erreurs corrigées par recalcul

### R3 — Couverture capacités × parcours (coverage_report.py)
- Toutes les cases capacité × parcours ont ≥ 2 exercices : **PASS**
- Cours : 6/6 capacités ✓
- Méthodes : 5/5 fiches ✓
- QCM et remédiation : LOT 5 (non couverts ici)

### R6 — Compilation (assemble.py)
- `make chapter CHAP=TSPE-DERIVATION-CONVEXITE` : PDF 21 pages généré
- LuaLaTeX 1.17.0, TEXMFCACHE=/tmp/texmf-cache
- verify_pdf : PASS

## Détail des corrections VERIFY (transparence)

21 exercices ont nécessité une correction de bloc VERIFY après la première génération.
Toutes les corrections sont des recalculs de la valeur vraie (règle VERIFY), jamais des suppressions :
- Valeurs de substitution erronées (EX-001, EX-003, EX-008, EX-018, EX-027, EX-042, EX-049)
- Comparaisons enchaînées Python (`a == b == c`) interdites (EX-039, EX-049)
- `assert expr > 0` non évaluable symboliquement (EX-020, EX-038, EX-050)
- `expand(x) == forme_factorisée` faux (EX-003, EX-043, EX-046, EX-050)
- Erreur d'intégration (EX-031 : antiderivée corrigée)
- `simplify(a) == b` remplacé par `simplify(a - b) == 0` (EX-016, EX-024, EX-025, EX-026)

## Coût API estimé : ~0 $

## Audit 2026-08-05 (branche terminale/collection-v1) — LOT 4
52 exercices + corriges + coups de pouce. SymPy 0 FAIL. R3 non automatisable
(pas de DB), mode ex-nihilo deja accepte.
