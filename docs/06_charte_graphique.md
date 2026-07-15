# Charte graphique — Manuel Nexus Réussite

Version 3.2 — Juillet 2026. Ce document est la spécification de référence pour la mise en page du manuel. Toute production PDF doit s'y conformer. La classe `gabarits/nexus-manuel.cls` implémente ces règles.

---

## 1. Grille de page

### 1.1 Format et marges

Format A4 recto-verso (`twoside`). La grille distingue deux zones :

| Zone | Dimension | Contenu |
|---|---|---|
| Colonne principale | largeur utile entre marge intérieure et marge extérieure, environ 12,5 cm | Cours, exercices, corrigés, méthodes, évaluations |
| Colonne de marge pédagogique | 3,6 cm, séparée du texte par 5 mm (`marginparsep`) | Appuis, rappels, alertes, repères de méthode |

Marges imposées :

| Marge | Valeur |
|---|---|
| Intérieure (reliure) | 2,0 cm |
| Extérieure | 4,5 cm (dont 3,6 cm de colonne pédagogique + 0,5 cm de séparation + 0,4 cm de blanc) |
| Haute | 2,2 cm |
| Basse | 2,2 cm |

Aucun calcul indispensable ne vit dans la marge : elle n'accueille que des appuis courts (définitions rappelées, pictogrammes, renvois).

### 1.2 Rythme de lecture

- Interligne effectif minimal : 1,25 (corps 11 pt, interligne ~13,75 pt).
- `\raggedbottom` : une page reste respirante plutôt que d'étirer les blancs verticaux.
- Aucun paragraphe > 8 lignes sans respiration (formule centrée, exemple, liste, encadré ou saut de paragraphe).
- Espacement entre paragraphes : 0,45 em.
- Listes : `itemsep=0.25em`, `topsep=0.35em` — visiblement aérées.
- Formules longues : centrées et isolées par `\medskip` avant et après.

---

## 2. Hiérarchie typographique

### 2.1 Polices

| Rôle | Police | Package |
|---|---|---|
| Corps (texte + maths) | Linux Libertine + Libertine Math | `libertine` + `newtxmath` |
| Titres, titres d'encadrés, navigation | Linux Biolinum (sans empattement) | chargé automatiquement via `libertine` |
| Code Python | `\ttfamily` monospace système | — |

`microtype` est activé pour l'optimisation des micro-espacements (protrusion, expansion).

### 2.2 Niveaux de titre

| Niveau | Élément | Taille | Graisse | Couleur | Détails |
|---|---|---|---|---|---|
| H0 | `\chapter` (ouverture) | 26 pt | gras | nxBleu | Pleine page, usage exclusif via `\ouverturechapitre` |
| H1 | `\section` (section-capacité Cn) | 15/19 pt | gras sans emp. | nxBleu | Rappel « Je sais… » en marge via `\sectionCapacite` |
| H2 | `\subsection` | 12/15 pt | gras sans emp. | nxBleu 85% noir | Sous-partie, jamais pour maquiller une phrase |
| H3 | `\subsubsection` | 11/14 pt | gras sans emp. | nxBleu 70% noir | Rarement utilisé, réservé aux subdivisions techniques |

### 2.3 Contraintes typographiques

- Veuves et orphelines interdites : `\widowpenalty=\clubpenalty=10000`.
- Pas de césure en début de ligne après un titre.
- Les titres d'encadrés sont en capitales réelles (`\MakeUppercase`) : Montserrat ne fournit pas de petites capitales utilisables par `fontspec`. La couleur est cuite dans `\nxboxtitle{couleur}{texte}` et ne dépend jamais de `tcbcolframe`.
- Le corps de l'encadré reste en romain standard.

---

## 3. Palette Nexus

### 3.1 Les cinq couleurs

| Couleur | Code HTML | Nom interne | Usage exclusif |
|---|---|---|---|
| Bleu Nexus | `#1B3A5C` | `nxBleu` | Savoir : définitions, théorèmes, propriétés, titres, en-têtes |
| Or Nexus | `#C9A227` | `nxOr` | Méthode : fiches méthodes, parcours, temps, navigation |
| Rouge Nexus | `#B0413E` | `nxRouge` | Erreur : erreurs fréquentes, contre-exemples, alertes |
| Vert Nexus | `#2E6E4E` | `nxVert` | Validation : exemples, corrigés, vérification, auto-évaluation |
| Gris Nexus | `#5A6472` | `nxGris` | Appui : marge pédagogique, cartes, informations secondaires |

### 3.2 Règles d'usage strictes

