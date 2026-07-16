# SPECIMEN A VALIDER --- Charte v4.1 « Éditorial premium »

Date : 16 juillet 2026.

## Changement v3 → v4.1

Transposition complète du kit v2 `gabarits/reference-v4/manuel-kit/` dans la
classe `nexus-manuel.cls`. Aucun fichier `.tex` de chapitre modifié.

## Blocs réalisés

| Bloc | Statut | Détail |
|---|---|---|
| H.1 Typographie | **Fait** | TeX Gyre Pagella (corps + maths, interligne 1.06), TeX Gyre Heros (titres, scaled 0.94), JetBrains Mono (code). `pdffonts` : toutes embarquées (emb=yes, sub=yes). |
| H.2 Palette | **Fait** | encre #16233B, mathsAccent #3A2BD4, nsiAccent #0E9E6E, coulRetenir #F5484B (corail), coulHistoire #8A6D3B (sépia), coulCode #1E293B (ardoise), grisdoux #F2F1EC. `\matiere` fixe chapcolor. Alias v3 conservés. |
| H.3 Ouvertures | **Fait** | Bandeau chapcolor 56% page, numéro géant fantôme 210pt, étiquette matière·niveau, titre 34pt. Décors TikZ géométriques : spirale (Suites), paraboles (Second degré), sécantes→tangente (Dérivation), grille binaire (Types construits). |
| H.4 Géométrie | **Fait** | inner=2.0cm, outer=4.8cm, marginparwidth=3.5cm. Encadrés kit v2 : nxdef=onglet plein+fond teinté+barre, nxthm=cadre+bandeau, nxprop=filet gauche, fmbox=onglet contour, nxerr=corail. Exercices : badge arrondi chapcolor. Code : keywords chapcolor, fond grisdoux. `\vocab{}{}`, `\code{}` ajoutés. |
| H.5 Gate visuel | **Fait** | 5 cibles compilées, 6 PNG inspectés, tests 411+214 pass (5 échecs retrieval pré-existants). |

## Gate visuel — 5 cibles compilées

| Cible | Pages | Ko | Verdict |
|---|---:|---:|---|
| 1SPE-SUITES | 82 | 492 | PASS |
| 1SPE-SECOND-DEGRE | 65 | 369 | PASS |
| 1SPE-DERIVATION-LOCAL | 39 | 253 | PASS |
| 1NSI-TYPES-CONSTRUITS | 36 | 231 | PASS |
| Spécimen maths | 4 | 70 | PASS |

## PNG inspectés (150 dpi, `validations/v41/`)

| Page | Accents | Encadrés kit | Losanges | Overfull | Verdict |
|---|---|---|---|---|---|
| DERLOCAL ouverture (p.1) | OK | Bandeau indigo, n° géant, titre blanc | — | 0 | PASS |
| DERLOCAL cours (p.3) | OK | nxdef onglet plein, nxthm cadre+bandeau | — | 0 | PASS |
| DERLOCAL exo (p.15) | OK | Badge arrondi indigo | ◆ à l'accent | 0 | PASS |
| SUITES ouverture (p.1) | OK | Bandeau indigo, spirale d'or | — | 0 | PASS |
| SUITES cours (p.3) | OK | nxdef, nxprop filet gauche | — | 0 | PASS |
| SUITES corrigé (p.30) | OK | Badge corrigé arrondi | — | 0 | PASS |

## Tests

- `make test` maths : 411 passed, 5 failed (test_retrieval pré-existant)
- `make test` NSI : 214 passed
- Sync gabarits : 4/4 fichiers identiques (cls, signatures, icons, figures)

## Arbitrages A_VALIDER_HUMAIN

1. **`\logonexus`** : aucun fichier logo fourni (`gabarits/assets/logo_nexus.*` absent). Repli textuel « NEXUS RÉUSSITE » en pied. Déposer le fichier pour intégration.
2. **Polices** : les TeX Gyre sont système (/usr/share/texmf/). Si la CI n'a pas `texlive-fonts-recommended`, ajouter à l'apt du workflow.

## Comparatif avant/après (mêmes pages)

| Page | v3.2 (avant) | v4.1 (après) |
|---|---|---|
| Ouverture | Fond nxBleu plein, n° Montserrat Thin haut droit | Bandeau 56% chapcolor, n° géant fantôme, décor TikZ |
| Cours | Filet bleu, titre section noir | Onglet plein accent, filet gauche chapcolor, cadre contour théorèmes |
| Exercices | Pavé rectangulaire nxBleu | Badge arrondi chapcolor, losanges à l'accent |
| Pied de page | Pavé rectangulaire nxBleu | Pastille ronde chapcolor |
| Polices | Libertinus + Montserrat | Pagella + Heros (chaleureux, contrasté) |
| Marges | 17mm inner, 118mm texte | 2.0cm inner, 4.8cm outer (notes marginales larges) |

## Décision requise

Valider la charte v4.1 « Éditorial premium ».
Pause non bloquante : la production reprend immédiatement.
