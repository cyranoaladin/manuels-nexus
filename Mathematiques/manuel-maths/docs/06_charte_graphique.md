# Charte graphique — Manuel Nexus Réussite

Version 4.1 « Éditorial premium » — Juillet 2026. Ce document est la spécification de référence pour la mise en page du manuel. Toute production PDF doit s'y conformer. La classe `gabarits/nexus-manuel.cls` implémente ces règles. Le kit de référence est archivé dans `gabarits/reference-v4/manuel-kit/`.

---

## 1. Grille de page

### 1.1 Format et marges (kit v2)

Format A4 recto-verso (`twoside`). Marge extérieure large pour les notes marginales.

| Marge | Valeur |
|---|---|
| Intérieure (reliure) | 2,0 cm |
| Extérieure | 4,8 cm |
| Marginparwidth | 3,5 cm |
| Marginparsep | 0,6 cm |
| Haute | 2,4 cm |
| Basse | 2,6 cm |
| Headsep | 0,7 cm |

### 1.2 Rythme de lecture

- Corps TeX Gyre Pagella 9,5 pt, interligne `\linespread{1.06}`.
- `\raggedbottom` : pages respirantes.
- Espacement entre paragraphes : 0,45 em.
- `microtype` activé (protrusion, expansion, tracking).
- Veuves et orphelines interdites (`\widowpenalty=\clubpenalty=10000`).

---

## 2. Hiérarchie typographique

### 2.1 Polices

| Rôle | Police | Détails |
|---|---|---|
| Corps + maths | TeX Gyre Pagella + TeX Gyre Pagella Math | `fontspec` + `unicode-math`, interligne 1.06 |
| Titres, labels, en-têtes, folio | TeX Gyre Heros | `setsansfont`, Scale=0.94 |
| Code Python | JetBrains Mono | Embarqué `gabarits/fonts/`, Scale=0.89 |

Raccourci `\titrefont` = `\sffamily\bfseries` (toujours Heros gras).

### 2.2 Niveaux de titre

| Niveau | Taille | Couleur |
|---|---|---|
| `\chapter` (ouverture) | 34 pt, Heros gras blanc sur bandeau | chapcolor |
| `\section` | 13/17 pt, Heros gras | encre |
| `\subsection` | 11/14 pt, Heros gras | encre 85% noir |
| `\subsubsection` | 10/13 pt, Heros gras | encre 70% noir |

---

## 3. Palette

### 3.1 Couleurs de structure (fixes)

| Couleur | Hex | Nom interne | Usage |
|---|---|---|---|
| Encre | `#16233B` | `encre` | Texte structurel, titres |
| Fonds neutres | `#F2F1EC` | `grisdoux` | Fonds d'encadrés neutres, code |
| Hairlines | `#E2E0D8` | `filetgris` | Filets fins, cadres légers |

### 3.2 Accents de matière (vifs)

| Matière | Hex | Nom interne | Sélection |
|---|---|---|---|
| Mathématiques | `#3A2BD4` | `mathsAccent` | `\matiere{Mathématiques}` |
| NSI | `#0E9E6E` | `nsiAccent` | `\matiere{NSI}` |

La couleur d'accent active est `chapcolor`, pilotée par `\matiere`.

### 3.3 Couleurs sémantiques (stables)

| Rôle | Hex | Nom interne | Usage exclusif |
|---|---|---|---|
| À retenir / alerte | `#F5484B` | `coulRetenir` | Erreurs fréquentes, corail |
| Histoire des sciences | `#8A6D3B` | `coulHistoire` | Blocs historiques, sépia |
| Code informatique | `#1E293B` | `coulCode` | Fond/filet code, ardoise |

### 3.4 Principe de design

Un manuel « jeune et haut de gamme » ne multiplie PAS les couleurs. La hiérarchie passe par la FORME et la TYPO, pas par la teinte. Une couleur d'accent par chapitre, deux couleurs sémantiques stables, le reste en structure (encre, gris).

---

## 4. Système de pictogrammes

Définis dans `gabarits/nexus-icons.tex`. Trait 0,8 pt, boîte 1 em, monochromes. Les dingbats pifont sont interdits.

| Commande | Objet | Couleur par défaut |
|---|---|---|
| `\nxLosange` | Losange plein | `chapcolor` |
| `\icnObjectif` | Cible | `chapcolor` |
| `\icnMethode` | Boussole | `chapcolor` |
| `\icnErreur` | Triangle + ! | `coulRetenir` |
| `\icnCle` | Clé | `encre!50` |
| `\icnCheck` | Coche | `nsiAccent` |
| `\icnOral` | Bulle de parole | `chapcolor` |
| `\icnPython` | Chevrons ››› | `chapcolor` |
| `\icnChrono` | Cadran | `encre!50` |
| `\icnEtoile` | Étoile 4 branches | `chapcolor` |

