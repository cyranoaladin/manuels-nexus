# SPECIMEN A VALIDER --- Charte v3 edition professionnelle

PDF : `build/specimen.pdf` (5 pages, 55 Ko)
PNG : `build/specimen_page-{1..5}.png` (150 dpi)

## Changements v2 → v3

| Composant | v2 | v3 |
|---|---|---|
| Moteur | pdfLaTeX + inputenc/fontenc | **LuaLaTeX** + fontspec + unicode-math |
| Base | book | **KOMA-Script scrbook** (9.5pt, twoside) |
| Texte | Libertine (Type1) | **Libertinus Serif OTF** (9.5/13.5pt) embarquee |
| Maths | newtxmath | **Libertinus Math** (accord parfait texte/math) |
| Titres | Biolinum | **Montserrat** (SemiBold H1/H2, Medium encadres, petites capitales +40) |
| Code | listings generic | **JetBrains Mono** 8.5pt, ligatures desactivees, chiffres tabulaires |
| Microtype | basique | **protrusion + expansion** (plein support LuaTeX) |
| Grille | 20mm/45mm approx | **118mm texte + 46mm marge** (6mm gouttiere), 17mm int, 20/18mm haut/bas |
| Marge | marginnote basique | **Marge pedagogique** : Montserrat 7.5pt gris, filet vertical 0.4pt or |
| Encadres | tcolorbox cadres complets | **Filet gauche 2pt** + fond ≤5% + titre petites capitales espacees |
| Exercices | texte simple | **Bandeau colore** : numero en carre nxBleu plein blanc |
| Corriges | texte vert | **Bandeau nxVert** avec icone |
| Erreurs | paragraphe | Filet nxRouge + **copie fautive barree** + correction |
| Approfondissement | cadre bleu | **Fond nxBleu!6 SANS filet** |
| Listes | enumitem basique | **Compactes** (1pt itemsep), labels nxBleu |
| Espacements | bigskip/vspace | **Multiples de 4.5pt** (tiers de ligne) via tcbset/KOMA |
| En-tetes | fancyhdr | **scrlayer-scrpage** Montserrat 7.5pt gris |
| Tables | tabular | **booktabs** (pas de filets verticaux) |

## Polices embarquees (gabarits/fonts/, OFL)

- Libertinus Serif : Regular, Bold, Italic, BoldItalic (5 fichiers)
- Libertinus Math : Regular
- Montserrat : Regular, Medium, SemiBold, Bold, Thin, Italic, MediumItalic, SemiBoldItalic (8 fichiers)
- JetBrains Mono : Regular, Bold, Italic, BoldItalic (4 fichiers)
- 3 fichiers LICENSE-*.txt (OFL pour les 3 familles)

## Gate visuel

- 0 Overfull hbox > 2pt
- Pas de collision de marge observee
- Pas de veuves/orphelines (widowpenalty/clubpenalty 10000)
- Gris typographique homogene (microtype protrusion+expansion actif)

## Points de jugement humain

1. **Typographie** : l'accord Libertinus Serif/Math est-il satisfaisant ?
   La taille 9.5pt est-elle lisible ?

2. **Titres Montserrat** : le contraste serif/sans-serif est-il equilibre ?
   Les petites capitales espacees (+40/1000) sont-elles lisibles ?

3. **Code JetBrains Mono** : la taille 8.5pt est-elle suffisante ?
   La distinction code (filet gauche blanc) vs console (fond gris) est-elle claire ?

4. **Marge pedagogique** : le filet vertical or + texte Montserrat 7.5pt gris
   est-il lisible et esthetique ?

5. **Encadres** : le filet gauche 2pt sans cadre complet donne-t-il un rendu
   professionnel ? La hierarchie visuelle (bleu definitions, or methodes,
   rouge erreurs) est-elle claire ?

6. **Exercices** : le bandeau colore avec numero en carre blanc est-il
   trop present ou equilibre ?

7. **Grille** : la colonne texte 118mm + marge 46mm laisse-t-elle assez
   d'espace pour le contenu ?

## Decision requise

Cette charte v3 est une decision de marque. Valider avant :
- Migration des 3 chapitres maths existants
- Migration du pilote NSI
- Propagation via SYNC_CHARTE.md

Apres validation, les deux validations (specimen v3 + pilote NSI) seront
traitees ensemble pour reprendre le flux de production.
