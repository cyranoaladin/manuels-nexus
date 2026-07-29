# Etat de la collection Nexus Reussite — Mathematiques

Date de mise a jour : 28 juillet 2026.

## Premiere specialite (1SPE)

- **Statut contenu** : 10 chapitres produits (LOT 0→7), tag historique `manuel/1SPE-v1`
- **Statut build** : variantes eleve + professeur recompilables via `scripts/assemble_manuel.py`
- **Livrables (28/07/2026)** :
  - eleve : `build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` — **365 p.**, verify_pdf PASS
  - professeur : `build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` — **406 p.**, verify_pdf PASS
  - sommaire : 10 chapitres numerotes 1→10, titres accentues, plus de doublons

### Inventaire exercices (hors CDP)

| Chapitre | EX | CDP | Ecart E5 (≥50 EX, CDP parcours ◆) |
|---|---:|---:|---|
| Suites | 49 | 0 | −1 EX, CDP manquants |
| Second degre | 42 | 0 | −8 EX, CDP manquants |
| Derivation locale | 50 | 18 | OK |
| Derivation globale | 53 | 18 | OK |
| Exponentielle | 50 | 18 | OK |
| Trigonometrie | 20 | 8 | reduit BO 2026 (C3–C5 retires) |
| Produit scalaire | 50 | 18 | OK |
| Geometrie reperee | 50 | 18 | OK |
| Proba conditionnelles | 50 | 18 | OK |
| Variables aleatoires | 50 | 18 | OK |
| **Total** | **464** | **134** | |

### Gates

| Gate | Statut |
|---|---|
| Compilation 2 variantes | a reattester a chaque rebuild |
| verify_pdf | PASS sur derniers builds |
| SymPy residuel | FAIL connus Suites (4) et Second degre (7) |
| BAT commercial (plan 2026-07-26) | non demarre (0/241 etapes) |
| Validation humaine BO / specimen | en attente (`A_VALIDER_HUMAIN.md`) |

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
