# Etat de la collection Nexus Reussite — Mathematiques

Date de mise a jour : 29 juillet 2026.

## Premiere specialite (1SPE)

- **Statut contenu** : 10 chapitres produits (LOT 0→7), tag historique `manuel/1SPE-v1`
- **Statut build** : variantes eleve + professeur recompilables via `scripts/assemble_manuel.py`
- **Livrables (29/07/2026)** :
  - eleve : `build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` — **369 p.**, verify_pdf PASS
  - professeur : `build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` — **410 p.**, verify_pdf PASS
  - sommaire : 10 chapitres numerotes 1→10, titres accentues, plus de doublons

### Inventaire exercices (hors CDP)

| Chapitre | EX | CDP | Ecart E5 (≥50 EX, CDP parcours ◆) |
|---|---:|---:|---|
| Suites | 50 | 21 | OK |
| Second degre | 50 | 20 | OK |
| Derivation locale | 50 | 18 | OK |
| Derivation globale | 53 | 18 | OK |
| Exponentielle | 50 | 18 | OK |
| Trigonometrie | 20 | 8 | reduit BO 2026 (C3–C5 retires) |
| Produit scalaire | 50 | 18 | OK |
| Geometrie reperee | 50 | 18 | OK |
| Proba conditionnelles | 50 | 18 | OK |
| Variables aleatoires | 50 | 18 | OK |
| **Total** | **473** | **175** | |

### Gates

| Gate | Statut |
|---|---|
| Compilation 2 variantes | reattestee 29/07/2026 (eleve 369p, professeur 410p), 0 erreur LaTeX |
| verify_pdf | PASS sur derniers builds |
| SymPy residuel | **0 FAIL** — relance complete des 13 chapitres 1SPE/TSPE le 29/07/2026 |
| Tests (`make test`) | 1936 passed / 5 skipped ; 3 echecs preexistants sans rapport (`test_maquette_v5.py`, comparaison visuelle page 13 de la maquette V5, chantier CHARTE distinct) |
| BAT commercial (plan 2026-07-26) | non demarre (0/241 etapes) ; seule la conception (specs) est commitee |
| Validation humaine BO / specimen | en attente (`A_VALIDER_HUMAIN.md`) |

### Correctifs du 29/07/2026 — regressions SymPy (upgrade sympy 1.14)

Une relance exhaustive de `verify_sympy.py` a revele que sympy 1.14 ne
considere plus un `Rational`/`Integer` exact comme egal a un `float` Python
meme numeriquement identique (ancien comportement implicite disparu). 16
assertions VERIFY en echec ont ete corrigees, sans jamais suppression ni
affaiblissement (regle VERIFY) :

- **1SPE-SUITES** (4) : `07_td_fil_rouge` (le seuil de depassement B_n>A_n
  n'etait JAMAIS atteint par l'algorithme decrit — vraie valeur n=1415 et
  non 167, TD entierement reecrit) ; `07_td_contextualise` (demi-vie
  carbone-14 fausse de bout en bout — vraie valeur n=57 siecles et non 58,
  toutes les valeurs numeriques recalculees) ; `FR-R3`, `RE-C6`.
- **1SPE-SECOND-DEGRE** (7) : `07_td_fil_rouge`, `RE-C4` (g(10)=125 et non
  115), `FR-R2`, `FR-R3`, `RE-C1`, `RE-C5`, `FR-R5`.
- **1SPE-PRODUIT-SCALAIRE** (3) : loi d'Al-Kashi, EX-030/CO-030 (division
  flottante Python au lieu de `Rational`).
- **TSPE-DERIVATION-CONVEXITE** (2) : EX-051/CO-051, EX-052/CO-052.

Completion E5/F01 : Suites 49→50 exercices + 21 coups de pouce (0→21) ;
Second degre 42→50 exercices + 20 coups de pouce (0→20). Couverture
capacite×parcours toujours ≥2/case sur les deux chapitres. Fichiers
`.similarity.json` du chapitre Second degre generes pour la premiere fois
(absents du depot jusqu'ici).

### Correctifs du 28/07/2026

- Page de garde et gabarit : rebuild eleve debloque
- Suppression des `\chapter` en double dans 4 fichiers `00_ouverture.tex`
- Titres de contrats accents restaures (4 chapitres)
- Onglet de tranche : longueurs TeX robustes
- Tables : suppression du double `\AtBeginEnvironment{tabular}`

## Terminale specialite (TSPE v1 — rentree 2026-2027)

- **Statut** : en production
- **Referentiel** : BO special n 8 du 25 juillet 2019 (programme 2019)
- Chapitres clos : TSPE-SUITES-LIMITES, TSPE-LIMITES-FONCTIONS, TSPE-DERIVATION-CONVEXITE
- Prochaine tache directive : 5a/5b referentiel + perimetre

## Jalon TSPE v2 (rentree 2027-2028)

- Programme Terminale BO 2026 applicable rentree 2027-2028
- Contenu retire de 1SPE (trigo avancee) en backlog TSPE v2
