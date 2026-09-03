# Graphe des consommateurs de la charte Nexus

Cartographie read-only des sources, assets et consommateurs. Aucun chemin n'est redirigé ou supprimé par ce rapport.

## Synthèse

- Assets physiques : **127**
- Contenus uniques : **64**
- Entrées de production non canoniques : **29**
- Consommateurs PDF finaux : **12**
- `.fls` finaux frais et attestés : **0**
- UNKNOWN lifecycle : **0**

## Entrées de production non canoniques

- `Mathematiques/manuel-maths/gabarits/chapitre_master.tex` — ACTIVE_BUILD_TEMPLATE — Le producteur de chapitre lit directement ce gabarit local. Preuve : `Mathematiques/manuel-maths/scripts/assemble.py:643`. Consommateurs : MATH_CHAPTER_BUILDER.
- `Mathematiques/manuel-maths/gabarits/logo_nexus.png` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-couverture.sty:124`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` — ACTIVE_COMPATIBILITY_WRAPPER — Le producteur de manuel charge explicitement le wrapper de charte local. Preuve : `Mathematiques/manuel-maths/scripts/assemble_manuel.py:1070`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-code.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:720`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:723`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:705`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-icons.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:701`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` — ACTIVE_COMPATIBILITY_WRAPPER — Le producteur de manuel charge explicitement le wrapper de classe local. Preuve : `Mathematiques/manuel-maths/scripts/assemble_manuel.py:1069`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` — ACTIVE_COMPATIBILITY_WRAPPER — Le gabarit de chapitre charge explicitement le wrapper de classe local. Preuve : `Mathematiques/manuel-maths/gabarits/chapitre_master.tex:2`. Consommateurs : MATH_CHAPTER_RUNTIME, MATH_LIVRET_RUNTIME.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua:41`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua:42`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:415`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex:49`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:716`. Consommateurs : 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur.
- `NSI/gabarits/book_master.tex` — ACTIVE_BUILD_TEMPLATE — Le producteur de manuel NSI lit directement ce gabarit local. Preuve : `NSI/scripts/assemble.py:455`. Consommateurs : NSI_BOOK_BUILDER.
- `NSI/gabarits/chapitre_master.tex` — ACTIVE_BUILD_TEMPLATE — Le producteur de chapitre lit directement ce gabarit local. Preuve : `NSI/scripts/assemble.py:550`. Consommateurs : NSI_CHAPTER_BUILDER.
- `NSI/gabarits/logo_nexus.png` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-couverture.sty:124`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-charte-v6.sty` — ACTIVE_COMPATIBILITY_WRAPPER — Le producteur de manuel charge explicitement le wrapper de charte local. Preuve : `NSI/gabarits/book_master.tex:3`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-code.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:720`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-figures-nsi.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:723`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-figures.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:705`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-icons.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:701`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-manuel-v5.cls` — ACTIVE_COMPATIBILITY_WRAPPER — Le producteur de manuel charge explicitement le wrapper de classe local. Preuve : `NSI/gabarits/book_master.tex:2`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-manuel.cls` — ACTIVE_COMPATIBILITY_WRAPPER — Le gabarit de chapitre charge explicitement le wrapper de classe local. Preuve : `NSI/gabarits/chapitre_master.tex:2`. Consommateurs : NSI_CHAPTER_RUNTIME.
- `NSI/gabarits/nexus-margin-json.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `NSI/gabarits/nexus-margin-shipout.lua:41`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-margin-layout.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `NSI/gabarits/nexus-margin-shipout.lua:42`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-margin-rail.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:415`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-margin-shipout.lua` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `NSI/gabarits/nexus-margin-rail.tex:49`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.
- `NSI/gabarits/nexus-signatures.tex` — ACTIVE_PROJECT_LOCAL_RUNTIME — La résolution relative au répertoire projet sélectionne cet asset local pendant les builds de la famille concernée. Preuve : `gabarits/common/nexus-manuel.cls:716`. Consommateurs : 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur.

## Réconciliation avec la métrique historique des 16 chemins

- Confirmés production : **15**
- Faux positif de référence : **1**
- Entrées production désormais explicites : **14**

- Référence seule : `NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty`

## Ensembles de cycle de vie

### ACTIVE_BUILD_TEMPLATE

- `Mathematiques/manuel-maths/gabarits/chapitre_master.tex`
- `NSI/gabarits/book_master.tex`
- `NSI/gabarits/chapitre_master.tex`

### ACTIVE_COMPATIBILITY_WRAPPER