Parcours : `\parcoursUn` (◆), `\parcoursDeux` (◆◆), `\parcoursTrois` (◆◆◆) — losanges à l'accent.

---

## 5. Styles d'encadrés (kit v2)

Tous en `tcolorbox`, `breakable`, coins arrondis 2 pt.

| Bloc | Signature visuelle | Environnement |
|---|---|---|
| Définition | Onglet plein chapcolor + fond teinté chapcolor!7 + barre gauche | `nxdef` |
| Théorème | Cadre contour chapcolor 1.2pt + bandeau plein chapcolor | `nxthm` |
| Propriété | Filet gauche chapcolor 2.5pt + label en ligne | `nxprop` |
| Méthode | Cadre fin filetgris + onglet contour chapcolor | `fmbox` |
| Erreur fréquente | Onglet plein corail + cadre corail 1.2pt | `nxerr` |
| Approfondissement | Onglet plein chapcolor + fond chapcolor!6 + filet gauche léger | `nxstar` |
| Carte (contrat) | Fond chapcolor!7 + barre gauche chapcolor | `nxcard` |

### Principes

- La distinction se fait par la GRAMMAIRE VISUELLE (onglet, cadre, filet), pas par la couleur.
- Fonds pastel : jamais plus de 8 % de saturation.
- Titres en capitales Heros gras (`\nxboxtitle`), letterspacing 8.

---

## 6. Exercices et navigation

### 6.1 En-tête d'exercice

Badge arrondi `chapcolor` avec « Exercice N » en blanc, suivi des losanges de parcours.
En marge : identifiant technique + chrono durée.

### 6.2 Corrigés

Badge arrondi `chapcolor!70!black` avec « Corrigé ». Standard copie-modèle, 10–20 lignes.

### 6.3 Coups de pouce

Fichiers compagnons `{ID}-CDP.tex`, regroupés après les exercices, jamais dans l'énoncé.

---

## 7. En-têtes et pieds de page

| Position | Contenu |
|---|---|
| En-tête impaire | Onglet de tranche chapcolor + mini-losange + headmark |
| Pied extérieur | Pastille ronde chapcolor avec numéro de page |
| Pied intérieur | « NEXUS RÉUSSITE » en petites capitales encre!50 |

Filet d'en-tête séparateur en chapcolor.

---

## 8. Page d'ouverture de chapitre

La commande `\ouverturechapitre[motif]{titre}{capacités}{accroche}{temps}` compose :

1. **Bandeau accent** : chapcolor plein sur 56 % de la hauteur de page.
2. **Numéro géant fantôme** : Heros gras 210 pt blanc opacity 0.15, ancré bas-gauche du bandeau.
3. **Étiquette matière · niveau** : Heros gras small, blanc opacity 0.9, haut-gauche.
4. **Titre** : Heros gras 34 pt blanc, ancré bas-gauche, text width 66 % page.
5. **Décor TikZ** : macro de `nexus-signatures.tex`, 100 % géométrique, moitié droite du bandeau.
6. **Sous le bandeau** : encadré objectifs chapcolor!7, carte accroche, temps estimés.

Décors livrés : spirale d'or (Suites), paraboles (Second degré), sécantes→tangente (Dérivation), grille binaire (Types construits), générique (fallback barres verticales).

---

## 9. Code informatique

Style `nxpy` : keywords chapcolor gras, commentaires encre!55 italique, chaînes coulHistoire, fond grisdoux, filet gauche coulCode!30, numéros de ligne encre!45.
`\code{mot}` pour le code en ligne (coulCode).
`\vocab{terme}{définition}` pour le vocabulaire en note marginale.

---

## 10. Imprimabilité et accessibilité

- Fonds lisibles en N&B (saturation ≤ 8 %).
- Pictogrammes doublés d'un libellé textuel.
- Contrastes ≥ 4,5:1 (WCAG AA).
- Liens internes cliquables, non dépendants de la couleur.

---

## 11. Figures mathématiques

Style dans `gabarits/nexus-figures.tex`.

| Élément | Style |
|---|---|
| Axes | encre!75, 0.6 pt, Stealth |
| Grille | filetgris, 0.3 pt |
| Courbes | chapcolor, 1.1 pt |
| Tangentes | chapcolor!70, 1.1 pt |
| Points | disque 1.6 pt chapcolor |

Règle : capacité graphique → ≥ 2 figures dans le cours, ≥ 1 dans les exercices. Chapitre d'analyse ≥ 6, géométrie ≥ 10.

---

## 12. Synchronisation de la charte

La synchro entre projets se fait UNIQUEMENT par le script `scripts/check_charte_sync.py` (7 fichiers) ou le rsync fichier-par-fichier de `SYNC_CHARTE.md`. `rsync --delete` sur `gabarits/` est **INTERDIT** car les extensions NSI (`nexus-code.tex`, `nexus-figures-nsi.tex`) n'existent que côté NSI.