1. **Règle des 2 couleurs vives** : une page ne montre jamais plus de deux couleurs vives parmi bleu, or, rouge et vert. Le gris peut les accompagner sans restriction.
2. **Fonds d'encadrés** : saturation limitée à 4–6 % de la teinte (ex. `nxBleu!4`, `nxOr!6`), jamais plus de 8 %. Objectif : lisibilité en impression noir et blanc.
3. **Texte sur fond** : toujours noir ou couleur sombre ; jamais de texte blanc sur fond coloré (sauf éventuellement titres de chapitre d'ouverture, si aplat bleu).
4. **Cohérence sémantique** : une couleur = une fonction. Le bleu ne sert jamais à signaler une erreur ; le rouge ne sert jamais à valider.

---

## 4. Système de pictogrammes

| Pictogramme | Rendu | Signification | Contexte |
|---|---|---|---|
| `\parcoursUn` | ◆ (or) | Parcours Consolidation | Exercices, temps, navigation |
| `\parcoursDeux` | ◆◆ (or) | Parcours Maîtrise | idem |
| `\parcoursTrois` | ◆◆◆ (or) | Parcours Approfondissement | idem |
| `\pictoOral` | icône + « Oral » (bleu) | Exercice à composante orale | En-tête d'exercice |
| `\pictoPython` | `>>> Python` (bleu) | Exercice à composante algorithmique | En-tête d'exercice |
| ▲ (ding 115) | triangle rouge | Erreur fréquente | Titre d'encadré erreur |
| ★ | étoile bleue | Approfondissement hors-programme | Titre d'encadré étoile |

**Règle** : un pictogramme n'est jamais le seul porteur de sens. Un libellé textuel l'accompagne toujours (accessibilité).

---

## 5. Styles d'encadrés

Tous les encadrés utilisent `tcolorbox` avec les réglages suivants :

| Style | Fond | Cadre | Titre |
|---|---|---|---|
| Définition (`nxdef`) | `nxBleu!4` | règle gauche 2 pt nxBleu | bleu Nexus |
| Théorème (`nxthm`) | `nxBleu!5` | règle gauche 2 pt nxBleu 80% noir | bleu Nexus 80% noir |
| Propriété (`nxprop`) | `nxGris!6` | règle gauche 2 pt nxGris 80% noir | nxGris 80% noir (jamais gris pur) |
| Erreur fréquente (`nxerr`) | `nxRouge!6` | règle gauche 2 pt nxRouge | rouge Nexus |
| Méthode (`fmbox`) | `nxOr!6` | règle gauche 2 pt nxOr 75% noir | nxOr 75% noir |
| Approfondissement (`nxstar`) | `nxBleu!6` | sans filet | bleu Nexus |
| Carte (`nxcard`) | `nxGris!6` | règle gauche 2 pt nxGris 80% noir | nxGris 80% noir |
| Mini-projet (`mpbox`) | `nxOr!5` | règle gauche 2 pt nxOr 75% noir | nxOr 75% noir |

### Principes communs

- **Breakable** : tous les encadrés sont `breakable` (coupure entre pages autorisée).
- **Pas de cadre lourd** : règle gauche fine (1,2 pt) plutôt que cadre intégral.
- **Coins discrets** : pas d'arrondi excessif, coins à angle droit ou très faible rayon.
- **Titres en petites capitales** : police sans empattement, gras.
- **Fond pastel** : jamais plus de 8 % de saturation.

---

## 6. Exercices et navigation

### 6.1 En-tête d'exercice

Chaque exercice affiche au premier regard :
1. **Numéro** en gras bleu (`Exercice N`) — très visible.
2. **Parcours** en or (◆, ◆◆ ou ◆◆◆) — immédiatement après le numéro.
3. **Identifiant technique** en petit monospace (`1SPE-SUITES-EX-024`).
4. **Durée estimée** en minutes.

### 6.2 Coups de pouce

Les coups de pouce sont des fichiers compagnons `exercices/{ID}-CDP.tex`. Ils sont regroupés après l'ensemble des exercices de la capacité, jamais dans l'énoncé. Trois niveaux : reformulation, première étape, plan de résolution.

### 6.3 Corrigés

Les corrigés sont au standard « copie modèle » : rédaction complète, théorèmes cités, hypothèses vérifiées, 10–20 lignes. Ils apparaissent dans une section dédiée en fin de chapitre, précédés de leur identifiant en vert.

---

## 7. En-têtes, pieds de page et sommaire

### 7.1 En-têtes et pieds

| Position | Page paire (gauche) | Page impaire (droite) |
|---|---|---|
| En-tête | Titre du chapitre courant (petites cap.) | « Nexus Réussite » (petites cap.) |
| Pied | — | — |
| Pied central | Numéro de page | Numéro de page |

Le filet d'en-tête est fin (0,4 pt). La page d'ouverture utilise `plain` (pas d'en-tête).

### 7.2 Sommaire

Le sommaire est précédé de l'ouverture de chapitre. Les entrées de section affichent le numéro et le titre en bleu sans empattement. Les sous-sections apparaissent en retrait. Le sommaire est généré automatiquement par `\tableofcontents`.

---

## 8. Page d'ouverture de chapitre

La commande `\ouverturechapitre{titre}{capacités}{carte}{temps}` compose une pleine page :

1. **Page bleue identitaire** : numéro de chapitre Montserrat Thin 110 pt blanc à 85 % en haut à droite ; motif génératif du chapitre dans la moitié inférieure droite ; filet or 30 mm × 1,2 pt au-dessus du titre blanc 26 pt ; signature « Manuel NSI Première — Nexus Réussite » en Montserrat Medium 8,5 pt blanc 80 %.
2. **Liste « Ce que je vais savoir faire »** : chaque capacité C1..Cn est précédée de `\icnObjectif` et formulée en langage élève.
3. **Carte du chapitre** : encadré gris, résumé de la situation d'accroche et structure.
4. **Temps estimés** par parcours : or, en pied de la page d'ouverture.

L'entrée est ajoutée automatiquement au sommaire. Le style de page est `plain`.

---

## 9. Imprimabilité et accessibilité

- Tous les fonds restent lisibles en impression noir et blanc (saturation ≤ 8 %).
- Les pictogrammes sont doublés d'un libellé textuel.
- Les contrastes texte/fond respectent un ratio ≥ 4,5:1 (WCAG AA).
- Les liens internes (renvois exercices ↔ corrigés) sont cliquables en PDF mais ne dépendent pas de la couleur seule.

---

## 10. Identité visuelle Nexus Réussite

### 10.1 Icônes propriétaires TikZ

Définies dans `gabarits/nexus-icons.tex`. Trait 0,8 pt uniforme, boîte 1 em, monochromes. Les dingbats pifont sont interdits dans le rendu final.

| Commande | Objet | Usage |
|---|---|---|
| `\nxLosange` | Losange or plein, contour nxBleu 0,4 pt | Parcours (remplace \ding{117}) |
| `\icnObjectif` | Cible | « Je sais… » |
| `\icnMethode` | Boussole | Fiches méthodes |
| `\icnErreur` | Triangle arrondi + ! | Erreurs fréquentes |
| `\icnCle` | Clé | Coups de pouce |
| `\icnCheck` | Coche | Corrigés |
| `\icnOral` | Bulle de parole | Exercices oraux |
| `\icnPython` | Chevrons ››› | Exercices algorithmiques |
| `\icnChrono` | Cadran | Durées |
| `\icnEtoile` | Étoile 4 branches fines | Approfondissement |
| `\icnCarte` | Nœuds reliés | Carte du chapitre |

### 10.2 Signature de chapitre

Définie dans `gabarits/nexus-signatures.tex`.

- **Bandeau d'ouverture** : bande verticale nxBleu!12 sur le bord extérieur de la page d'ouverture, avec motif génératif propre au thème (Suites : points en progression, Dérivation : faisceau de sécantes, Second degré : famille de paraboles, Probabilités : arbre).
- **Onglet de tranche** : rectangle nxBleu plein (0,6 cm × 1,5 cm) en bord extérieur des pages impaires, position verticale décalée par chapitre (navigation livre fermé).
- **Mini-losange en-tête** : losange nxBleu!30 dans l'en-tête de chaque page, identification discrète du chapitre.

### 10.3 Figures mathématiques

Style normalisé dans `gabarits/nexus-figures.tex`.

| Élément | Style |
|---|---|
| Axes | nxGris 0,5 pt, flèches Stealth 4 pt |
| Grille | nxGris!15, 0,3 pt |
| Courbes | nxBleu 1,1 pt |
| Tangentes | nxOr 1,1 pt |
| Sécantes | nxOr!60, 0,8 pt, pointillées |
| Points de contact | disque 1,6 pt nxBleu, sans étiquette |
| Aires | nxVert!15, sans contour |

Les graduations sont limitées aux valeurs utiles. Une étiquette de courbe se place en fin de courbe, décalée à droite (`\node[right, nxBleu]`), jamais sur le tracé. Une étiquette de tangente se place sous la droite en `nxOr!75!black`. Le point de contact ne porte aucune autre annotation.

**Règle permanente** : toute capacité graphique implique ≥ 2 figures dans le cours et ≥ 1 dans les exercices. Chapitre d'analyse ≥ 6 figures, géométrie ≥ 10.
