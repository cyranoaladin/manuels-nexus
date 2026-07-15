# LOT 3bis — Charte graphique professionnelle (v2.0)

Date : 2026-07-15. Cout API estime : 0 $ (production locale). Mode : fichiers / ex nihilo.

## Livrable a : docs/06_charte_graphique.md

Specification complete en 9 sections :
1. Grille de page A4 avec marge pedagogique 3,6 cm
2. Hierarchie typographique H0-H3 (tailles, graisses, couleurs)
3. Palette Nexus 5 couleurs + regle des 2 couleurs vives + fonds <= 8 %
4. Systeme de pictogrammes (7 symboles, tous doubles d'un libelle)
5. Styles d'encadres (6 types, breakable, regle gauche 1.2pt, petites capitales)
6. Exercices et navigation (en-tete 4 elements, CDP separes, corriges copie-modele)
7. En-tetes/pieds professionnels (petites capitales, filet 0.4pt)
8. Page d'ouverture composee
9. Imprimabilite et accessibilite

## Livrable b : gabarits/nexus-manuel.cls v2.0

Ameliorations par rapport a v0.1 :
- `newtxmath` avec option `libertine` pour mathematiques assorties a Libertine
- `titletoc` pour sommaire style (chapitres bleus, sections retrait, points de conduite)
- `\subsubsection` (H3) formatee : 11/14pt, bleu 70% noir
- En-tetes en petites capitales grises (`\scshape\color{nxGris}`)
- Filet d'en-tete explicite 0.4pt
- `\ouverturechapitre` restructuree avec espacements verticaux calibres et titre 26/32pt

## Livrable c : Gate visuel

Compilation des 3 chapitres existants : PASS sans erreur.
- 1SPE-SUITES : 6 pages, 499 850 octets
- 1SPE-SECOND-DEGRE : 5 pages, 484 281 octets
- 1SPE-DERIVATION-LOCAL : 4 pages, 328 675 octets

Inspection PNG (pdftoppm -r 140) :
- Ouverture : titre 26pt bleu, capacites, carte grise, temps or. PASS.
- Page exercices/cours : encadres a regle gauche, fonds pastels, en-tete petites capitales. PASS.
- Aucun debordement, collision, encadre casse.

Detail dans `validations/charte.visual.json`.

## Exigences metier permanentes

- E5/F01 : >= 50 exercices par chapitre, >= 2 exercices par case capacite x parcours, ratio 40/40/20.
- Tout objet est autonome : corrige copie-modele 10-20 lignes, methode illustree, diagnostic QCM, CDP separes pour parcours 1.
- Parcours 1 = coups de pouce, parcours 2 = format examen, parcours 3 = prise d'initiative.
