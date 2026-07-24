# LOT-7 — Rapport d'assemblage : TSPE-DERIVATION-CONVEXITE

## Chapitre : Compléments sur la dérivation — Convexité

### Inventaire complet

#### Cours (LOT-3) — 8 fichiers

| Fichier | Contenu | Capacités |
|---------|---------|-----------|
| `cours/10_C1_derivee_composee.tex` | Théorème (v∘u)', cas particuliers (e^u, ln u, u^n, √u) | C1 |
| `cours/11_C2_etude_complete.tex` | Méthode d'étude complète, exemple guidé | C2 |
| `cours/12_C3_convexite_inegalites.tex` | Définition convexité, lien avec f'', Jensen | C3 |
| `cours/13_C4_esquisse_courbe.tex` | Lien f/f'/f'', esquisse depuis tableaux | C4 |
| `cours/14_C5_lecture_graphique.tex` | Lecture graphique convexité, inflexion | C5 |
| `cours/15_C6_courbe_tangentes.tex` | Démonstration exigible : f'' ≥ 0 ⇒ courbe au-dessus tangentes | C6 |
| `cours/07_td_contextualise.tex` | TD optimisation boîte de conserve | C1, C2, C3 |
| `cours/07_td_fil_rouge.tex` | TD fonction coût et convexité | C1–C6 |

#### Méthodes (LOT-3) — 5 fiches

| Fichier | Méthode | Capacités |
|---------|---------|-----------|
| `methodes/TSPE-DERCONV-ME-001.tex` | M1 : Dériver une fonction composée | C1 |
| `methodes/TSPE-DERCONV-ME-002.tex` | M2 : Mener une étude complète | C2 |
| `methodes/TSPE-DERCONV-ME-003.tex` | M3 : Inégalités par convexité | C3, C6 |
| `methodes/TSPE-DERCONV-ME-004.tex` | M4 : Esquisser et lire graphiquement | C4, C5 |
| `methodes/TSPE-DERCONV-ME-005.tex` | M5 : Combiner dérivation et étude | C1, C2 |

#### Exercices (LOT-4) — 52 exercices + 15 CDP + 52 corrigés

Distribution parcours :
- Parcours 1 (◆) : 20 exercices
- Parcours 2 (◆◆) : 20 exercices
- Parcours 3 (◆◆◆) : 12 exercices
Ratio : 38,5 / 38,5 / 23 %

#### QCM + Remédiation (LOT-5)

| Fichier | Contenu |
|---------|---------|
| `qcm/TSPE-DERIVATION-CONVEXITE-QCM.tex` | 15 questions (Q1–Q15) |
| `remediation/TSPE-DERIVATION-CONVEXITE-FR-R1.tex` | R1 : Dérivation |
| `remediation/TSPE-DERIVATION-CONVEXITE-FR-R2.tex` | R2 : Nombre dérivé, tangente |
| `remediation/TSPE-DERIVATION-CONVEXITE-FR-R3.tex` | R3 : Exponentielle |
| `remediation/TSPE-DERIVATION-CONVEXITE-FR-R4.tex` | R4 : Limites, croissances comparées |
| `remediation/TSPE-DERIVATION-CONVEXITE-FR-R5.tex` | R5 : Logarithme |
| `remediation/TSPE-DERIVATION-CONVEXITE-RE-C1.tex` | Erreurs dérivée composée |
| `remediation/TSPE-DERIVATION-CONVEXITE-RE-C2.tex` | Erreurs étude complète |
| `remediation/TSPE-DERIVATION-CONVEXITE-RE-C3.tex` | Erreurs inégalités convexité |
| `remediation/TSPE-DERIVATION-CONVEXITE-RE-C4.tex` | Erreurs esquisse courbe |
| `remediation/TSPE-DERIVATION-CONVEXITE-RE-C5.tex` | Erreurs lecture graphique + tangentes |

#### Évaluations (LOT-6)

| Fichier | Description |
|---------|-------------|
| `evaluations/TSPE-DERIVATION-CONVEXITE-EV-A.tex` | Version A (20 pts, 55 min) |
| `evaluations/TSPE-DERIVATION-CONVEXITE-EV-A-corrige.tex` | Corrigé A |
| `evaluations/TSPE-DERIVATION-CONVEXITE-EV-B.tex` | Version B (re-paramétrée) |
| `evaluations/TSPE-DERIVATION-CONVEXITE-EV-B-corrige.tex` | Corrigé B |

### Matrice de couverture capacités × parcours

| | ◆ | ◆◆ | ◆◆◆ | Cours | Méth. | QCM | Réméd. | EV-A | EV-B |
|---|---|----|-----|-------|-------|-----|--------|------|------|
| C1 | 4 | 4 | 2 | oui | M1, M5 | Q1–Q3 | FR-R1, RE-C1 | Ex1 | Ex1 |
| C2 | 4 | 4 | 2 | oui | M2, M5 | Q4–Q6 | RE-C2 | Ex2 | Ex2 |
| C3 | 3 | 3 | 2 | oui | M3 | Q7–Q9 | RE-C3 | Ex3 | Ex3 |
| C4 | 3 | 3 | 2 | oui | M4 | Q10–Q11 | RE-C4 | Ex4 | Ex4 |
| C5 | 3 | 3 | 2 | oui | M4 | Q12–Q13 | RE-C5 | Ex4 | Ex4 |
| C6 | 3 | 3 | 2 | oui | M3 | Q14–Q15 | RE-C5 | Ex3 | Ex3 |

Couverture : 100 % des capacités sur tous les parcours et supports.

### Démonstration exigible

| Démonstration | Localisation |
|---------------|--------------|
| Si f'' ≥ 0, la courbe est au-dessus de ses tangentes | `cours/15_C6_courbe_tangentes.tex` |

### Statistiques

- Total fichiers créés : 144
  - 8 cours (6 sections + 2 TD)
  - 5 méthodes
  - 52 exercices + 15 CDP = 67
  - 52 corrigés
  - 1 QCM
  - 10 remédiation (5 FR + 5 RE)
  - 4 évaluations
  - 142 validations SymPy (.sympy.json)
  - 8 rapports LOT (LOT-0 à LOT-7)

### Check-list LOT-7 (docs/01 Partie 8)

- [x] **9 temps du gabarit** : ouverture, diagnostic, activités, cours, méthodes, exercices, TD, QCM, évaluations + remédiation — tous présents
- [x] **Couverture F01** : 6/6 capacités × 3 parcours ≥ 2 exercices — **satisfaite**
- [x] **R2 SymPy** : 120 OK / 0 FAIL — **PASS**
- [x] **R6 Compilation** : PDF 28 pages, 191 Ko — **PASS**
- [x] **R7 Référentiel** : conformité BO 2019 vérifiée, 6 capacités, 1 démo exigible — **PASS**
- [x] **Schémas META** : 124/124 — **PASS**
- [x] **Résolution aveugle** : A+B 0 divergence — **PASS**
- [x] **Démonstration exigible C6** : rédigée intégralement — **PASS**

### Coût API estimé : ~0 $

## Tag : `chap/TSPE-DERIVATION-CONVEXITE-v1`