- `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`
- `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`
- `NSI/gabarits/nexus-charte-v6.sty`
- `NSI/gabarits/nexus-manuel-v5.cls`
- `NSI/gabarits/nexus-manuel.cls`

### ACTIVE_LOCAL_RUNTIME

- `Mathematiques/manuel-maths/gabarits/logo_nexus.png`
- `Mathematiques/manuel-maths/gabarits/nexus-code.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-figures.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-icons.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua`
- `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua`
- `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`
- `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua`
- `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex`
- `NSI/gabarits/logo_nexus.png`
- `NSI/gabarits/nexus-code.tex`
- `NSI/gabarits/nexus-figures-nsi.tex`
- `NSI/gabarits/nexus-figures.tex`
- `NSI/gabarits/nexus-icons.tex`
- `NSI/gabarits/nexus-margin-json.lua`
- `NSI/gabarits/nexus-margin-layout.lua`
- `NSI/gabarits/nexus-margin-rail.tex`
- `NSI/gabarits/nexus-margin-shipout.lua`
- `NSI/gabarits/nexus-signatures.tex`

### ACTIVE_TOOL_TEMPLATE

- `Mathematiques/manuel-maths/gabarits/objet_standalone.tex`
- `NSI/gabarits/objet_standalone.tex`

### CANONICAL_SOURCE

- `gabarits/common/chapitre_master.tex`
- `gabarits/common/fonts/JetBrainsMono-Bold.otf`
- `gabarits/common/fonts/JetBrainsMono-BoldItalic.otf`
- `gabarits/common/fonts/JetBrainsMono-Italic.otf`
- `gabarits/common/fonts/JetBrainsMono-Regular.otf`
- `gabarits/common/fonts/LibertinusMath-Regular.otf`
- `gabarits/common/fonts/LibertinusSerif-Bold.otf`
- `gabarits/common/fonts/LibertinusSerif-BoldItalic.otf`
- `gabarits/common/fonts/LibertinusSerif-Italic.otf`
- `gabarits/common/fonts/LibertinusSerif-Regular.otf`
- `gabarits/common/fonts/Montserrat-Bold.otf`
- `gabarits/common/fonts/Montserrat-Italic.otf`
- `gabarits/common/fonts/Montserrat-Medium.otf`
- `gabarits/common/fonts/Montserrat-MediumItalic.otf`
- `gabarits/common/fonts/Montserrat-Regular.otf`
- `gabarits/common/fonts/Montserrat-SemiBold.otf`
- `gabarits/common/fonts/Montserrat-SemiBoldItalic.otf`
- `gabarits/common/fonts/Montserrat-Thin.otf`
- `gabarits/common/logo_nexus.png`
- `gabarits/common/nexus-arbres.sty`
- `gabarits/common/nexus-boites.sty`
- `gabarits/common/nexus-charte.sty`
- `gabarits/common/nexus-code.tex`
- `gabarits/common/nexus-couverture.sty`
- `gabarits/common/nexus-decor.sty`
- `gabarits/common/nexus-exercices.sty`
- `gabarits/common/nexus-figures-bib.sty`
- `gabarits/common/nexus-icons.tex`
- `gabarits/common/nexus-manuel.cls`
- `gabarits/common/nexus-margin-json.lua`
- `gabarits/common/nexus-margin-layout.lua`
- `gabarits/common/nexus-margin-rail.tex`
- `gabarits/common/nexus-margin-shipout.lua`
- `gabarits/common/nexus-pages-froides.sty`
- `gabarits/common/nexus-pont.sty`
- `gabarits/common/nexus-signatures.tex`
- `gabarits/maths/nexus-maths.sty`
- `gabarits/nsi/nexus-nsi.sty`

### DORMANT_COMPATIBILITY_WRAPPER

- `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-decor.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty`
- `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty`
- `NSI/gabarits/nexus-boites-v6.sty`
- `NSI/gabarits/nexus-couverture.sty`
- `NSI/gabarits/nexus-decor.sty`
- `NSI/gabarits/nexus-exercices-v6.sty`
- `NSI/gabarits/nexus-figures-bib.sty`
- `NSI/gabarits/nexus-pages-froides.sty`
- `NSI/gabarits/nexus-pont-v6.sty`

### DORMANT_FONT_SOURCE

