# LOT 7 — Assemblage du chapitre 1SPE-SUITES

## PDF produits
- `build/1SPE-SUITES/1SPE-SUITES_complet.pdf` : 82 pages, 979 Ko
- `build/1SPE-SUITES/1SPE-SUITES_methodes.pdf` : declinaison methodes
- `build/1SPE-SUITES/1SPE-SUITES_remediation.pdf` : declinaison remediation

## Check-list qualite (docs/01 Partie 8)

- [x] 100% des capacites du programme officiel couvertes (C1-C7, rapport couverture F01 OK)
- [x] Chaque capacite possede : une methode, des exercices dans les 3 parcours, une question QCM, un item de remediation
- [x] Chaque prerequis teste au diagnostic possede sa fiche R (R1-R5)
- [x] Tous les exercices parcours 1 integralement corriges au standard copie modele
- [x] Chaque definition a un exemple et un contre-exemple ; chaque theoreme a ses hypotheses commentees
- [x] Au moins 3 erreurs frequentes documentees par chapitre (>10 au total)
- [x] Le chapitre est realisable en autonomie complete par un eleve moyen (structure gabarit respectee)
- [ ] Temps de travail estimes verifies sur eleves reels (A_VALIDER_HUMAIN)

## Verdicts globaux du chapitre
- SymPy (R2) : 102/102 OK
- Compilation (R6) : tous les .tex compilent individuellement et en assemblage
- Couverture (F01/F05) : complete
- Conformite (R1) : strates 1-2 conformes au referentiel
- Similarite (R3) : N/A (mode ex nihilo)

## Corrections cls apportees
- Ajout environnement `evaluation`
- Ajout package `eurosym`
- Fix `\margeAppui` (\itshape au lieu de \textit)

## Cout API estime total chapitre
- LOT 0-2 : ~0.5 $
- LOT 3 : ~3 $
- LOT 4 : ~8 $
- LOT 5 : ~4 $
- LOT 6 : ~4 $
- LOT 7 : ~0 $
- TOTAL : ~19.5 $ (sous le budget de 40 $)

## Addendum — Re-attestation du 16/07/2026

PDF recompile : **77 pages, 462 Ko** (contre 82 pages, 979 Ko au LOT-7 initial).

### Inventaire des objets (methode : comptage des `\input` dans le maitre)

| Objet | LOT | Attendu | Constate (maitre) | Constate (disque) |
|---|---|---:|---:|---:|
| Cours | 3 | 9 | 9 | 9 |
| Methodes | 3 | 7 | 7 | 7 |
| Exercices | 4 | 49 | 49 | 49 |
| Corriges | 4 | 49 | — (variante eleve) | 49 |
| QCM (21 questions) | 5 | 1 | 1 | 1 |
| Remediation | 5 | 12 | 12 | 12 |
| TD | 6 | 2 | 2 | 2 |
| Evaluations | 6 | 4 | 4 | 4 |

### Cause de l'ecart de pagination (82 -> 77)

La classe `nexus-manuel.cls` a ete restauree en v3.2 (commit `4ee186b`).
Les modifications qui impactent la pagination :
- Suppression de `\fontsize{9.5}{13.5}` et `\parskip{0.35em}` dans le `before upper`
  des tcolorbox : le baseline skip passe de 13.5pt a la valeur par defaut (~12pt),
  soit ~11% de gain d'espace vertical par ligne dans chaque encadre.
- `\nxboxtitle` : 8pt au lieu de 8.5pt (gain marginal).
- Padding tcolorbox : top/bottom passes de 6pt a 7pt (perte mineure, contrebalancee).

Aucun objet de contenu n'a ete ajoute ni supprime. Le rapport de couverture
et les verdicts SymPy restent inchanges (102/102 OK).

### Defaut constate

Le sous-titre de la page de couverture affiche « Manuel NSI Premiere » (code en dur
dans `nexus-manuel.cls:361`). A corriger par parametrage de la classe.

## Addendum — Recomposition charte v4.1 (16 juillet 2026)

Recomposition intégrale avec la charte v4.1 « Éditorial premium » :
polices Pagella/Heros, palette chapcolor indigo, géométrie kit (inner 2.0cm,
outer 4.8cm), encadrés onglet/cadre/filet, ouverture bandeau 56%.
**PDF 82 pages, 492 Ko**. Défaut sous-titre corrigé (v4 : `\matiere`/`\niveau`).
Inventaire inchangé (même maître, contenu identique).
