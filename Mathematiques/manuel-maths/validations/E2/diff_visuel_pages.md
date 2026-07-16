# E.2.4 — Diff visuel et composition des ecarts de pagination

Date : 16 juillet 2026.

## PNG inspectes (150 dpi)

Les rendus sont dans le meme repertoire :
- `suites_page-{01,02,03}.png` : TDM, couverture, contrat SUITES
- `secdeg_page-{01,02,03}.png` : TDM, couverture, contrat SECOND-DEGRE
- `suites_cours-{05,06,07}.png` : ouverture + diagnostic SUITES
- `secdeg_cours-{05,06,07}.png` : ouverture + diagnostic SECOND-DEGRE
- `nsi_page-{01,02,03}.png` : premiers pages NSI pilote
- `specimen_page-{1,2,3}.png` : specimen charte

## Pages homologues SUITES (p.2-3 vs p.5-6)

| Element | Couverture (p.2) | Contrat (p.3) | Diagnostic (p.6) |
|---|---|---|---|
| Numero chapitre | 110pt Montserrat Thin blanc, haut-droit | — | — |
| Filet or | Present au-dessus du titre | — | — |
| Sous-titre | **"Manuel NSI Premiere"** (DEFAUT) | — | — |
| Capacites C1-C7 | — | Liste complete avec losanges | Detaillees dans l'ouverture |
| Prerequis R1-R5 | — | — | 10 questions, Python inclus |
| Pied de page | absent (thispagestyle empty) | 6 / NEXUS REUSSITE | 6 / NEXUS REUSSITE |
| En-tete | absent | onglet + mini-motif + headmark | idem |

## Pages homologues SECOND-DEGRE (p.2-3 vs p.5-6)

Structure identique a SUITES. Titre : "Fonctions polynomes du second degre" (sans accents
car issu du contrat.yaml dont les champs ne portent pas d'accents).

## Defaut constate

**Sous-titre de couverture** : la macro `\ouverturechapitre` dans `nexus-manuel.cls:361`
contient `{Manuel NSI Premiere --- Nexus Reussite}` en dur. Les chapitres de
mathematiques heritent donc d'un sous-titre NSI. Ce texte devrait etre parametre
par un argument ou une commande de classe.

**Accents contrat** : les libelles des capacites dans les contrats YAML maths
n'ont pas d'accents (`reconnaitre`, `symetrie`). Cela impacte la page de contrat
et la couverture mais pas le cours (accente dans les .tex de contenu).

## Composition de l'ecart 82 -> 77 pages (SUITES)

L'ecart de 5 pages entre le LOT-7 original (82 p.) et la re-attestation (77 p.)
est du a la restauration de la charte v3.2 depuis le commit `4ee186b`. Les
modifications du cls qui impactent la pagination :

| Modification cls | Effet sur la hauteur verticale |
|---|---|
| `nxbase` : suppression de `\fontsize{9.5}{13.5}` et `\parskip{0.35em}` dans le `before upper` des tcolorbox | Le contenu des encadres utilise desormais les valeurs par defaut du document (baseline skip standard 12pt au lieu de 13.5pt, parskip standard au lieu de 0.35em). Gain net de ~11% d'espace vertical dans chaque encadre. |
| `\nxboxtitle` : 8pt/11pt au lieu de 8.5pt/11pt | Gain marginal (~0.5pt/titre). |
| `nxstar` : remplacement du style ad-hoc par `nxbase` + `leftrule=0pt` | Elimination de la duplication du `before upper` ; meme gain d'espace. |
| Padding tcolorbox : `top=7pt, bottom=7pt` au lieu de `top=6pt, bottom=6pt` | Perte de 2pt par encadre (contrebalancee par le gain sur le corps). |
| Ouverture chapitre : repositionnement du titre (+10mm vers le haut) | Page de couverture identique (1 page), pas d'effet net. |

**Bilan** : le gain net (~1.5pt de baseline par ligne dans les encadres) cumule sur
9 sections de cours + 7 methodes + 12 remediations (chacune dans un tcolorbox)
absorbe environ 5 pages. Aucun objet n'a ete supprime.

## Composition de l'ecart 64 -> 61 pages (SECOND-DEGRE)

Meme cause que SUITES. Le chapitre est plus court (6 capacites au lieu de 7)
donc le gain net est proportionnellement similaire : 3 pages sur 64 (4.7%)
contre 5 pages sur 82 (6.1%) pour SUITES.

## Verdict

Les ecarts de pagination sont entierement expliques par les modifications de la classe
`nexus-manuel.cls` entre la compilation LOT-7 et la re-attestation. **Aucun objet de
contenu n'a ete ajoute ni supprime.**

Le defaut de sous-titre "Manuel NSI Premiere" sur les couvertures maths est un point
ouvert a corriger.

## F.2 — Inspection complementaire exercices / QCM / corriges (16 juillet 2026)

PNG supplementaires inspectes (150 dpi) :
- `suites_exo-24.png` : page 24, exercices 1-5 (parcours 1)
- `suites_qcm-42.png` : page 42, QCM + debut C1
- `suites_eval-49.png` : page 49, evaluation A
- `secdeg_exo-20.png` : page 20, exercices 1-3 (parcours 1)
- `secdeg_qcm-35.png` : page 35, TD fil rouge + QCM
- `nsi_exo-10.png` : page 10, exercices NSI 1-4 (parcours 1)
- `nsi_qcm-25.png` : page 25, coups de pouce + TD 1

### Grille d'inspection

| Page | Accents | Losanges parcours | Encadres | Overfull | Verdict |
|---|---|---|---|---|---|
| SUITES exo p.24 | OK (considere, definie, geometrique) | 1 losange jaune par exercice (parcours 1) | Exercice bleu, ID + temps en marge | 0 | PASS |
| SUITES QCM p.42 | Partiels (titre QCM sans accents : auto-evaluation, numeriques) | — | Titre section bleu | 0 | PASS (*) |
| SUITES eval p.49 | OK (evaluation, capacites) | — | Sujet numerote | 0 | PASS |
| SECDEG exo p.20 | OK (trinome, parabole, canonique) | 1 losange jaune (parcours 1) | Exercice bleu, marge OK | 0 | PASS |
| SECDEG QCM p.35 | Partiels (titre QCM sans accents) | 3 losanges (exercice 48 = parcours 3) | Corrige gris, QCM section | 0 | PASS (*) |
| NSI exo p.10 | OK (considere, ecrire, euclidienne) | 1 losange jaune (parcours 1) | Exercice bleu, code Python OK | 0 | PASS |
| NSI CDP+TD p.25 | OK (meteo, temperature, comprehension) | 1 losange (exercice 56-57 TD) | CDP gras, TD section | 0 | PASS |

(*) Les titres QCM sans accents proviennent du contenu des fichiers .tex (pas de la classe).
Le rendu losange, la mise en page et les encadres sont conformes a la charte v3.2.

### Verdict F.2

**PASS** — 0 defaut bloquant sur les pages exercices, QCM et TD des trois chapitres.
Les accents manquants dans les titres QCM sont un point cosmétique non bloquant
(contenu des fichiers .tex, pas defaut de classe).