- `Mathematiques/manuel-maths/gabarits/fonts/LibertinusMath-Regular.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Bold.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-BoldItalic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Italic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Regular.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Bold.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Italic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Medium.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-MediumItalic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Regular.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-SemiBold.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-SemiBoldItalic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Thin.otf`
- `NSI/gabarits/fonts/LibertinusMath-Regular.otf`
- `NSI/gabarits/fonts/LibertinusSerif-Bold.otf`
- `NSI/gabarits/fonts/LibertinusSerif-BoldItalic.otf`
- `NSI/gabarits/fonts/LibertinusSerif-Italic.otf`
- `NSI/gabarits/fonts/LibertinusSerif-Regular.otf`
- `NSI/gabarits/fonts/Montserrat-Bold.otf`
- `NSI/gabarits/fonts/Montserrat-Italic.otf`
- `NSI/gabarits/fonts/Montserrat-Medium.otf`
- `NSI/gabarits/fonts/Montserrat-MediumItalic.otf`
- `NSI/gabarits/fonts/Montserrat-Regular.otf`
- `NSI/gabarits/fonts/Montserrat-SemiBold.otf`
- `NSI/gabarits/fonts/Montserrat-SemiBoldItalic.otf`
- `NSI/gabarits/fonts/Montserrat-Thin.otf`

### FONT_PROVISION_SOURCE

- `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Bold.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-BoldItalic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Italic.otf`
- `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Regular.otf`
- `NSI/gabarits/fonts/JetBrainsMono-Bold.otf`
- `NSI/gabarits/fonts/JetBrainsMono-BoldItalic.otf`
- `NSI/gabarits/fonts/JetBrainsMono-Italic.otf`
- `NSI/gabarits/fonts/JetBrainsMono-Regular.otf`

### HISTORICAL_ONLY

- `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-nsi.tex`
- `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-physique.tex`
- `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-suites.tex`
- `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/main.tex`
- `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/manuel.sty`

### OBSOLETE_PROVED

Aucun.

### REFERENCE_ONLY

- `NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty`

### VISUAL_FIXTURE

- `Mathematiques/manuel-maths/gabarits/specimen-pont-v6.tex`
- `Mathematiques/manuel-maths/gabarits/specimen-v6.tex`
- `Mathematiques/manuel-maths/gabarits/specimen.tex`
- `NSI/gabarits/specimen.tex`

## Assets

