# Manuel scolaire LaTeX — Charte « Éditorial premium » (v2.0)

Feuille de style `manuel.sty` pour composer un manuel de lycée
(maths / NSI / physique-chimie) au rendu professionnel.

## Compilation

```
pdflatex main
makeindex main
pdflatex main
```
Compatible Overleaf (moteur **pdfLaTeX**, rien à configurer) ainsi que
lualatex/xelatex. Deux passes minimum pour la table des matières, les
références croisées (`cleveref`) et les compteurs d'encadrés.

## Principe de design

Un manuel « jeune et haut de gamme » **ne multiplie pas les couleurs**.
La charte fixe :

- **une couleur d'accent par matière** (`chapcolor`), qui rythme tout le
  chapitre : titres, pastilles de section, filets, numéro d'ouverture ;
- **deux couleurs sémantiques stables** : corail = *à retenir*,
  sépia = *histoire des sciences* ;
- le reste de la hiérarchie passe par la **forme** et la **typographie**,
  pas par la teinte.

| Bloc            | Signature visuelle                     |
|-----------------|----------------------------------------|
| Définition      | onglet plein + fond teinté + barre     |
| Théorème        | cadre contour + bandeau plein          |
| Propriété       | filet gauche + label en ligne          |
| Méthode         | cadre fin + onglet contour + n°        |
| Exemple         | filet fin + label capitales            |
| Activité        | cadre en tirets                        |
| À retenir       | corail, forte saillance                |
| Histoire        | sépia, italique                        |
| Démonstration   | filet + amorce italique + ∎            |
| Remarque        | gris neutre + amorce grasse            |

## Choisir la matière (accent + étiquette)

En tête de chaque fichier chapitre :

```latex
\matiere{maths}      % → indigo  · « Mathématiques »
\matiere{nsi}        % → émeraude · « Sciences numériques »
\matiere{physique}   % → terracotta · « Physique-Chimie »
\niveau{Terminale spécialité}
```

`\matiere{<Nom libre>}` accepte aussi un nom personnalisé (accent indigo
par défaut). Pour un accent sur mesure : `\couleurchapitre{maCouleur}`.

## Ouverture de chapitre (pleine page)

Le visuel par défaut de `\chapter` est neutralisé : c'est
`\ouverturechapitre` (ou l'environnement `ouverture`) qui peint la page
— bandeau couleur, numéro géant fantôme, titre, décor TikZ — puis dépose
les objectifs et passe à la page suivante.

```latex
\matiere{maths}
\chapter{Suites numériques et récurrence}   % n°, TOC, en-têtes

\begin{ouverture}[\decorFibonacci]{Suites numériques\\ et récurrence}
  \item Démontrer une propriété par récurrence.
  \item Étudier la limite d'une suite.
\end{ouverture}
```

- 1er argument optionnel `[...]` : **code TikZ du décor**, dessiné dans
  le repère `current page` (voir `\decorFibonacci` dans
  `chapitres/chap-suites.tex`). Définissez-le comme une macro pour éviter
  les soucis de crochets.
- 2e argument : **titre affiché** (répété volontairement — `\\` autorisé).
- corps : les objectifs, en `\item`.

Le décor est **entièrement géométrique** (rectangles d'or + spirale
logarithmique, cercles d'ondes, grille binaire…), sans illustration
externe : conforme à un rendu « tout TikZ ». Réservez la moitié droite
du bandeau.

## Encadrés pédagogiques

Tous numérotés par chapitre ; titre optionnel en argument `[...]`.

```latex
\begin{definition}[Principe de récurrence] ... \end{definition}
\begin{theoreme}[Limite de $q^n$]\label{thm:qn} ... \end{theoreme}
\begin{propriete} ... \end{propriete}
\begin{methode}[Rédiger une récurrence] ... \end{methode}
\begin{exemple} ... \end{exemple}
\begin{activite}[Seuil d'une suite] ... \end{activite}
\begin{retenir} ... \end{retenir}                 % titre : [Autre titre]
\begin{histoire}[Fibonacci (1202)] ... \end{histoire}
\begin{demonstration} ... \end{demonstration}      % ∎ automatique
\begin{remarque} ... \end{remarque}
```

## Code informatique

```latex
\begin{python}[recherche de seuil]
...code...
\end{python}
```
Mots-clés colorés à l'accent du chapitre, filet ardoise, numéros de
ligne. Code en ligne : `\code{seuil}`. Langage réglable dans le style
`manuelpython` (clé `language=`).

## Éléments de texte

- **Note de vocabulaire en marge** : `\vocab{récurrence}{définition…}`
- **Section** : pastille numérotée automatique.
- **Exercice** : `\exercice[2]{Titre}` → badge + difficulté ★★☆
  (1 à 3 étoiles). Placez-les en `multicols` pour la page d'exercices.
- **Figures** : `pgfplots` pré-stylé (axes encre, grille douce, accent
  du chapitre). Voir la courbe semi-log de `chap-suites.tex`.

## Options du package

```latex
\usepackage[palatino]{manuel}   % corps Palatino (défaut)
\usepackage[moderne]{manuel}    % corps Latin Modern
```

## Palette (rappel)

| Rôle              | Hex        |
|-------------------|------------|
| Encre (texte)     | `#16233B`  |
| Maths (accent)    | `#3A2BD4`  |
| NSI (accent)      | `#0E9E6E`  |
| Physique (accent) | `#E4572E`  |
| À retenir (corail)| `#F5484B`  |
| Histoire (sépia)  | `#8A6D3B`  |
| Code (ardoise)    | `#1E293B`  |
| Fonds neutres     | `#F2F1EC`  |

## Arborescence

```
manuel-kit/
├── manuel.sty              feuille de style (la charte)
├── main.tex                squelette + couverture pleine page
├── main.listing            extrait de code exporté (optionnel)
└── chapitres/
    ├── chap-suites.tex      maths — vitrine complète
    ├── chap-physique.tex    physique — accent terracotta
    └── chap-nsi.tex         NSI — accent émeraude
```

Licence : usage libre — Nexus Réussite.
