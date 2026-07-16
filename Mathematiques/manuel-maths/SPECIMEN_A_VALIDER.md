# SPECIMEN A VALIDER --- Charte v3.1 edition professionnelle

PDF : `build/specimen.pdf` (5 pages, 69 Ko, 0 overfull hbox)
PNG : `build/specimen_page-{1..5}.png` (150 dpi)

## Corrections v3.0 → v3.1

| Defaut v3.0 | Correction v3.1 |
|---|---|
| Titres d'encadres : barre pleine, « Pour aller plus loin » illisible | detach title : texte petites capitales de la couleur du filet, pose sur le fond, sans barre |
| Ouverture de chapitre : pages blanches, pas d'ouverture composee | Pleine page TikZ overlay : fond nxBleu, numero Montserrat Thin 90pt blanc, titre 26pt. Page contrat separee |
| Numerotation « 0.1 » en en-tete | refstepcounter{chapter} + chaptermark dans ouverturechapitre. Sections numerotees 1.1, 1.2 |
| Pied de page : chiffre centre nu | Pave nxBleu coin exterieur + « Nexus Reussite » petites capitales cote interieur |
| Code : espaces parasites, guillemets courbes | lstset global columns=fullflexible, keepspaces, breaklines. lstinline protege de babel NoAutoSpacing |
| QCM : diagnostics a cote des options (revele la reponse) | Options propres (A/B/C sans annotation). Diagnostics dans fichier separe (QCM-DIAG.tex) |
| 22 overfull hbox dans le pilote | 0 overfull (breaklines + reformulations lstinline longs) |
| ID/duree dans le bandeau exercice (pollution visuelle) | Metadata deportees en marge (ID + duree en Montserrat 6.5pt gris) |

## Contenu du specimen (5 pages)

1. Ouverture pleine page bleu + page contrat
2. Cours : definition D1, theoreme (deballage), erreur frequente (copie fautive barree), figure pgfplots, approfondissement, 2 appuis de marge
3. Fiche methode M1 complete (6 rubriques)
4. Exercices 3 parcours (bandeaux, metadata en marge) + corriges avec commentaire de marge
5. Code NSI (codereference en boite, python, console, memtable, arbre TikZ) + mini-projet en boite or + QCM nouvelle formule

## Gates

- 0 Overfull hbox > 2pt
- 170 tests passes (dont regression QCM diagnostic adjacent)
- lot-gates ALL PASSED sur le pilote (verify 0 fail, accents OK, gates-corpus-strict VERT)
- Pilote 0 overfull, 211 Ko

## Decision requise

Valider la charte v3.1 avant migration des chapitres existants.
Les deux validations (specimen v3.1 + pilote NSI) sont traitees ensemble.