| Chemin | Rôle | Lifecycle | Runtime | Canonique | Consommateurs |
|---|---|---|:---:|---|---|
| `Mathematiques/manuel-maths/gabarits/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | ACTIVE_BUILD_TEMPLATE | NO | `gabarits/common/chapitre_master.tex` | MATH_CHAPTER_BUILDER |
| `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Bold.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Bold.otf` | MATH_FONT_PROVISIONING |
| `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-BoldItalic.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-BoldItalic.otf` | MATH_FONT_PROVISIONING |
| `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Italic.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Italic.otf` | MATH_FONT_PROVISIONING |
| `Mathematiques/manuel-maths/gabarits/fonts/JetBrainsMono-Regular.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Regular.otf` | MATH_FONT_PROVISIONING |
| `Mathematiques/manuel-maths/gabarits/fonts/LibertinusMath-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusMath-Regular.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Bold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Bold.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-BoldItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-BoldItalic.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Italic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Italic.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/LibertinusSerif-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Regular.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Bold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Bold.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Italic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Italic.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Medium.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Medium.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-MediumItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-MediumItalic.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Regular.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-SemiBold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBold.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-SemiBoldItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBoldItalic.otf` | — |
| `Mathematiques/manuel-maths/gabarits/fonts/Montserrat-Thin.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Thin.otf` | — |
| `Mathematiques/manuel-maths/gabarits/logo_nexus.png` | LOGO_ASSET | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/logo_nexus.png` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-boites.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-charte.sty` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-code.tex` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-couverture.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-decor.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-exercices.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-figures-bib.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/nsi/nexus-nsi.sty` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/maths/nexus-maths.sty` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-icons.tex` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-manuel.cls` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-manuel.cls` | MATH_CHAPTER_RUNTIME, MATH_LIVRET_RUNTIME |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-json.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-json.lua` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-layout.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-layout.lua` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-rail.tex` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-shipout.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-shipout.lua` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-pages-froides.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-pont.sty` | — |
| `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-signatures.tex` | 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TSPE:eleve, TSPE:professeur |
| `Mathematiques/manuel-maths/gabarits/objet_standalone.tex` | OBJECT_RUNTIME_TEMPLATE | ACTIVE_TOOL_TEMPLATE | NO | — | MATH_MCP_OBJECT_COMPILER |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-nsi.tex` | HISTORICAL_REFERENCE | HISTORICAL_ONLY | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-physique.tex` | HISTORICAL_REFERENCE | HISTORICAL_ONLY | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-suites.tex` | HISTORICAL_REFERENCE | HISTORICAL_ONLY | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/main.tex` | HISTORICAL_REFERENCE | HISTORICAL_ONLY | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/manuel.sty` | HISTORICAL_REFERENCE | HISTORICAL_ONLY | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/specimen-pont-v6.tex` | VISUAL_SPECIMEN_TEMPLATE | VISUAL_FIXTURE | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/specimen-v6.tex` | VISUAL_SPECIMEN_TEMPLATE | VISUAL_FIXTURE | NO | — | — |
| `Mathematiques/manuel-maths/gabarits/specimen.tex` | VISUAL_SPECIMEN_TEMPLATE | VISUAL_FIXTURE | NO | — | — |
| `NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty` | REFERENCE_MODEL_STYLE | REFERENCE_ONLY | NO | — | NSI_REFERENCE_CORPUS_P13 |
| `NSI/gabarits/book_master.tex` | BOOK_RUNTIME_TEMPLATE | ACTIVE_BUILD_TEMPLATE | NO | — | NSI_BOOK_BUILDER |
| `NSI/gabarits/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | ACTIVE_BUILD_TEMPLATE | NO | — | NSI_CHAPTER_BUILDER |
| `NSI/gabarits/fonts/JetBrainsMono-Bold.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Bold.otf` | NSI_FONT_PROVISIONING |
| `NSI/gabarits/fonts/JetBrainsMono-BoldItalic.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-BoldItalic.otf` | NSI_FONT_PROVISIONING |
| `NSI/gabarits/fonts/JetBrainsMono-Italic.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Italic.otf` | NSI_FONT_PROVISIONING |
| `NSI/gabarits/fonts/JetBrainsMono-Regular.otf` | FONT_BINARY | FONT_PROVISION_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Regular.otf` | NSI_FONT_PROVISIONING |
| `NSI/gabarits/fonts/LibertinusMath-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusMath-Regular.otf` | — |
| `NSI/gabarits/fonts/LibertinusSerif-Bold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Bold.otf` | — |
| `NSI/gabarits/fonts/LibertinusSerif-BoldItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-BoldItalic.otf` | — |
| `NSI/gabarits/fonts/LibertinusSerif-Italic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Italic.otf` | — |
| `NSI/gabarits/fonts/LibertinusSerif-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Regular.otf` | — |
| `NSI/gabarits/fonts/Montserrat-Bold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Bold.otf` | — |
| `NSI/gabarits/fonts/Montserrat-Italic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Italic.otf` | — |
| `NSI/gabarits/fonts/Montserrat-Medium.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Medium.otf` | — |
| `NSI/gabarits/fonts/Montserrat-MediumItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-MediumItalic.otf` | — |
| `NSI/gabarits/fonts/Montserrat-Regular.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Regular.otf` | — |
| `NSI/gabarits/fonts/Montserrat-SemiBold.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBold.otf` | — |
| `NSI/gabarits/fonts/Montserrat-SemiBoldItalic.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBoldItalic.otf` | — |
| `NSI/gabarits/fonts/Montserrat-Thin.otf` | FONT_BINARY | DORMANT_FONT_SOURCE | NO | `gabarits/common/fonts/Montserrat-Thin.otf` | — |
| `NSI/gabarits/logo_nexus.png` | LOGO_ASSET | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/logo_nexus.png` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-boites.sty` | — |
| `NSI/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-charte.sty` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-code.tex` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-couverture.sty` | — |
| `NSI/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-decor.sty` | — |
| `NSI/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-exercices.sty` | — |
| `NSI/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-figures-bib.sty` | — |
| `NSI/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/nsi/nexus-nsi.sty` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/maths/nexus-maths.sty` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-icons.tex` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-manuel.cls` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | ACTIVE_COMPATIBILITY_WRAPPER | YES | `gabarits/common/nexus-manuel.cls` | NSI_CHAPTER_RUNTIME |
| `NSI/gabarits/nexus-margin-json.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-json.lua` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-margin-layout.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-layout.lua` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-rail.tex` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-margin-shipout.lua` | RUNTIME_LUA_MODULE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-margin-shipout.lua` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-pages-froides.sty` | — |
| `NSI/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | DORMANT_COMPATIBILITY_WRAPPER | NO | `gabarits/common/nexus-pont.sty` | — |
| `NSI/gabarits/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | ACTIVE_LOCAL_RUNTIME | YES | `gabarits/common/nexus-signatures.tex` | 1NSI:eleve, 1NSI:professeur, TNSI:eleve, TNSI:professeur |
| `NSI/gabarits/objet_standalone.tex` | OBJECT_RUNTIME_TEMPLATE | ACTIVE_TOOL_TEMPLATE | NO | — | NSI_MCP_OBJECT_COMPILER |
| `NSI/gabarits/specimen.tex` | VISUAL_SPECIMEN_TEMPLATE | VISUAL_FIXTURE | NO | — | — |
| `gabarits/common/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | CANONICAL_SOURCE | NO | `gabarits/common/chapitre_master.tex` | — |
| `gabarits/common/fonts/JetBrainsMono-Bold.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Bold.otf` | — |
| `gabarits/common/fonts/JetBrainsMono-BoldItalic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-BoldItalic.otf` | — |
| `gabarits/common/fonts/JetBrainsMono-Italic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Italic.otf` | — |
| `gabarits/common/fonts/JetBrainsMono-Regular.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/JetBrainsMono-Regular.otf` | — |
| `gabarits/common/fonts/LibertinusMath-Regular.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/LibertinusMath-Regular.otf` | — |
| `gabarits/common/fonts/LibertinusSerif-Bold.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Bold.otf` | — |
| `gabarits/common/fonts/LibertinusSerif-BoldItalic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-BoldItalic.otf` | — |
| `gabarits/common/fonts/LibertinusSerif-Italic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Italic.otf` | — |
| `gabarits/common/fonts/LibertinusSerif-Regular.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/LibertinusSerif-Regular.otf` | — |
| `gabarits/common/fonts/Montserrat-Bold.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-Bold.otf` | — |
| `gabarits/common/fonts/Montserrat-Italic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-Italic.otf` | — |
| `gabarits/common/fonts/Montserrat-Medium.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-Medium.otf` | — |
| `gabarits/common/fonts/Montserrat-MediumItalic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-MediumItalic.otf` | — |
| `gabarits/common/fonts/Montserrat-Regular.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-Regular.otf` | — |
| `gabarits/common/fonts/Montserrat-SemiBold.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBold.otf` | — |
| `gabarits/common/fonts/Montserrat-SemiBoldItalic.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-SemiBoldItalic.otf` | — |
| `gabarits/common/fonts/Montserrat-Thin.otf` | FONT_BINARY | CANONICAL_SOURCE | NO | `gabarits/common/fonts/Montserrat-Thin.otf` | — |
| `gabarits/common/logo_nexus.png` | LOGO_ASSET | CANONICAL_SOURCE | NO | `gabarits/common/logo_nexus.png` | — |
| `gabarits/common/nexus-arbres.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-arbres.sty` | — |
| `gabarits/common/nexus-boites.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-boites.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-charte.sty` | CANONICAL_STYLE_IMPLEMENTATION | CANONICAL_SOURCE | YES | `gabarits/common/nexus-charte.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-code.tex` | — |
| `gabarits/common/nexus-couverture.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-couverture.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-decor.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-decor.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-exercices.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-exercices.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-figures-bib.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-figures-bib.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-icons.tex` | — |
| `gabarits/common/nexus-manuel.cls` | CANONICAL_CLASS_IMPLEMENTATION | CANONICAL_SOURCE | YES | `gabarits/common/nexus-manuel.cls` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, MATH_CHAPTER_RUNTIME, MATH_LIVRET_RUNTIME, NSI_CHAPTER_RUNTIME, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-margin-json.lua` | RUNTIME_LUA_MODULE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-margin-json.lua` | — |
| `gabarits/common/nexus-margin-layout.lua` | RUNTIME_LUA_MODULE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-margin-layout.lua` | — |
| `gabarits/common/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-margin-rail.tex` | — |
| `gabarits/common/nexus-margin-shipout.lua` | RUNTIME_LUA_MODULE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-margin-shipout.lua` | — |
| `gabarits/common/nexus-pages-froides.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-pages-froides.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-pont.sty` | CANONICAL_SUPPORT_STYLE | CANONICAL_SOURCE | YES | `gabarits/common/nexus-pont.sty` | 1NSI:eleve, 1NSI:professeur, 1SPE:eleve, 1SPE:professeur, TCOMPL:eleve, TCOMPL:professeur, TEXPERTES:eleve, TEXPERTES:professeur, TNSI:eleve, TNSI:professeur, TSPE:eleve, TSPE:professeur |
| `gabarits/common/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | CANONICAL_SOURCE | NO | `gabarits/common/nexus-signatures.tex` | — |
| `gabarits/maths/nexus-maths.sty` | CANONICAL_DISCIPLINE_ADAPTER | CANONICAL_SOURCE | NO | `gabarits/maths/nexus-maths.sty` | — |
| `gabarits/nsi/nexus-nsi.sty` | CANONICAL_DISCIPLINE_ADAPTER | CANONICAL_SOURCE | NO | `gabarits/nsi/nexus-nsi.sty` | — |
