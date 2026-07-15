# Charte graphique — Manuel Nexus Reussite

Version 2.0 — Juillet 2026. Ce document est la specification de reference pour la mise en page du manuel. Toute production PDF doit s'y conformer. La classe `gabarits/nexus-manuel.cls` implemente ces regles.

---

## 1. Grille de page

### 1.1 Format et marges

Format A4 recto-verso (`twoside`). La grille distingue deux zones :

| Zone | Dimension | Contenu |
|---|---|---|
| Colonne principale | largeur utile entre marge interieure et marge exterieure, environ 12,5 cm | Cours, exercices, corriges, methodes, evaluations |
| Colonne de marge pedagogique | 3,6 cm, separee du texte par 5 mm (`marginparsep`) | Appuis, rappels, alertes, reperes de methode |

Marges imposees :

| Marge | Valeur |
|---|---|
| Interieure (reliure) | 2,0 cm |
| Exterieure | 4,5 cm (dont 3,6 cm de colonne pedagogique + 0,5 cm de separation + 0,4 cm de blanc) |
| Haute | 2,2 cm |
| Basse | 2,2 cm |

Aucun calcul indispensable ne vit dans la marge : elle n'accueille que des appuis courts (definitions rappelees, pictogrammes, renvois).

### 1.2 Rythme de lecture

- Interligne effectif minimal : 1,25 (corps 11 pt, interligne ~13,75 pt).
- `\raggedbottom` : une page reste respirante plutot que d'etirer les blancs verticaux.
- Aucun paragraphe > 8 lignes sans respiration (formule centree, exemple, liste, encadre ou saut de paragraphe).
- Espacement entre paragraphes : 0,45 em.
- Listes : `itemsep=0.25em`, `topsep=0.35em` — visiblement aerees.
- Formules longues : centrees et isolees par `\medskip` avant et apres.

---

## 2. Hierarchie typographique

### 2.1 Polices

| Role | Police | Package |
|---|---|---|
| Corps (texte + maths) | Linux Libertine + Libertine Math | `libertine` |
| Titres, titres d'encadres, navigation | Linux Biolinum (sans empattement) | charge automatiquement via `libertine` |
| Code Python | `\ttfamily` monospace systeme | — |

`microtype` est active pour l'optimisation des micro-espacements (protrusion, expansion).

### 2.2 Niveaux de titre

| Niveau | Element | Taille | Graisse | Couleur | Details |
|---|---|---|---|---|---|
| H0 | `\chapter` (ouverture) | 26 pt | gras | nxBleu | Pleine page, usage exclusif via `\ouverturechapitre` |
| H1 | `\section` (section-capacite Cn) | 15/19 pt | gras sans emp. | nxBleu | Rappel « Je sais... » en marge via `\sectionCapacite` |
| H2 | `\subsection` | 12/15 pt | gras sans emp. | nxBleu 85% noir | Sous-partie, jamais pour maquiller une phrase |
| H3 | `\subsubsection` | 11/14 pt | gras sans emp. | nxBleu 70% noir | Rarement utilise, reserve aux subdivisions techniques |

### 2.3 Contraintes typographiques

- Veuves et orphelines interdites : `\widowpenalty=\clubpenalty=10000`.
- Pas de cesure en debut de ligne apres un titre.
- Les titres d'encadres sont en **petites capitales** (`\textsc`).
- Le corps de l'encadre reste en romain standard.

---

## 3. Palette Nexus

### 3.1 Les cinq couleurs

| Couleur | Code HTML | Nom interne | Usage exclusif |
|---|---|---|---|
| Bleu Nexus | `#1B3A5C` | `nxBleu` | Savoir : definitions, theoremes, proprietes, titres, en-tetes |
| Or Nexus | `#C9A227` | `nxOr` | Methode : fiches methodes, parcours, temps, navigation |
| Rouge Nexus | `#B0413E` | `nxRouge` | Erreur : erreurs frequentes, contre-exemples, alertes |
| Vert Nexus | `#2E6E4E` | `nxVert` | Validation : exemples, corriges, verification, auto-evaluation |
| Gris Nexus | `#5A6472` | `nxGris` | Appui : marge pedagogique, cartes, informations secondaires |

### 3.2 Regles d'usage strictes

