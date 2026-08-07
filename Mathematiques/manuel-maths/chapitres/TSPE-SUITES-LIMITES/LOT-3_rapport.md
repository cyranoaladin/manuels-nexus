# LOT-3 — Rapport de production : Cours + Methodes

## Chapitre : TSPE-SUITES-LIMITES

### Fichiers produits

| Fichier | Objet | Capacites |
|---------|-------|-----------|
| `cours/10_C1_convergence_divergence.tex` | Definitions formelles, operations sur les limites | C1 |
| `cours/11_C2_recurrence.tex` | Principe de recurrence, structure de redaction | C2 |
| `cours/12_C3_modelisation.tex` | Suites auxiliaires, modeles discrets, point fixe | C3 |
| `cours/13_C4_suite_croissante_non_majoree.tex` | Theoreme + demonstration exigible | C4 |
| `cours/14_C5_bernoulli_qn.tex` | Inegalite de Bernoulli + limite q^n (demonstrations exigibles) | C5 |
| `cours/15_C6_comparaison.tex` | Theoreme de comparaison + gendarmes (demonstrations exigibles) | C6 |
| `cours/16_C7_limites_exponentielle.tex` | Limites exp en +inf et -inf (demonstrations exigibles) | C7 |
| `cours/07_td_contextualise.tex` | TD: capital place a taux variable | C1, C3, C5, C6 |
| `cours/07_td_fil_rouge.tex` | TD fil rouge: etude complete d'une suite recurrente | C1-C7 |
| `methodes/TSPE-SUITLIM-ME-001.tex` | Determiner la limite d'une suite | C1 |
| `methodes/TSPE-SUITLIM-ME-002.tex` | Rediger une demonstration par recurrence | C2 |
| `methodes/TSPE-SUITLIM-ME-003.tex` | Etudier une suite arithmetico-geometrique | C3 |
| `methodes/TSPE-SUITLIM-ME-004.tex` | Monotonie/comparaison pour convergence/divergence | C4, C6 |
| `methodes/TSPE-SUITLIM-ME-005.tex` | Bernoulli et croissances comparees | C5, C7 |

### Demonstrations exigibles

- C4 : Suite croissante non majoree tend vers +inf (dans 13_C4)
- C5 : Inegalite de Bernoulli par recurrence + limite de q^n (dans 14_C5)
- C6 : Theoreme de comparaison + theoreme des gendarmes (dans 15_C6)
- C7 : Limites de l'exponentielle en +inf et -inf (dans 16_C7)

### Decisions

- Les TD contexualise et fil rouge contiennent des VERIFY blocks avec assertions SymPy.
- Le TD fil rouge couvre les 7 capacites via une suite recurrente u_{n+1} = (u_n+3)/(u_n+1).
- Piste Grand Oral proposee dans C3 (modelisation medicament).
- 5 fiches methodes couvrant M1-M5.

### Points ouverts

- Verification LaTeX (make check-latex) a effectuer.

## Audit de reprise — 2026-08-05 (branche `terminale/collection-v1`)

**Verification mathematique** (`make verify` / `scripts/verify_sympy.py --chap TSPE-SUITES-LIMITES`) :
116 [OK], 26 [REVIEW] (contenu non calculable : cours en prose, coups de pouce,
QCM — normal), **0 [FAIL]**.

Relecture manuelle des 4 demonstrations exigibles (C4, C5, C6, C7) contre le
programme BO : toutes correctes et rigoureuses (suite croissante non majoree ->
+infini ; inegalite de Bernoulli par recurrence + limite de $q^n$ par cas ;
theoreme de comparaison + gendarmes ; limites de l'exponentielle en +/-infini
et croissances comparees par l'inegalite $e^x \geq 1+x$). Aucune erreur
mathematique trouvee.

**R6 (compilation) — echec trouve et corrige.** `make chapter CHAP=TSPE-SUITES-LIMITES`
echouait (`NEXUS-MARGIN-ERROR:width`, 0 page produite) : 3 blocs `\margeAppui{}`
(dans `11_C2_recurrence.tex`, `12_C3_modelisation.tex`, `13_C4_suite_croissante_non_majoree.tex`)
depassaient la largeur de la colonne de marge geree par le solveur deterministe
(`gabarits/nexus-margin-shipout.lua`). Cause identifiee par bissection : un
`\margeAppui` contenant une liste (`itemize`/`enumerate`) ou plusieurs
paragraphes (ligne vide -> `\par`) produit un bloc que le solveur juge en
depassement, meme quand le texte tient visuellement dans la colonne. Un
`\margeAppui` en un seul paragraphe de prose passe systematiquement.

Correction appliquee : les 3 blocs reecrits en prose compacte mono-paragraphe,
contenu pedagogique inchange (mêmes methodes/mises en garde, juste reformulees
sans liste). Recompilation : succes, PDF 36 pages, 237 Ko, inspection visuelle
de 6 pages (aucune superposition, aucune collision).

**Point a signaler hors perimetre de ce chapitre** : ce bug (liste/multi-
paragraphe dans `\margeAppui` -> `NEXUS-MARGIN-ERROR:width`) est dans le
gabarit partage `gabarits/nexus-manuel.cls` / `nexus-margin-shipout.lua`, donc
potentiellement present dans d'autres chapitres (1SPE inclus) qui utiliseraient
le meme pattern. Non corrige a la source ici (modification du gabarit partage
hors perimetre LOT 3, impact Maths+NSI via `check_charte_sync.py`) : a traiter
comme ticket separe si confirme ailleurs.

**Statut LOT 3** : contenu mathematiquement verifie, compilation reparee et
verifiee visuellement. Propose pour validation humaine avant LOT 4.