1. **Regle des 2 couleurs vives** : une page ne montre jamais plus de deux couleurs vives parmi bleu, or, rouge et vert. Le gris peut les accompagner sans restriction.
2. **Fonds d'encadres** : saturation limitee a 4-6 % de la teinte (ex. `nxBleu!4`, `nxOr!6`), jamais plus de 8 %. Objectif : lisibilite en impression noir et blanc.
3. **Texte sur fond** : toujours noir ou couleur sombre ; jamais de texte blanc sur fond colore (sauf eventuellement titres de chapitre d'ouverture, si aplat bleu).
4. **Coherence semantique** : une couleur = une fonction. Le bleu ne sert jamais a signaler une erreur ; le rouge ne sert jamais a valider.

---

## 4. Systeme de pictogrammes

| Pictogramme | Rendu | Signification | Contexte |
|---|---|---|---|
| `\parcoursUn` | ◆ (or) | Parcours Consolidation | Exercices, temps, navigation |
| `\parcoursDeux` | ◆◆ (or) | Parcours Maitrise | idem |
| `\parcoursTrois` | ◆◆◆ (or) | Parcours Approfondissement | idem |
| `\pictoOral` | icone + « Oral » (bleu) | Exercice a composante orale | En-tete d'exercice |
| `\pictoPython` | `>>> Python` (bleu) | Exercice a composante algorithmique | En-tete d'exercice |
| ▲ (ding 115) | triangle rouge | Erreur frequente | Titre d'encadre erreur |
| ★ | etoile bleue | Approfondissement hors-programme | Titre d'encadre etoile |

**Regle** : un pictogramme n'est jamais le seul porteur de sens. Un libelle textuel l'accompagne toujours (accessibilite).

---

## 5. Styles d'encadres

Tous les encadres utilisent `tcolorbox` avec les reglages suivants :

| Style | Fond | Cadre | Titre |
|---|---|---|---|
| Definition (`nxdef`) | `nxBleu!4` | regle gauche 1,2 pt nxBleu, pas de cadre | `\textsc{Definition}` + numero |
| Theoreme (`nxthm`) | `nxBleu!5` | regle gauche 1,2 pt nxBleu 80% noir | `\textsc{Theoreme}` + numero |
| Propriete (`nxprop`) | `nxGris!6` | regle gauche 1,2 pt nxGris | `\textsc{Propriete}` + numero |
| Erreur frequente (`nxerr`) | `nxRouge!6` | regle gauche 1,2 pt nxRouge | triangle + `\textsc{Erreur frequente}` |
| Methode (`fmbox`) | `nxOr!6` | regle gauche 1,2 pt nxOr 80% noir | `\textsc{Methode Mn}` + titre |
| Approfondissement (`nxstar`) | `nxBleu!5` | cadre fin 0,4 pt nxBleu | etoile + `\textsc{Pour aller plus loin}` |

### Principes communs

- **Breakable** : tous les encadres sont `breakable` (coupure entre pages autorisee).
- **Pas de cadre lourd** : regle gauche fine (1,2 pt) plutot que cadre integral.
- **Coins discrets** : pas d'arrondi excessif, coins a angle droit ou tres faible rayon.
- **Titres en petites capitales** : police sans empattement, gras.
- **Fond pastel** : jamais plus de 8 % de saturation.

---

## 6. Exercices et navigation

### 6.1 En-tete d'exercice

Chaque exercice affiche au premier regard :
1. **Numero** en gras bleu (`Exercice N`) — tres visible.
2. **Parcours** en or (◆, ◆◆ ou ◆◆◆) — immediatement apres le numero.
3. **Identifiant technique** en petit monospace (`1SPE-SUITES-EX-024`).
4. **Duree estimee** en minutes.

### 6.2 Coups de pouce

Les coups de pouce sont des fichiers compagnons `exercices/{ID}-CDP.tex`. Ils sont regroupes apres l'ensemble des exercices de la capacite, jamais dans l'enonce. Trois niveaux : reformulation, premiere etape, plan de resolution.

### 6.3 Corriges

Les corriges sont au standard « copie modele » : redaction complete, theoremes cites, hypotheses verifiees, 10-20 lignes. Ils apparaissent dans une section dediee en fin de chapitre, precedes de leur identifiant en vert.

---

## 7. En-tetes, pieds de page et sommaire

### 7.1 En-tetes et pieds

| Position | Page paire (gauche) | Page impaire (droite) |
|---|---|---|
| En-tete | Titre du chapitre courant (petites cap.) | « Nexus Reussite » (petites cap.) |
| Pied | — | — |
| Pied central | Numero de page | Numero de page |

Le filet d'en-tete est fin (0,4 pt). La page d'ouverture utilise `plain` (pas d'en-tete).

### 7.2 Sommaire

Le sommaire est precede de l'ouverture de chapitre. Les entrees de section affichent le numero et le titre en bleu sans empattement. Les sous-sections apparaissent en retrait. Le sommaire est genere automatiquement par `\tableofcontents`.

---

## 8. Page d'ouverture de chapitre

La commande `\ouverturechapitre{titre}{capacites}{carte}{temps}` compose une pleine page :

1. **Titre** en 26 pt gras bleu, precede d'un espace vertical genereux.
2. **Liste « Ce que je vais savoir faire »** : capacites C1..Cn en langage eleve.
3. **Carte du chapitre** : encadre gris, resume de la situation d'accroche et structure.
4. **Temps estimes** par parcours : or, en pied de la page d'ouverture.

L'entree est ajoutee automatiquement au sommaire. Le style de page est `plain`.

---

## 9. Imprimabilite et accessibilite

- Tous les fonds restent lisibles en impression noir et blanc (saturation <= 8 %).
- Les pictogrammes sont doubles d'un libelle textuel.
- Les contrastes texte/fond respectent un ratio >= 4,5:1 (WCAG AA).
- Les liens internes (renvois exercices <-> corriges) sont cliquables en PDF mais ne dependent pas de la couleur seule.
