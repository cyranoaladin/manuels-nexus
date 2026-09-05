% nexus-manuel.cls v4.1 — Classe du manuel Nexus Réussite (édition premium)
% Moteur : LuaLaTeX obligatoire. Base : KOMA-Script scrbook.
% Polices : TeX Gyre Pagella (corps + maths) + TeX Gyre Heros (titres) + JetBrains Mono (code).
% Charte graphique : kit v2 « Éditorial premium » transposé.
\NeedsTeXFormat{LaTeX2e}
% Ces gabarits sont chargés par leur chemin -- `../../gabarits/common/nexus-charte`
% depuis les mathématiques, autrement depuis la NSI. LaTeX comparait ce chemin au
% nom déclaré ici et signalait l'écart, une fois par fichier. `\@currname` EST le
% nom demandé : le fichier déclare donc qu'il est bien celui qu'on a appelé, et
% garde son identité lisible dans la description. Le noyau compare le nom déclaré
% à `\@currpath\@currname` : c'est donc cette paire, et non le seul `\@currname`,
% qui rend la déclaration exacte. Aucun `\@ifpackageloaded` du
% dépôt n'interroge ces noms ; l'identité des trois copies est prouvée par les
% tests d'égalité octet à octet, pas par cette ligne.
\ProvidesClass{\@currpath\@currname}[2026/07/20 v6.0 nexus-manuel -- Manuel Nexus Reussite - Canonique]

% ===========================================================================
%  BASE KOMA-SCRIPT
% ===========================================================================
% `DIV=6` est écrit, et non plus déduit : typearea ne tabule aucune valeur de
% DIV pour un corps de 9,5 pt, cherchait donc la sienne en vain, le signalait,
% puis retombait sur `DIV=calc`. Six est exactement ce que ce calcul donne,
% ce que vérifie, en interrogeant typearea seul,
% test_the_written_div_is_the_one_the_calculation_gives. L'écrire fixe
% aussi la mise en page si une version ultérieure de KOMA calculait autrement.
\ifdefined\nxVBaseCompatibility
  \LoadClass[a4paper,fontsize=9.5pt,DIV=6,twoside,open=right,headings=normal,
    chapterprefix=false,numbers=noenddot]{scrbook}
\else
  \LoadClass[a4paper,fontsize=9.5pt,DIV=6,twoside,open=any,headings=normal,
    chapterprefix=false,numbers=noenddot]{scrbook}
\fi

% ===========================================================================
%  MOTEUR ET LANGUE
% ===========================================================================
\RequirePackage{iftex}
\RequireLuaTeX
\RequirePackage[french]{babel}
\RequirePackage{csquotes}
\RequirePackage{amsmath}
\RequirePackage{amsthm}
\RequirePackage{amssymb}
% Les deux carrés de fin de démonstration -- creux et plein -- venaient de
% MSAM10, une fonte AMS héritée dont le PDF ne porte aucune table ToUnicode.
% Le glyphe s'extrayait donc comme le caractère de contrôle U+0003 (creux) ou
% U+0004 (plein) : une couche de texte que l'on ne peut ni copier ni analyser,
% et qui rendait invalide le XML de `pdftotext -bbox` -- ce qui a fait échouer
% la vérification des marges sur le manuel livré, à la ligne 11 642.
%
% Ils sont donc dessinés, avec des filets : mêmes métriques au centième de
% point près (7,3889 pt de large, 6,41249 pt de haut, aucune profondeur,
% mesurées sur MSAM10 puis reproduites en em pour suivre le corps), et plus
% aucun caractère dans la couche de texte -- un ornement de fin de preuve n'en
% est pas un.
\newcommand{\nxCarreCote}{0.678em}
\newcommand{\nxCarreFlanc}{0.0516em}
\renewcommand{\square}{%
  \mathord{\raisebox{\depth}{%
    \fboxsep=0pt\fboxrule=0.4pt
    \kern\nxCarreFlanc
    \fbox{\rule{0pt}{\dimexpr\nxCarreCote-0.8pt\relax}%
          \rule{\dimexpr\nxCarreCote-0.8pt\relax}{0pt}}%
    \kern\nxCarreFlanc}}}
\renewcommand{\blacksquare}{%
  \mathord{\kern\nxCarreFlanc
    \rule[0pt]{\nxCarreCote}{\nxCarreCote}%
    \kern\nxCarreFlanc}}

% ===========================================================================
%  MATIÈRE ET NIVEAU (paramétrage du sous-titre de couverture)
% ===========================================================================
\ifdefined\nxVBaseCompatibility
  \newcommand{\nexus@matiere}{NSI}
  \newcommand{\nexus@niveau}{Première}
\else
  \newcommand{\nexus@matiere}{Mathématiques}
  \newcommand{\nexus@niveau}{Première spécialité}
\fi
\RequirePackage{etoolbox}
\newcommand{\matiere}[1]{%
  \renewcommand{\nexus@matiere}{#1}%
  \ifstrequal{#1}{Mathématiques}{\colorlet{chapcolor}{mathsAccent}}{%
  \ifstrequal{#1}{NSI}{\colorlet{chapcolor}{nsiAccent}}{%
  \colorlet{chapcolor}{mathsAccent}}}%
}
\newcommand{\niveau}[1]{\renewcommand{\nexus@niveau}{#1}}

% ===========================================================================
%  POLICES — Kit v2 : Pagella (corps+maths), Heros (titres), JetBrains Mono (code)
% ===========================================================================
\RequirePackage{fontspec}
\RequirePackage{unicode-math}

\defaultfontfeatures{Ligatures=TeX}

% Corps : TeX Gyre Pagella (= Palatino libre), interligne 1.06
\setmainfont{TeX Gyre Pagella}
\linespread{1.06}
% Mathématiques : TeX Gyre Pagella Math
\setmathfont{TeX Gyre Pagella Math}

% Titres, labels, en-têtes, folio : TeX Gyre Heros (= Helvetica libre)
\setsansfont{TeX Gyre Heros}[Scale=0.94]
% Raccourci « famille titre » : toujours sans-serif gras.
\newcommand{\titrefont}{\sffamily\bfseries}

% Code : JetBrains Mono (installé dans le système ou ~/.local/share/fonts/)
% Les fichiers .otf sources sont conservés dans gabarits/fonts/ pour la CI.
% Le code imprimé doit être RECOPIABLE : ce que l'élève lit doit être ce que
% Python accepte. `\defaultfontfeatures{Ligatures=TeX}` s'applique à TOUTES les
% fontes chargées ensuite, celle du code comprise -- et la fonctionnalité
% `tlig` y transforme le guillemet droit `"` en guillemet typographique `”`.
% Un manuel imprimait donc `print(f”...”)`, `”””Renvoie...”””` : du code
% syntaxiquement invalide, sur 29 pages. Les ligatures de programmation de
% JetBrains Mono soudaient en outre `==` en un seul glyphe.
%
% Ces trois fonctionnalités sont donc éteintes POUR LA FONTE DU CODE, et pour
% elle seule : la typographie française du corps garde ses guillemets, ses
% tirets et ses ligatures. Remplacer globalement les guillemets du manuel
% aurait cassé le texte pour réparer le code.
% `Ligatures=NoCommon` demandait la desactivation de `liga` par le nom que
% fontspec lui donne ; JetBrains Mono n'expose pas cette fonctionnalite sous ce
% script, et fontspec le signalait dix fois par compilation. L'option etait de
% toute facon redondante : `RawFeature` desactive les trois fonctionnalites
% -- ligatures TeX, contextuelles et de programmation -- et le controle de
% fidelite du code imprime prouve que la sortie reste fidele a l'octet pres.
\setmonofont{JetBrains Mono}[Scale=0.89, RawFeature={-tlig;-calt;-liga}]

% ===========================================================================
%  TYPOGRAPHIE PROFESSIONNELLE
% ===========================================================================
\RequirePackage[activate={true,nocompatibility},tracking=true,
  expansion=true,protrusion=true]{microtype}
\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\setlength{\parskip}{0.45em}
\ifdefined\nxVBaseCompatibility\else
  \emergencystretch=2em
\fi

% ===========================================================================
%  COULEURS — Kit v2 « Éditorial premium »
% ===========================================================================
\RequirePackage[table]{xcolor}

% -- Structure (fixe) --
\definecolor{encre}{HTML}{16233B}       % bleu nuit — texte structurel
\definecolor{grisdoux}{HTML}{F2F1EC}    % fonds neutres chauds
\definecolor{filetgris}{HTML}{E2E0D8}   % hairlines

% -- Accents de matière --
\definecolor{mathsAccent}{HTML}{3A2BD4}   % indigo — maths
\definecolor{nsiAccent}{HTML}{0E9E6E}     % émeraude — NSI

% -- Sémantique stable --
\definecolor{coulRetenir}{HTML}{F5484B}   % corail — à retenir / alerte
\definecolor{coulHistoire}{HTML}{8A6D3B}  % sépia — histoire des sciences
\definecolor{coulCode}{HTML}{1E293B}      % ardoise — code informatique

% -- Couleur d'accent du chapitre (pilotée par \matiere) --
\colorlet{chapcolor}{mathsAccent}

% -- Alias v3 (rétro-compatibilité fichiers existants, dépréciés) --
\colorlet{nxBleu}{encre}
\colorlet{nxOr}{coulHistoire}
\colorlet{nxGris}{encre!50}
\colorlet{nxRouge}{coulRetenir}
\colorlet{nxVert}{nsiAccent}

% ===========================================================================
%  GRILLE DE PAGE — Kit v2 : marge ext. large pour notes marginales
% ===========================================================================
\RequirePackage{geometry}
\ifdefined\nxVBaseCompatibility
  \geometry{%
    a4paper,
    top=2.4cm, bottom=2.6cm,
    inner=2.0cm, outer=4.8cm,
    marginparwidth=3.5cm, marginparsep=0.6cm,
    headsep=0.7cm,
  }
\else
  \geometry{%
    a4paper,
    top=2.4cm, bottom=2.6cm,
    inner=2.0cm, outer=4.4cm,
    marginparwidth=2.8cm, marginparsep=0.45cm,
    headsep=0.7cm,
  }
  \setlength{\marginparpush}{6pt}
\fi

% ===========================================================================
%  BOÎTES DE PAGE ET FOND PERDU
% ===========================================================================
% Décision produit (2026-09-03) : format fini A4, fond perdu de 3 mm sur les
% quatre côtés.
%   TrimBox  = 210 × 297 mm  (le format fini, après coupe)
%   BleedBox = TrimBox + 3 mm de chaque côté = 216 × 303 mm
%   MediaBox = BleedBox
%
% Mise en œuvre côté moteur, sans post-traitement PDF : le support (\pagewidth,
% \pageheight) est agrandi de 2 × 3 mm et le contenu est décalé de 3 mm vers
% l'intérieur (\hoffset, \voffset). \paperwidth et \paperheight, eux, restent
% le format FINI : le nœud « current page » de TikZ, que toute la charte
% utilise pour se caler sur les bords, continue donc de désigner exactement la
% TrimBox. C'est la propriété qui protège la géométrie contractuelle de
% l'onglet latéral : ses 12 mm visibles restent 12 mm à l'intérieur du format
% fini et son millimètre d'encre débordante reste UN millimètre hors TrimBox.
% Les 2 mm restants entre l'onglet et la BleedBox sont la marge technique de
% coupe : offrir 3 mm de fond perdu ne fait pas passer l'onglet à 3 mm.
%
% \newgeometry et \restoregeometry restaurent \hoffset et \voffset dans l'état
% sauvegardé par geometry au début du document, c'est-à-dire sans décalage :
% le manuel les appelle à chaque bloc de cours et à chaque grille d'exercices,
% et le fond perdu disparaîtrait sur ces centaines de pages. Les deux commandes
% réappliquent donc le décalage.
\newcommand*{\nxFondPerduDim}{3mm}
\newlength{\nxFondPerdu}

% ORIGINE DE LA PAGE COMPOSÉE DANS LE SUPPORT — source de vérité unique du
% référentiel. La page composée est le format fini : son coin est l'origine du
% TrimBox. Le support (MediaBox) l'entoure du fond perdu. Trois consommateurs
% en descendent, et un seul de ces deux registres est écrit à la main :
%
%   \hoffset, \voffset          décalage du contenu dans le support ;
%   /TrimBox                    coin de la page composée dans le PDF ;
%   compositeur de marges       repère logique des obstacles et du rail.
%
% Le compositeur reçoit cette origine et VÉRIFIE qu'elle vaut bien \hoffset et
% \voffset au moment où les coordonnées sont produites. Un fond perdu qui
% changerait, ou qui serait appliqué à un autre moment de l'initialisation, ne
% peut donc plus translater silencieusement le contenu logique de 3 mm : il
% échoue. C'est le défaut mesuré le 2026-09-03 (559 403 sp, soit exactement le
% fond perdu) entre le rail et l'obstacle déclaré.
\newlength{\nxOrigineTrimX}
\newlength{\nxOrigineTrimY}
% Le fond perdu est POSÉ en un seul endroit, et l'origine de la page composée
% en découle. C'est ce qui rend la géométrie invariante au fond perdu :
% la changer ici déplace le support et la boîte PDF, jamais la position
% logique du contenu imprimé.
\newcommand{\nxFixerFondPerdu}[1]{%
  \setlength{\nxFondPerdu}{#1}%
  \setlength{\nxOrigineTrimX}{\nxFondPerdu}%
  \setlength{\nxOrigineTrimY}{\nxFondPerdu}%
}
\nxFixerFondPerdu{\nxFondPerduDim}

\newcommand{\nxAppliquerFondPerdu}{%
  \hoffset=\nxOrigineTrimX
  \voffset=\nxOrigineTrimY
  \pagewidth=\dimexpr\paperwidth+2\nxFondPerdu\relax
  \pageheight=\dimexpr\paperheight+2\nxFondPerdu\relax
}
% Conversion d'une longueur TeX en points PostScript (l'unité des boîtes PDF) :
% 1 in = 72 bp = 72,27 pt, donc 1 pt = 7200/7227 bp exactement.
%
% Le rapport est écrit comme une division d'entiers, et non comme le décimal
% 0.996264 : \dimexpr lit un coefficient décimal en le quantifiant au 1/65536,
% ce qui introduisait 1,4 · 10⁻³ bp sur une largeur A4 — environ 95 sp, donc
% au-delà du sp près que les gates de marge exigent. La forme « *7200/7227 »
% multiplie sur 64 bits avant de diviser : l'erreur retombe au demi-sp de
% l'arrondi final, et les boîtes de page deviennent comparables exactement.
\newcommand{\nxDimEnBp}[1]{\strip@pt\dimexpr\dimexpr#1\relax*7200/7227\relax}
% Le TrimBox est posé à l'origine déclarée, pas à une constante répétée : la
% boîte PDF et le décalage du contenu ne peuvent pas diverger.
\newcommand{\nxDeclarerBoitesDePage}{%
  \edef\nx@boitesDePage{%
    /TrimBox [\nxDimEnBp{\nxOrigineTrimX}\space\nxDimEnBp{\nxOrigineTrimY}\space
      \nxDimEnBp{\dimexpr\nxOrigineTrimX+\paperwidth\relax}\space
      \nxDimEnBp{\dimexpr\nxOrigineTrimY+\paperheight\relax}]
    /BleedBox [0 0 \nxDimEnBp{\dimexpr2\nxFondPerdu+\paperwidth\relax}\space
      \nxDimEnBp{\dimexpr2\nxFondPerdu+\paperheight\relax}]%
  }%
  \pdfvariable pageattr\expandafter{\nx@boitesDePage}%
}
\apptocmd{\newgeometry}{\nxAppliquerFondPerdu}{}{%
  \ClassError{nexus-manuel}{fond perdu non rebranche sur \string\newgeometry}{}}
\apptocmd{\restoregeometry}{\nxAppliquerFondPerdu}{}{%
  \ClassError{nexus-manuel}{fond perdu non rebranche sur
    \string\restoregeometry}{}}
% geometry réaffirme \pagewidth/\pageheight dans son propre \AtBeginDocument,
% et le fait APRÈS le nôtre (mesure du 2026-09-03 : \hoffset gardait bien
% 3 mm, \pagewidth retombait à 210 mm et la MediaBox restait A4). On agrandit
% donc le support dans « begindocument/end », qui s'exécute une fois tout
% \AtBeginDocument terminé.
\AddToHook{begindocument/end}{%
  \nxAppliquerFondPerdu
  \nxDeclarerBoitesDePage
}

% ===========================================================================
%  MARGE PÉDAGOGIQUE (colonne de design)
% ===========================================================================
\RequirePackage{marginnote}
\RequirePackage{mparhack}
\renewcommand*{\raggedleftmarginnote}{}
\renewcommand*{\raggedrightmarginnote}{\raggedright}

\newcommand{\margeAppui}[1]{%
  \nxMarginRailNote{appui}{\sffamily\fontsize{7.5}{10}\selectfont
    \color{encre!50}\rule[-0.5ex]{0.4pt}{2.5ex}\kern4pt #1}%
}
\newcommand{\commentaireMarge}[1]{%
  \nxMarginRailNote{commentaire}{%
    \sffamily\fontsize{7.5}{10}\selectfont\color{chapcolor}#1}%
}
% Vocabulaire en marge (kit v2)
\newcommand{\vocab}[2]{%
  \textcolor{chapcolor}{\textbf{#1}}%
  \nxMarginRailNote{vocab}{\textcolor{chapcolor}{\rule{2.6cm}{2pt}}\\[2pt]
    {\titrefont\color{chapcolor}#1}\\[2pt]\itshape\small #2}}

% ===========================================================================
%  HIÉRARCHIE TYPOGRAPHIQUE (KOMA-Script RedeclareSectionCommand)
% ===========================================================================
\addtokomafont{chapter}{\titrefont\color{encre}\fontsize{22}{27}\selectfont}
\ifdefined\nxVBaseCompatibility
  \addtokomafont{section}{\titrefont\color{encre}\fontsize{13}{17}\selectfont}
  \addtokomafont{subsection}{\titrefont\color{encre!85!black}\fontsize{11}{14}\selectfont}
  \addtokomafont{subsubsection}{\titrefont\color{encre!70!black}\fontsize{10}{13}\selectfont}
\else
  \addtokomafont{section}{\titrefont\color{encre}\fontsize{12.2}{15.5}\selectfont\raggedright}
  \addtokomafont{subsection}{\titrefont\color{encre!85!black}\fontsize{10.8}{13.5}\selectfont\raggedright}
  \addtokomafont{subsubsection}{\titrefont\color{encre!70!black}\fontsize{10}{13}\selectfont\raggedright}
\fi

% Espacement multiples de 4.5pt (tiers de ligne)
\RedeclareSectionCommand[
  beforeskip=18pt, afterskip=9pt
]{section}
\RedeclareSectionCommand[
  beforeskip=13.5pt, afterskip=4.5pt
]{subsection}
\RedeclareSectionCommand[
  beforeskip=9pt, afterskip=4.5pt
]{subsubsection}

\newcommand{\sectionCapacite}[2]{%
  \section{#1}\margeAppui{\textbf{Je sais\ldots} #2}%
}

% ===========================================================================
%  EN-TÊTES / PIEDS (scrlayer-scrpage)
% ===========================================================================
\RequirePackage[automark]{scrlayer-scrpage}
\clearpairofpagestyles
\ohead{\ifodd\value{page}\nxOnglet\fi\nxMiniMotif\kern0.7em\sffamily\fontsize{7.5}{10}\selectfont\color{encre}\headmark}
% Pied : numéro dans pastille chapcolor coin extérieur, Nexus Réussite côté intérieur
\newcommand{\nxFolioPastille}[1]{%
  \tikz\node[fill=chapcolor, text=white, circle,
    inner sep=3.6pt, font=\titrefont\small]{#1};}
\ofoot{\nxFolioPastille{\thepage}}
% La pastille est un cercle : son diamètre suit la largeur du folio, donc le
% nombre de chiffres. Mesuré sur la page 1, `\footheight` devenait trop court
% à la page 10, puis à la page 100 -- scrlayer l'allongeait alors lui-même, en
% le disant trois fois. La hauteur est ici mesurée une fois pour toutes sur la
% pastille la plus haute que le manuel puisse porter, celle de trois chiffres.
% Un manuel qui dépasserait 999 pages ferait légitimement reparaître l'alerte.
\newsavebox{\nxFolioPastilleLaPlusHaute}
\AddToHook{begindocument}{%
  % Le pied est composé sur une ligne : scrlayer y ajoute le support de la
  % ligne courante, dont la profondeur compte dans la hauteur exigée. La
  % mesure reprend donc exactement la même boîte.
  \sbox{\nxFolioPastilleLaPlusHaute}{\strut\nxFolioPastille{000}}%
  \setlength{\footheight}{%
    \dimexpr\ht\nxFolioPastilleLaPlusHaute
      +\dp\nxFolioPastilleLaPlusHaute\relax}%
}
\ifoot{\sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\addfontfeatures{LetterSpace=6}\MakeUppercase{Nexus Réussite}}

% ===========================================================================
%  LISTES (enumitem global)
% ===========================================================================
\RequirePackage{enumitem}
\setlist{itemsep=1pt, topsep=3pt, parsep=0pt, leftmargin=1.5em}
\setlist[enumerate,1]{label=\textcolor{chapcolor}{\textbf{\arabic*.}}}
\setlist[itemize,1]{label=\textcolor{chapcolor}{\small$\blacktriangleright$}}

% ===========================================================================
%  ENCADRÉS v4.1 — Kit « Éditorial premium » (tcolorbox, signatures visuelles)
% ===========================================================================
\RequirePackage[most,skins]{tcolorbox}
\RequirePackage{pifont}
\RequirePackage[normalem]{ulem}

% Label de titre commun
\newcommand{\nxboxtitle}[2]{{\titrefont\fontsize{8}{11}\selectfont
  \addfontfeatures{LetterSpace=8}\textcolor{#1}{\MakeUppercase{#2}}}}

% Base commune (géométrie et rythme partagés)
\tcbset{
  manuelbase/.style={
    enhanced, breakable, arc=2pt, boxrule=0pt,
    left=10pt, right=10pt, top=8pt, bottom=9pt,
    fonttitle=\titrefont, coltitle=white,
    before skip=15pt, after skip=15pt},
  ongletplein/.style={
    attach boxed title to top left={yshift=-2.4mm, xshift=6pt},
    boxed title style={boxrule=0pt, arc=2pt,
      left=8pt, right=8pt, top=3pt, bottom=3pt},
    top=11pt},
  ongletcontour/.style={
    coltitle=chapcolor,
    attach boxed title to top left={yshift=-2.4mm, xshift=6pt},
    boxed title style={boxrule=1pt, colframe=chapcolor,
      colback=white, arc=2pt, left=8pt, right=8pt, top=3pt, bottom=3pt},
    top=11pt},
}

% Alias v3 pour compatibilité
\tcbset{nxbase/.style={manuelbase, ongletplein}}

% ---- 1. DÉFINITION : onglet plein + fond teinté + barre gauche ----
\newcounter{nxDefNum}[chapter]
\newtcolorbox{nxdef}[1][]{manuelbase, ongletplein,
  colback=chapcolor!7,
  borderline west={3pt}{0pt}{chapcolor},
  colbacktitle=chapcolor,
  title={\nxboxtitle{white}{Définition~#1}}}

% ---- 2. THÉORÈME : cadre contour + bandeau plein ----
\newtcolorbox{nxthm}[1][]{manuelbase,
  colback=white, colframe=chapcolor, boxrule=1.2pt,
  colbacktitle=chapcolor, coltitle=white,
  title={\nxboxtitle{white}{Théorème~#1}},
  top=6pt, toptitle=3pt, bottomtitle=3pt, lefttitle=10pt}

% ---- 3. PROPRIÉTÉ : filet gauche + label en ligne ----
\newtcolorbox{nxprop}[1][]{manuelbase,
  colback=white,
  borderline west={2.5pt}{0pt}{chapcolor},
  left=12pt,
  before upper={\textcolor{chapcolor}{\titrefont Propriété~#1.}\ }}

% ---- CARTE (objectifs, contrat) ----
\newtcolorbox{nxcard}[1][]{manuelbase,
  colback=chapcolor!7,
  borderline west={3pt}{0pt}{chapcolor},
  left=12pt,
  before upper={\textcolor{chapcolor}{\titrefont #1}\ }}

% Raccourcis
\newcommand{\definition}[2][]{\begin{nxdef}[#1]#2\end{nxdef}}
\newcommand{\theoreme}[2][]{\begin{nxthm}[#1]#2\end{nxthm}}
\newcommand{\propriete}[2][]{\begin{nxprop}[#1]#2\end{nxprop}}
\newcommand{\exemple}[1]{\par\noindent\textbf{\textcolor{chapcolor}{Exemple.}} #1\par}
\newcommand{\contreexemple}[1]{\par\noindent\textbf{\textcolor{coulRetenir}{Contre-exemple.}} #1\par}
\newcommand{\demonstration}[1]{\par\noindent\textit{D\'emonstration.} #1\par}

% ---- ERREUR FRÉQUENTE : corail ----
\newtcolorbox{nxerr}{manuelbase, ongletplein,
  colback=coulRetenir!8, colframe=coulRetenir, boxrule=1.2pt,
  colbacktitle=coulRetenir,
  title={\nxboxtitle{white}{Erreur fréquente}}}
\newcommand{\erreurFrequente}[1]{\begin{nxerr}#1\end{nxerr}}

% ---- APPROFONDISSEMENT ★ : filet chapcolor, fond léger ----
\newtcolorbox{nxstar}{manuelbase, ongletplein,
  colback=chapcolor!6,
  borderline west={2.5pt}{0pt}{chapcolor!45},
  colbacktitle=chapcolor,
  title={\nxboxtitle{white}{Pour aller plus loin}}}
\newcommand{\approfondissement}[1]{\begin{nxstar}#1\end{nxstar}}

% ===========================================================================
%  FICHES MÉTHODES (filet nxOr, 6 rubriques)
% ===========================================================================
\newtcolorbox{fmbox}[2]{manuelbase, ongletcontour,
  colback=white, colframe=filetgris, boxrule=1.2pt,
  colbacktitle=white,
  title={\nxboxtitle{chapcolor}{Méthode #1 --- #2}}}
\newenvironment{fichemethode}[2]{\begin{fmbox}{#1}{#2}}{\end{fmbox}}
\newcommand{\quandUtiliser}[1]{\paragraph{Quand l'utiliser.}#1}
\newcommand{\pasApas}[1]{\paragraph{La méthode pas à pas.}#1}
\newcommand{\exempleRedige}[1]{\paragraph{Exemple rédigé.}#1}
\newcommand{\pieges}[1]{\paragraph{Les pièges.}#1}
\newcommand{\verifier}[1]{\paragraph{Vérifier son résultat.}#1}
\newcommand{\sEntrainer}[1]{\paragraph{S'entraîner.}#1}
\newcommand{\refExos}[1]{\textit{(renvois exercices #1)}}

% ===========================================================================
%  EXERCICES / CORRIGÉS (bandeau pleine largeur)
% ===========================================================================
\newcounter{exo}[chapter]
\RequirePackage{graphicx}
\newif\ifnxVersionProfesseur
\nxVersionProfesseurtrue
\input{gabarits/nexus-margin-rail.tex}

% Pictogrammes parcours (redéfinis par nexus-icons.tex si présent)
\newcommand{\parcoursUn}{}
\newcommand{\parcoursDeux}{}
\newcommand{\parcoursTrois}{}
\newcommand{\pictoOral}{}
\newcommand{\pictoPython}{}

\newenvironment{exercice}[3]{%
  \refstepcounter{exo}\par\medskip\noindent
  \tikz[baseline=(n.base)]\node[fill=chapcolor, text=white,
    rounded corners=2pt, inner xsep=7pt, inner ysep=3.5pt](n)
    {\titrefont\small Exercice \theexo};%
  \enskip
  \ifnum#2=1\relax\parcoursUn\fi
  \ifnum#2=2\relax\parcoursDeux\fi
  \ifnum#2=3\relax\parcoursTrois\fi
  \nxMarginRailNote{chrono}{%
    \sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\icnChrono~#3~min}%
  \ifnxVersionProfesseur
    \nxMarginRailNote{professor-id}{%
      \sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\texttt{#1}}%
  \fi
  \par\nopagebreak\smallskip
}{\par\medskip}

\newenvironment{corrige}[1]{%
  \par\medskip\noindent
  \tikz[baseline=(n.base)]\node[fill=chapcolor!70!black, text=white,
    rounded corners=2pt, inner xsep=7pt, inner ysep=3.5pt](n)
    {\titrefont\small Corrigé};%
  \ifnxVersionProfesseur
    \nxMarginRailNote{professor-id}{%
      \sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\texttt{#1}}%
  \fi
  \par\nopagebreak\smallskip
}{\par\medskip}

\newcommand{\baremeIndicatif}[1]{%
  \par\noindent{\sffamily\fontsize{7.5}{10}\selectfont\itshape Barème indicatif : #1}\par
}
\newcommand{\coupDePouce}[2]{%
  \par\noindent{\small\sffamily\textbf{Coup de pouce #1.} #2}\par
}
\newenvironment{coupdepouce}[1]{}{}

% ===========================================================================
%  ÉVALUATIONS
% ===========================================================================
\newenvironment{evaluation}[2]{%
  \par\bigskip\noindent
  \textbf{\textcolor{chapcolor}{\large\sffamily Évaluation%
    \ifnxVersionProfesseur~\texttt{#1}\fi}}\quad
  {\sffamily\fontsize{8}{10}\selectfont #2~min}\par\nopagebreak\medskip
}{\par\bigskip}

\newcommand{\exerciceEval}[4]{%
  \par\medskip\noindent\textbf{Exercice #1}\hfill\textit{#2 points --- #3}\par\nopagebreak\smallskip
}

% ===========================================================================
%  CODE PYTHON (listings avec JetBrains Mono)
% ===========================================================================
\RequirePackage{listings}

% Réglages globaux listings. Le commentaire annonçait « upquote » : il n'y en
% avait pas, et il n'en fallait pas -- `upquote` ne change rien ici, la
% transformation du guillemet droit venait de la FONTE et se règle là où la
% fonte est chargée.
\lstset{
  columns=fullflexible,
  keepspaces=true,
  breaklines=true,
  showstringspaces=false,
  tabsize=4,
  literate=%
    {é}{{\'{e}}}1 {è}{{\`{e}}}1 {ê}{{\^{e}}}1 {ë}{{\"{e}}}1
    {à}{{\`{a}}}1 {â}{{\^{a}}}1 {ù}{{\`{u}}}1 {û}{{\^{u}}}1
    {î}{{\^{i}}}1 {ô}{{\^{o}}}1 {ç}{{\c{c}}}1
    {É}{{\'{E}}}1 {È}{{\`{E}}}1 {À}{{\`{A}}}1
    {—}{{---}}1,
}

\lstdefinestyle{nxpy}{%
  language=Python,
  basicstyle=\ttfamily\fontsize{8.5}{11}\selectfont,
  keywordstyle=\color{chapcolor}\bfseries,
  commentstyle=\color{encre!55}\itshape,
  stringstyle=\color{coulHistoire},
  frame=l,
  framerule=1pt,
  rulecolor=\color{coulCode!30},
  backgroundcolor=\color{grisdoux},
  numbers=left,
  numberstyle=\ttfamily\fontsize{6}{8}\selectfont\color{encre!45},
  numbersep=8pt,
  xleftmargin=18pt,
  aboveskip=9pt,
  belowskip=9pt,
}
\lstnewenvironment{python}{\lstset{style=nxpy}}{}

% `\lstinputlisting` n'appliquait AUCUN style : le `\lstset` global ne fixe pas
% de `basicstyle`, si bien qu'un programme lu depuis un fichier heritait de la
% fonte du texte courant. Les dix-sept programmes Python inclus par fichier
% etaient donc composes en Pagella -- serif, proportionnelle, docstrings en
% italique -- et la fonte du texte applique `Ligatures=TeX` : les guillemets
% droits du code y devenaient des guillemets courbes. Le meme defaut que dans
% les blocs `python`, mais sur un autre chemin, invisible tant qu'on ne
% comparait pas la source a la page.
%
% Le style ne peut pas etre pose dans le `\lstset` global : `\lstinline` le
% prendrait aussi et composerait le code en ligne a 8,5 pt, encadre et
% numerote, au milieu d'un paragraphe. Il est donc applique la ou il a du sens,
% sur le programme affiche, dans un groupe qui le confine.
\let\nxOrigLstInputListing\lstinputlisting
\renewcommand{\lstinputlisting}[2][]{%
  \begingroup
    \lstset{style=nxpy}%
    \nxOrigLstInputListing[#1]{#2}%
  \endgroup}

% Code en ligne
\newcommand{\code}[1]{{\ttfamily\color{coulCode}#1}}

% Protection de \lstinline contre babel-french (NoAutoSpacing).
% Le code en ligne est insecable : un identifiant snake_case a rallonge
% (montant_paye, cotisations_payees) occupe une largeur que le paragraphe ne
% peut ni couper ni compenser, et laisse une ligne trop lache. On autorise la
% coupure APRES le souligne, sans trait d'union — un identifiant coupe reste
% lisible, la convention du code l'exige.
\let\nxOrigLstinline\lstinline
\renewcommand{\lstinline}{\NoAutoSpacing
  \lstset{literate={\_}{{\_\allowbreak}}1}\nxOrigLstinline}

% ===========================================================================
%  TABLES (booktabs)
% ===========================================================================
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{eurosym}
\newif\ifnxCompactTables
\ifdefined\nxVBaseCompatibility
  \nxCompactTablesfalse
\else
  \nxCompactTablestrue
\fi
\newcommand{\nxApplyCompactTableStyle}{%
  \ifnxCompactTables
    \footnotesize
    \setlength{\tabcolsep}{3.4pt}%
    \renewcommand{\arraystretch}{0.94}%
  \fi
}
\AtBeginEnvironment{tabular}{\nxApplyCompactTableStyle}
\AtBeginEnvironment{tabularx}{\nxApplyCompactTableStyle}

% ===========================================================================
%  FIGURES (définies dans nexus-figures.tex ; fallback si absent)
% ===========================================================================
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc}

% ===========================================================================
%  OUVERTURE DE CHAPITRE v4.1 — Bandeau accent + numéro géant + décor TikZ
% ===========================================================================
% nxChapNum est défini dans nexus-signatures.tex
\usetikzlibrary{backgrounds}

\newlength{\nxBandHeight}
\setlength{\nxBandHeight}{0.48\paperheight}
\newsavebox{\nxTitreChapBox}
\newlength{\nxTitreChapHeight}

% Usage : \ouverturechapitre[motif]{Titre}{capacites}{accroche}{temps}
\newcommand{\ouverturechapitre}[5][motifGenerique]{%
  % La coupure vient AVANT toute autre chose, et notamment avant
  % \addcontentsline. Sans elle, TeX composait encore la derniere page du
  % chapitre precedent au moment ou l'entree de sommaire etait ecrite : le
  % sommaire et les signets annonçaient donc une page qui n'etait pas
  % l'ouverture. Trois chapitres sur dix cote eleve et six sur dix cote
  % professeur portaient un folio faux d'exactement une page ; il n'en reste
  % aucun.
  %
  % La pagination, elle, CHANGE : mesure du 2026-09-03 sur les deux variantes,
  % 359 -> 363 pages cote eleve et 633 -> 635 cote professeur. L'ouverture
  % disputait bel et bien sa page a la fin du chapitre precedent, et
  % `\thispagestyle{empty}` s'appliquait alors a cette page-la plutot qu'a
  % l'ouverture. Ce changement de baseline visuelle est ratifie :
  % audit/HUMAN_DECISION_1SPE_VISUAL_BASELINE_PAGINATION_2026-09-03.json, et
  % il est prouve page par page par
  % scripts/build_1spe_pagination_baseline_ratification.py.
  %
  % `\cleardoublepage` est explicitement REFUSE ici : aucun contrat n'exige
  % qu'un chapitre demarre sur une page impaire.
  \clearpage
  % La page d'ouverture porte sa propre rubrique. Sans cette ligne elle
  % heritait de la derniere rubrique du chapitre PRECEDENT : huit ouvertures
  % sur onze affichaient l'onglet « Remediation ».
  \rubrique{Ouverture}%
  \stepcounter{nxChapNum}%
  \refstepcounter{chapter}%
  % \refstepcounter pose l'ancre « chapter.N » : l'entrée de sommaire qui suit
  % a donc déjà sa destination, il ne faut pas lui en poser une seconde.
  \global\nxAncreChapitreFraichetrue
  \chaptermark{#2}%
  \ifdefined\nxVBaseCompatibility
    \addcontentsline{toc}{chapter}{#2}%
  \else
    \addcontentsline{toc}{chapter}{\protect\numberline{\thechapter}#2}%
  \fi
  % --- PAGE VISUELLE (recto, bandeau accent haut 56%) ---
  \thispagestyle{empty}%
  \ifdefined\nxVBaseCompatibility\else
    % Hauteur réelle du titre (1 ou plusieurs lignes) : l'étiquette
    % « Chapitre N » se place au-dessus du titre replié.
    \sbox{\nxTitreChapBox}{\begin{minipage}{0.60\paperwidth}%
      \titrefont\fontsize{27}{31}\selectfont#2\end{minipage}}%
    \setlength{\nxTitreChapHeight}{\ht\nxTitreChapBox}%
    \addtolength{\nxTitreChapHeight}{\dp\nxTitreChapBox}%
  \fi
  \noindent\begin{tikzpicture}[remember picture, overlay]
    % Bandeau plein accent (haut de page), débordé jusqu'à la BleedBox sur les
    % trois bords qu'il touche après coupe
    \fill[chapcolor]
      ([shift={(-\nxFondPerduDim,\nxFondPerduDim)}]current page.north west)
      rectangle
      ([shift={(\nxFondPerduDim,-\nxBandHeight)}]current page.north east);
    % Décor TikZ du chapitre (dans le bandeau, moitié droite)
    \csname #1\endcsname
    % Étiquette matière · niveau
    \ifdefined\nxVBaseCompatibility
      \node[anchor=north west, text=white, opacity=0.9,
            font=\titrefont\small, inner sep=0pt]
        at ([shift={(20mm,-17mm)}]current page.north west)
        {\MakeUppercase{\nexus@matiere}\ \ $\cdot$\ \ \nexus@niveau};
    \else
      \node[anchor=north west, text=white, opacity=0.9,
            font=\titrefont\small, inner sep=0pt]
        at ([shift={(14mm,-16mm)}]current page.north west)
        {\MakeUppercase{\nexus@matiere}\ \ $\cdot$\ \ \nexus@niveau};
    \fi
    % Numéro géant fantôme
    \node[anchor=south west, text=white, opacity=0.15, inner sep=0pt,
          font=\titrefont\fontsize{210}{210}\selectfont]
      at ([shift={(16mm,-\nxBandHeight+2mm)}]current page.north west)
      {\ifnum\value{chapter}>0 \thechapter\fi};
    % « Chapitre N »
    \ifdefined\nxVBaseCompatibility
      \node[anchor=south west, text=white, align=left, inner sep=0pt,
            font=\titrefont]
        at ([shift={(20mm,-\nxBandHeight+24mm)}]current page.north west)
        {\fontsize{15}{15}\selectfont\MakeUppercase{Chapitre~\thechapter}};
    \else
      \node[anchor=south west, text=white, align=left, inner sep=0pt,
            font=\titrefont]
        at ([shift={(14mm,-\nxBandHeight+13mm+\nxTitreChapHeight+6mm)}]
          current page.north west)
        {\fontsize{15}{15}\selectfont\MakeUppercase{Chapitre~\thechapter}};
    \fi
    % Titre géant
    \ifdefined\nxVBaseCompatibility
      \node[anchor=south west, text=white, align=left, inner sep=0pt,
            text width=0.66\paperwidth,
            font=\titrefont\fontsize{34}{40}\selectfont]
        at ([shift={(20mm,-\nxBandHeight+13mm)}]current page.north west)
        {#2\par};
    \else
      \node[anchor=south west, text=white, align=left, inner sep=0pt,
            text width=0.60\paperwidth,
            font=\titrefont\fontsize{27}{31}\selectfont]
        at ([shift={(14mm,-\nxBandHeight+13mm)}]current page.north west)
        {#2\par};
    \fi
  \end{tikzpicture}\par
  % Espace sous le bandeau. La réserve suit le bandeau : le contenu commence
  % 2,6 mm sous son bord inférieur, la même respiration qu'avant la refonte.
  \vspace*{\dimexpr\nxBandHeight-\topskip-1.8cm\relax}%
  % Objectifs / capacités sous le bandeau
  % `breakable` est indispensable : un chapitre de seize capacités remplit
  % plus d'une page. Sans lui, tcolorbox tronque silencieusement la liste --
  % TSPE-GEOMETRIE-ESPACE perdait ses objectifs C15 et C16, avec un simple
  % « Overfull \vbox » au journal et un PDF d'apparence correcte.
  \begin{tcolorbox}[enhanced, breakable, frame hidden, boxrule=0pt, arc=3pt,
    colback=chapcolor!7,
    borderline west={3pt}{0pt}{chapcolor},
    left=12pt, right=12pt, top=7pt, bottom=7pt,
    before upper={\textcolor{chapcolor}{\titrefont\large
      Objectifs --- Capacités attendues}\par\vspace{3pt}}]
    % Réglage de liste compact de la charte, celui-là même que la grille
    % d'exercices emploie. Les capacités sont la seule partie de l'ouverture
    % qui grandit avec le chapitre : c'est là que l'espacement doit être
    % canonique et serré, pas ailleurs.
    \setlist{itemsep=0pt,topsep=1pt,parsep=0pt,partopsep=0pt,leftmargin=1.35em}%
    #3%
  \end{tcolorbox}%
  \vspace{0.25cm}%
  \begin{nxcard}%
    #4%
    % Les temps estimés restent sur l'ouverture, dans le bloc d'information
    % qu'ils qualifient. Isolés sous la carte, ils formaient un paragraphe de
    % vingt-neuf caractères que la coupure de page emportait seul : cinq
    % ouvertures sur dix ne rejetaient QUE cette ligne sur une seconde page.
    \par\vspace{4pt}%
    \noindent\textcolor{chapcolor}{\titrefont Temps estimés :} #5%
  \end{nxcard}%
  \par\vfill
  \clearpage
}

% ===========================================================================
%  EXTENSIONS (chargées si présentes, silencieuses sinon)
% ===========================================================================
\IfFileExists{gabarits/common/nexus-icons.tex}{\input{gabarits/common/nexus-icons.tex}}{%
  \IfFileExists{gabarits/nexus-icons.tex}{\input{gabarits/nexus-icons.tex}}{%
    \ClassWarning{nexus-manuel}{Nexus asset missing: icons}}}

\IfFileExists{gabarits/maths/nexus-maths.sty}{\input{gabarits/maths/nexus-maths.sty}}{%
  \IfFileExists{gabarits/nexus-figures.tex}{\input{gabarits/nexus-figures.tex}}{%
    \ClassWarning{nexus-manuel}{Nexus asset missing: figures}%
    \newcounter{nxfig}[chapter]
    \newenvironment{nxfigure}[2][0.9\linewidth]{%
      \refstepcounter{nxfig}\par\medskip\begin{center}\begin{minipage}{##1}\centering
      \def\nxfigcaption{##2}}{%
      \par\smallskip{\sffamily\fontsize{8}{10}\selectfont\color{nxGris}%
        \textbf{Figure \thenxfig} --- \nxfigcaption}%
      \end{minipage}\end{center}\medskip}}}

\IfFileExists{gabarits/common/nexus-signatures.tex}{\input{gabarits/common/nexus-signatures.tex}}{%
  \IfFileExists{gabarits/nexus-signatures.tex}{\input{gabarits/nexus-signatures.tex}}{%
    \ClassWarning{nexus-manuel}{Nexus asset missing: signatures}\newcounter{nxChapNum}}}

\IfFileExists{gabarits/common/nexus-code.tex}{\input{gabarits/common/nexus-code.tex}}{%
  \IfFileExists{gabarits/nexus-code.tex}{\input{gabarits/nexus-code.tex}}{}}

\IfFileExists{gabarits/nsi/nexus-nsi.sty}{\input{gabarits/nsi/nexus-nsi.sty}}{%
  \IfFileExists{gabarits/nexus-figures-nsi.tex}{\input{gabarits/nexus-figures-nsi.tex}}{}}


% ===========================================================================
%  V5 ITERATION 2 EXTENSIONS & COMPATIBILITY LAYER
% ===========================================================================
\def\nxVBaseCompatibility{1}


% ===========================================================================
%  MESURE — la v5 ne doit RIEN retirer a la justification de la v4.1
% ===========================================================================
% La branche compatibilite de nexus-manuel.cls porte la marge exterieure a
% 4,8 cm et la colonne de marge a 3,5 cm. La justification tombe alors de
% 14,6 a 14,2 cm : quatre millimetres de moins que la mesure contre laquelle
% les 2 751 objets de la collection ont ete ecrits et relus.
%
% Ces 4 mm ne sont pas theoriques. Le corpus de NSI porte des fragments de
% code en ligne que \lstinline et \texttt composent en boites insecables — un
% schema de relation de 60 caracteres dans TNSI-BASES-DE-DONNEES, un
% dictionnaire en comprehension de 46 caracteres dans 1NSI-TYPES-CONSTRUITS.
% A 14,2 cm ils ne trouvent plus de coupure acceptable et laissent des lignes
% trop laches, que le gate de diagnostics rejette. Compenser encadre par
% encadre ne marche pas : reduire leurs marges internes deplace le probleme
% et l'aggrave parfois.
%
% On rend donc les 4 mm. La colonne de marge reste plus large qu'en v4.1
% (3,1 cm contre 2,8), et l'onglet lateral, dessine au bord de page par-dessus
% la marge, garde toute sa place.
\geometry{a4paper,
  top=2.4cm, bottom=2.6cm,
  inner=2.0cm, outer=4.4cm,
  marginparwidth=3.1cm, marginparsep=0.55cm,
  headsep=0.7cm}

% La v4.1 reserve \emergencystretch a son propre mode (nexus-manuel.cls, garde
% \ifdefined\nxVBaseCompatibility\else) : la v5 en etait donc privee, alors
% qu'un identifiant en ligne insecable y deborde tout aussi bien.
\emergencystretch=3em
\tolerance=1500

% Conserver l'unique voie autorisée vers la vraie marge. Les gabarits à marge
% nulle redirigent leurs notes vers le bas du bloc au lieu de l'appeler.
\let\nxVOriginalMarginnote\marginnote
\newif\ifnxVNoMargin
\nxVNoMarginfalse
\newcount\nxVMultiColDepth
\nxVMultiColDepth=0
\AtBeginEnvironment{multicols}{\global\advance\nxVMultiColDepth\@ne}
\AtEndEnvironment{multicols}{\global\advance\nxVMultiColDepth\m@ne}
\newcommand{\nxVBottomNotes}{}
\newcommand{\nxVStoreBottomNote}[1]{%
  \typeout{NEXUS-V5-MARGINNOTE-REDIRECTED}%
  \g@addto@macro\nxVBottomNotes{\nxVBottomNote{#1}}%
}
\newcommand{\nxVBottomNote}[1]{%
  \par\smallskip\noindent
  {\sffamily\fontsize{7}{9}\selectfont\color{encre!70}%
    \textcolor{chapcolor}{\rule{0.4pt}{2\baselineskip}}\hspace{5pt}%
    \begin{minipage}[t]{\dimexpr\linewidth-8pt\relax}#1\end{minipage}}%
}
\newcommand{\nxVFlushBottomNotes}{%
  \ifx\nxVBottomNotes\@empty\else
    \par\medskip\nxVBottomNotes
  \fi
  \global\let\nxVBottomNotes\@empty
}
\NewDocumentCommand{\nxVEmitOriginalMarginnote}{m o}{%
  \ifnum\nxVMultiColDepth>0\relax
    \typeout{NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED}%
  \fi
  \IfNoValueTF{#2}{\nxVOriginalMarginnote{#1}}{%
    \nxVOriginalMarginnote{#1}[#2]}%
}
\RenewDocumentCommand{\marginnote}{m o}{%
  \ifnxVNoMargin
    \nxVStoreBottomNote{#1}%
  \else
    \ifnum\nxVMultiColDepth>0\relax
      \nxVStoreBottomNote{#1}%
    \else
      \IfNoValueTF{#2}{\nxVEmitOriginalMarginnote{#1}}{%
        \nxVEmitOriginalMarginnote{#1}[#2]}%
    \fi
  \fi
}

% ===========================================================================
%  MARK DÉDIÉ DE RUBRIQUE — résolu par la page au moment du shipout
% ===========================================================================
\newmarks\nxRubriqueMarks
\newcommand{\rubrique}[1]{\marks\nxRubriqueMarks{#1}}
\newcommand{\nxRubriquePage}{%
  \ifx\firstmarks\nxRubriqueMarks\@empty
    \botmarks\nxRubriqueMarks
  \else
    \firstmarks\nxRubriqueMarks
  \fi
}
\newif\ifnxVSuppressTab
\nxVSuppressTabfalse

% ===========================================================================
%  ONGLETS LATÉRAUX DE RUBRIQUE
% ===========================================================================
% Bandeau vertical 12mm au bord extérieur, couleur accent pour rubrique active
% Position verticale = f(chapter) → index de pouce
\newsavebox{\nxVOngletTextBox}
\newlength{\nxVOngletLength}
\newlength{\nxVOngletHalfLength}
\newcommand{\nxOngletRubrique}{%
  \ifnxVSuppressTab\else
  \begingroup
  \sbox{\nxVOngletTextBox}{{\titrefont\fontsize{6}{6}\selectfont
    \color{white}\MakeUppercase{\nxRubriquePage}}}%
  \setlength{\nxVOngletLength}{%
    \dimexpr\wd\nxVOngletTextBox+6mm\relax}%
  \ifdim\nxVOngletLength<16mm
    \setlength{\nxVOngletLength}{16mm}\fi
  \setlength{\nxVOngletHalfLength}{\nxVOngletLength}%
  \divide\nxVOngletHalfLength by 2
  \begin{tikzpicture}[remember picture, overlay]
    \pgfmathsetmacro{\ongletY}{-25 - (\value{chapter}-1)*18}
    \ifodd\value{page}%
      % Épaisseur extérieure contractuelle : 12 mm visibles sur la page
      % (spec 2026-07-20) ; le +1 mm hors page garde l'arête de coupe nette.
      \path[fill=encre,rounded corners=1.1mm]
        ([xshift=-12mm,yshift=\ongletY mm]current page.north east)
        rectangle
        ([xshift=1mm,yshift=\ongletY mm-\nxVOngletLength]
          current page.north east);
      \draw[chapcolor,line width=0.7pt]
        ([xshift=-12mm,yshift=\ongletY mm]current page.north east)
        --
        ([xshift=-12mm,yshift=\ongletY mm-\nxVOngletLength]
          current page.north east);
      \node[rotate=90,anchor=center,inner sep=0pt]
        at ([yshift=\ongletY mm-\nxVOngletHalfLength,
             xshift=-6mm]current page.north east)
        {\usebox{\nxVOngletTextBox}};
    \else
      \path[fill=encre,rounded corners=1.1mm]
        ([xshift=-1mm,yshift=\ongletY mm]current page.north west)
        rectangle
        ([xshift=12mm,yshift=\ongletY mm-\nxVOngletLength]
          current page.north west);
      \draw[chapcolor,line width=0.7pt]
        ([xshift=12mm,yshift=\ongletY mm]current page.north west)
        --
        ([xshift=12mm,yshift=\ongletY mm-\nxVOngletLength]
          current page.north west);
      \node[rotate=-90,anchor=center,inner sep=0pt]
        at ([yshift=\ongletY mm-\nxVOngletHalfLength,
             xshift=6mm]current page.north west)
        {\usebox{\nxVOngletTextBox}};
    \fi
  \end{tikzpicture}%
  \endgroup
  \fi
}
\let\nxOnglet\nxOngletRubrique

% Injecter l'onglet dans les en-têtes
\ohead{\nxOngletRubrique\nxMiniMotif\kern0.7em\sffamily\fontsize{7.5}{10}\selectfont\color{encre}%
  \nxRubriquePage}

% ===========================================================================
%  PAGE BLANCHE DÉCORÉE — vecteurs seuls, aucune couche texte
% ===========================================================================
\newpairofpagestyles{blanche}{\clearpairofpagestyles}
\newcommand{\nxPageBlancheDecoree}{%
  \thispagestyle{blanche}%
  \begin{tikzpicture}[remember picture,overlay]
    \foreach \i in {0,...,8}{%
      \draw[chapcolor,opacity=0.04,line width=0.7pt]
        ([xshift=\i*28mm,yshift=18mm]current page.south west)
        -- ++(24mm,24mm) -- ++(-24mm,24mm) -- cycle;
      \draw[chapcolor,opacity=0.04,line width=0.7pt]
        ([xshift=\i*28mm,yshift=158mm]current page.south west)
        -- ++(24mm,24mm) -- ++(-24mm,24mm) -- cycle;
    }%
  \end{tikzpicture}%
  \noindent\vbox to \textheight{\vfil}\par
  \clearpage
}
% NX-V5-END-PAGE-BLANCHE

% ===========================================================================
%  RUPTURE DE RUBRIQUE — expédier, blanche éventuelle, puis écrire le mark
% ===========================================================================
\newcommand{\nxRubriqueMajeure}[2][]{%
  \clearpage
  \ifstrequal{#1}{blanche}{\nxPageBlancheDecoree}{}%
  \rubrique{#2}%
}
% NX-V5-END-RUBRIQUE-MAJEURE

\newcommand{\debutrubrique}[1]{%
  \nxRubriqueMajeure{#1}%
  \section*{\textcolor{chapcolor}{\MakeUppercase{#1}}}%
  \addcontentsline{toc}{section}{#1}%
}

% ===========================================================================
%  OUVERTURE v5 — quatre contenus v4.1 inchangés + sommaire des neuf temps
% ===========================================================================
\newcommand{\nxTempsChapitre}[2]{%
  \noindent\sffamily\fontsize{6.5}{8}\selectfont
  #1\nobreak\leaders\hbox{\kern1.5pt.\kern1.5pt}\hfill\nobreak #2\par
}
\newcommand{\nxSommaireChapitreV}{%
  \nxTempsChapitre{Ouverture}{1}%
  \nxTempsChapitre{Diagnostic}{2}%
  \nxTempsChapitre{Activités}{3}%
  \nxTempsChapitre{Cours}{5}%
  \nxTempsChapitre{Méthodes}{9}%
  \nxTempsChapitre{Entraînement}{13}%
  \nxTempsChapitre{TD}{23}%
  \nxTempsChapitre{Auto-évaluation}{27}%
  \nxTempsChapitre{Évaluation}{31}%
}
% NX-V5-END-SOMMAIRE

\newcommand{\nxOuvertureSupplementV}{%
  \begin{tikzpicture}[remember picture,overlay]
    \node[anchor=north east,fill=white,fill opacity=0.94,text opacity=1,
      rounded corners=2pt,inner sep=7pt,text=encre]
      at ([xshift=-17mm,yshift=-18mm]current page.north east)
      {\begin{minipage}{55mm}
        {\titrefont\fontsize{7}{9}\selectfont\color{chapcolor}
          LES 9 TEMPS DU CHAPITRE}\par\smallskip
        \nxSommaireChapitreV
      \end{minipage}};
  \end{tikzpicture}%
  \nxOngletRubrique
}

\newcommand{\ouverturechapitreV}[5][motifGenerique]{%
  \rubrique{Ouverture}%
  \AddToHookNext{shipout/foreground}{\nxOuvertureSupplementV}%
  \ouverturechapitre[#1]{#2}{#3}{#4}{#5}%
}

% NX-V5-COURS-START
% ===========================================================================
%  COURS v5 — registre de notes, marge active et pagination sûre
% ===========================================================================
\RequirePackage{needspace}
\RequirePackage{placeins}
\RequirePackage{flafter}
\newlength{\nxCoursGrid}
\setlength{\nxCoursGrid}{4.5pt}

\newcommand{\nxCoursEnsureRegister}[1]{%
  \ifcsname nxCoursAnnotations@#1\endcsname\else
    \expandafter\gdef\csname nxCoursAnnotations@#1\endcsname{}%
  \fi
}
\newcommand{\coursVocab}[3]{%
  \nxCoursEnsureRegister{#1}%
  \expandafter\g@addto@macro\csname nxCoursAnnotations@#1\endcsname{%
    \nxCoursVocabNote{#2}{#3}}%
}
\newcommand{\coursRenvoi}[3]{%
  \nxCoursEnsureRegister{#1}%
  \expandafter\g@addto@macro\csname nxCoursAnnotations@#1\endcsname{%
    \nxCoursRenvoiNote{#2}{#3}}%
}

\newcommand{\nxCoursNoteBase}[1]{%
  \par\noindent
  \begin{minipage}{\linewidth}%
    \fontsize{7.5}{10}\selectfont\sffamily\color{encre!72}%
    \rule{0.4pt}{3\baselineskip}\hspace{4pt}%
    \begin{minipage}[t]{\dimexpr\linewidth-7pt\relax}#1\end{minipage}%
  \end{minipage}%
  \par\vspace{9pt}% deux pas de la grille 4.5pt
}
\newcommand{\nxCoursVocabNote}[2]{%
  \nxCoursNoteBase{{\titrefont\color{chapcolor}VOCABULAIRE}\par
    {\bfseries #1}\par #2}%
}
\newcommand{\nxCoursRenvoiNote}[2]{%
  \nxCoursNoteBase{{\titrefont\color{chapcolor}RENVOI}\par
    Méthode~#1\enspace\textperiodcentered\enspace p.~#2}%
}
\newcommand{\nxCoursAnnotations}[1]{%
  \ifcsname nxCoursAnnotations@#1\endcsname
    \nxVOriginalMarginnote{%
      \begin{minipage}{\marginparwidth}%
        \csname nxCoursAnnotations@#1\endcsname
      \end{minipage}}[4.5pt]%
  \fi
}
\newcommand{\nxCoursPageBreak}{\par\penalty-10000\relax}
\newcommand{\nxCoursAppuiNote}[1]{%
  \par\noindent
  \begin{minipage}{\linewidth}%
    \sffamily\fontsize{8}{10}\selectfont\color{encre!72}%
    \textcolor{chapcolor}{\rule{0.4pt}{2\baselineskip}}\hspace{6pt}%
    \begin{minipage}[t]{\dimexpr\linewidth-9pt\relax}%
      {\titrefont\color{chapcolor}POINT D'APPUI}\par #1%
    \end{minipage}%
  \end{minipage}%
  \par\vspace{13.5pt plus 4.5pt}%
}
\newcommand{\nxCoursMargeAppui}[1]{%
  \nxCoursAppuiNote{#1}%
}
\newenvironment{nxCoursFigure}[2][0.9\linewidth]{%
  \refstepcounter{nxfig}%
  \def\nxfigcaption{#2}%
  \def\nxfigdetail{}%
  \renewcommand{\nxcaption}[1]{\def\nxfigdetail{##1}}%
  \begin{figure}[!t]
  \centering
  \begin{minipage}{#1}\centering
  \pgfplotsset{nexus/.append style={height=1.11\linewidth}}%
}{%
  \par\smallskip
  {\sffamily\fontsize{8}{10}\selectfont\color{nxGris}%
    \textbf{Figure \thenxfig} --- \nxfigcaption
    \ifx\nxfigdetail\@empty\else.\space\nxfigdetail\fi}%
  \end{minipage}%
  \end{figure}%
}

\NewDocumentEnvironment{coursV}{}{%
  \newgeometry{top=2.4cm,bottom=2.6cm,inner=2.0cm,outer=4.8cm,
    marginparwidth=3.5cm,marginparsep=0.6cm,headsep=0.7cm}%
  \let\nxCoursRealClearpage\clearpage
  \flushbottom
  \setlength{\parskip}{4.5pt plus 2.25pt minus 1.125pt}%
  \tcbset{manuelbase/.append style={%
    before skip=13.5pt plus 2.25pt minus 2.25pt,
    after skip=13.5pt plus 2.25pt minus 2.25pt}}%
  \let\erreurFrequente\nxCoursErreurFrequente
  \let\approfondissement\nxCoursApprofondissement
  \let\clearpage\nxCoursPageBreak
  \let\nxfigure\nxCoursFigure
  \let\endnxfigure\endnxCoursFigure
  \let\margeAppui\nxCoursMargeAppui
  \let\nxCoursSectionOriginal\section
  \RenewDocumentCommand{\section}{s o m}{%
    \IfBooleanTF{##1}{%
      \nxCoursSectionOriginal*{##3}%
    }{%
      \IfNoValueTF{##2}{\nxCoursSectionOriginal{##3}}{%
        \nxCoursSectionOriginal[##2]{##3}}%
    }%
    \nxCoursAnnotations{##3}%
  }%
}{%
  \FloatBarrier
  \nxCoursPageBreak
  \let\clearpage\nxCoursRealClearpage
  \restoregeometry
}

\newcounter{nxErreurPage}
\AddToHook{shipout/after}{\setcounter{nxErreurPage}{0}}
\newtcolorbox{nxerrcoursv}{manuelbase,ongletplein,unbreakable,
  colback=coulRetenir!8,colframe=coulRetenir,boxrule=1.2pt,
  colbacktitle=coulRetenir,
  before skip=13.5pt plus 4.5pt,after skip=13.5pt plus 4.5pt,
  fontupper={\setlength{\baselineskip}{13.5pt plus 4.5pt}},
  title={\nxboxtitle{white}{Erreur fréquente}}}
\newtcolorbox{nxstarcoursv}{manuelbase,ongletplein,unbreakable,
  colback=chapcolor!6,
  borderline west={2.5pt}{0pt}{chapcolor!45},
  colbacktitle=chapcolor,
  before skip=13.5pt plus 4.5pt,after skip=13.5pt plus 4.5pt,
  fontupper={\setlength{\baselineskip}{13.5pt plus 4.5pt}},
  title={\nxboxtitle{white}{Pour aller plus loin}}}
\newcommand{\nxCoursErreurFrequente}[1]{%
  \stepcounter{nxErreurPage}%
  \ifnum\value{nxErreurPage}>2\relax
    \clearpage
    \setcounter{nxErreurPage}{1}%
  \fi
  \Needspace{30\nxCoursGrid}% 135 pt, bloc insécable et respiration de grille
  \begin{nxerrcoursv}#1\end{nxerrcoursv}%
}

\newcommand{\nxCoursApprofondissement}[1]{%
  \FloatBarrier
  \Needspace{\dimexpr3\baselineskip+18pt\relax}% titre et deux lignes minimum
  \begin{nxstarcoursv}#1\end{nxstarcoursv}%
}
% NX-V5-COURS-END

% ===========================================================================
%  GRILLE EXERCICES — 2 colonnes 68mm, gouttière 6mm
% ===========================================================================
\RequirePackage{multicol}
\newcommand{\nxVFullDiamond}{%
  \tikz[baseline=-0.12em]{%
    \fill[chapcolor] (0,0) -- (0.24em,0.34em) -- (0.48em,0)
      -- (0.24em,-0.34em) -- cycle;}%
}
\newcommand{\nxVOutlineDiamond}{%
  \tikz[baseline=-0.12em]{%
    \draw[chapcolor,line width=0.45pt] (0,0) -- (0.24em,0.34em)
      -- (0.48em,0) -- (0.24em,-0.34em) -- cycle;}%
}
\newcommand{\icnCalculatrice}[1][chapcolor]{%
  \tikz[baseline=-0.15em]{%
    \draw[#1,line width=0.7pt,rounded corners=0.7pt]
      (-0.33em,-0.42em) rectangle (0.33em,0.42em);
    \draw[#1,line width=0.55pt] (-0.22em,0.16em) rectangle (0.22em,0.31em);
    \foreach \x in {-0.18em,0em,0.18em}{%
      \foreach \y in {-0.22em,0em}{\fill[#1] (\x,\y) circle (0.035em);}%
    }%
  }%
}
\expandafter\def\csname nxVGridPicto@python\endcsname{%
  \icnPython[chapcolor]\,{\sffamily\fontsize{5.5}{6.5}\selectfont Python}%
}
\expandafter\def\csname nxVGridPicto@calculatrice\endcsname{%
  \icnCalculatrice[chapcolor]\,{\sffamily\fontsize{5.5}{6.5}\selectfont Calculatrice}%
}
\newcommand{\nxVGridPicto}[1]{%
  \edef\nxVGridPictoName{#1}%
  \ifcsname nxVGridPicto@\nxVGridPictoName\endcsname
    \csname nxVGridPicto@\nxVGridPictoName\endcsname
  \fi
}
\newenvironment{nxVGridExercise}[3]{%
  \edef\nxVThisGridPage{\csname nxv@page@#1\endcsname}%
  \ifnum\nxVThisGridPage>\nxVGridPage\relax
    \newpage
    \global\edef\nxVGridPage{\nxVThisGridPage}%
  \fi
  \refstepcounter{exo}\par\vspace{2pt}\noindent
  \ifcsname nxv@number@#1\endcsname\else
    \PackageError{nexus-manuel-v5}{META exercice absente}{#1}%
  \fi
  \csname nxv@label@#1\endcsname
  \tikz[baseline=(n.base)]\node[fill=chapcolor,text=white,
    rounded corners=2pt,inner xsep=5pt,inner ysep=2.5pt](n)
    {\titrefont\scriptsize\csname nxv@number@#1\endcsname};%
  \enskip
  \csname nxv@difficulty@#1\endcsname
  \enskip
  {\sffamily\fontsize{5.5}{6.5}\selectfont\color{encre!52}%
    \icnChrono[encre!52]\,\csname nxv@duration@#1\endcsname\,min}%
  \hfill\nxVGridPicto{\csname nxv@picto@#1\endcsname}%
  \edef\nxVGridReference{\csname nxv@reference@#1\endcsname}%
  \par\nopagebreak\vspace{1pt}
}{%
  \par\nopagebreak\vspace{1pt}
  {\sffamily\fontsize{6}{7.2}\selectfont\color{chapcolor}%
    \nxVGridReference}%
  \par\vspace{3pt}
}
\newenvironment{grilleExercices}{%
  \nxRubriqueMajeure{Exercices}%
  \newgeometry{top=2.4cm, bottom=2.6cm, inner=2.0cm, outer=1.4cm,
    marginparwidth=0cm, marginparsep=0cm, headsep=0.7cm}%
  \nxVNoMargintrue
  \setlength{\columnseprule}{0.3pt}%
  \renewcommand{\columnseprulecolor}{\color{filetgris}}%
  \begin{multicols}{2}[\section*{\textcolor{chapcolor}{\MakeUppercase{Exercices}}}]%
  \fontsize{7.8}{9.2}\selectfont
  \setlist{itemsep=0pt,topsep=1pt,parsep=0pt,partopsep=0pt,leftmargin=1.35em}%
  \def\nxVGridPage{9}%
  \let\exercice\nxVGridExercise
  \let\endexercice\endnxVGridExercise
}{%
  \nxVFlushBottomNotes
  \end{multicols}%
  \global\let\nxVGridPage\@undefined
  \restoregeometry
}

% ===========================================================================
%  MÉTHODE APPARIÉE — résolution p. gauche, applications p. droite
% ===========================================================================
\newcounter{nxVMethodCallout}
\newcommand{\nxVMethodLegends}{}
% Rendu vectoriel portable des appels éditoriaux ① ② ③.
\newcommand{\nxVCalloutGlyph}[1]{%
  \tikz[baseline=(nxvcall.base)]\node[draw=chapcolor,text=chapcolor,circle,
    line width=0.65pt,inner sep=1.1pt,
    font=\sffamily\bfseries\fontsize{6}{6}\selectfont](nxvcall){#1};%
}
\newcommand{\nxVAppendMethodLegend}[2]{%
  \g@addto@macro\nxVMethodLegends{%
    \par\noindent
    {\titrefont\color{chapcolor}\nxVCalloutGlyph{#1}}\enspace
    {\sffamily\fontsize{7.5}{9.5}\selectfont\color{encre!75}#2}}%
}
\newcommand{\nxVMethodCallout}[1]{%
  \stepcounter{nxVMethodCallout}%
  \edef\nxVCalloutNumber{\arabic{nxVMethodCallout}}%
  {\titrefont\color{chapcolor}%
    \expandafter\nxVCalloutGlyph\expandafter{\nxVCalloutNumber}}%
  \edef\nxVAppendCallout{%
    \noexpand\nxVAppendMethodLegend{\nxVCalloutNumber}{\unexpanded{#1}}}%
  \nxVAppendCallout
}
\newcommand{\nxVRenderMethodLegends}{%
  \par\medskip
  \begin{tcolorbox}[enhanced,frame hidden,boxrule=0pt,arc=2pt,
    colback=chapcolor!5,left=7pt,right=7pt,top=5pt,bottom=5pt,
    before upper={\titrefont\fontsize{7}{9}\selectfont\color{chapcolor}%
      REPÈRES DE RÉSOLUTION}]
    \nxVMethodLegends
  \end{tcolorbox}%
}
\newcommand{\nxVMethodLabel}[1]{%
  \ifcsname nxv@method-label@#1\endcsname
    \csname nxv@method-label@#1\endcsname
  \fi
}

\newenvironment{nxVApplicationExercise}[3]{%
  \par\medskip\noindent
  \tikz[baseline=(n.base)]\node[fill=chapcolor!10,draw=chapcolor,
    text=chapcolor,rounded corners=2pt,inner xsep=6pt,inner ysep=3pt](n)
    {\titrefont\small Application};%
  \enskip
  {\sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}#3\,min}%
  \par\nopagebreak\smallskip
}{\par\medskip}

\newcommand{\separationApplications}{%
  \nxVFlushBottomNotes
  \ifnxvPairingFallback
    \par\bigskip
  \else
    \clearpage
  \fi
  \section*{\textcolor{chapcolor}{À VOUS DE JOUER}}%
  \let\exercice\nxVApplicationExercise
  \let\endexercice\endnxVApplicationExercise
}

\NewDocumentEnvironment{methodePairee}{m}{%
  \nxRubriqueMajeure[blanche]{Méthodes}%
  \begingroup
  \nxVNoMargintrue
  \global\let\nxVBottomNotes\@empty
  \setcounter{nxVMethodCallout}{0}%
  \global\let\nxVMethodLegends\@empty
  \nxVMethodLabel{#1}%
  \ifnxvPairingFallback
    \PackageWarning{nexus-manuel-v5}{NEXUS-V5-METHOD-PAIRING-FALLBACK}%
  \fi
  \let\nxVOriginalCommentaireMarge\commentaireMarge
  \renewcommand{\commentaireMarge}[1]{\nxVMethodCallout{##1}}%
  \let\nxVOriginalExempleRedige\exempleRedige
  \renewcommand{\exempleRedige}[1]{%
    \paragraph{Exemple résolu.}%
    \nxVMethodCallout{Point de départ de la résolution.}\enspace ##1%
    \nxVRenderMethodLegends}%
  \renewcommand{\refExos}[1]{%
    \ifcsname nxv@training@##1\endcsname
      \csname nxv@training@##1\endcsname
    \else
      \PackageWarning{nexus-manuel-v5}{Renvoi méthode ##1 absent}%
    \fi}%
  \section*{\textcolor{chapcolor}{EXERCICE RÉSOLU}}%
}{%
  \nxVFlushBottomNotes
  \endgroup
}

% ===========================================================================
%  FAIRE LE POINT (QCM 2 colonnes en fin de chapitre)
% ===========================================================================
\newif\ifnxVQcmDiagnostics
\newif\ifnxVQcmItemBoxOpen
\newenvironment{faireLePoint}{%
  \nxRubriqueMajeure{Auto-évaluation}%
  \section*{\textcolor{chapcolor}{\MakeUppercase{Faire le point}}}%
  \nxVQcmDiagnosticsfalse
  \let\nxVQcmOriginalDfrac\dfrac
  \let\nxVQcmOriginalNewpage\newpage
  \let\nxVQcmOriginalItem\item
  \let\nxVQcmOriginalEndEnumerate\endenumerate
  \global\nxVQcmItemBoxOpenfalse
  \renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}%
  \RenewDocumentCommand{\item}{o}{%
    \ifnum\@enumdepth=1\relax
      \ifnxVQcmItemBoxOpen
        \end{minipage}\par\global\nxVQcmItemBoxOpenfalse
      \fi
      \ifnum\value{enumi}=8\relax\nxVQcmOriginalNewpage\fi
      \Needspace{10\baselineskip}% garder question et réponses dans la colonne
      \begin{minipage}{\linewidth}\global\nxVQcmItemBoxOpentrue
    \fi
    \IfNoValueTF{##1}{\nxVQcmOriginalItem}{\nxVQcmOriginalItem[##1]}%
  }%
  \renewcommand{\endenumerate}{%
    \ifnum\@enumdepth=1\relax
      \ifnxVQcmItemBoxOpen
        \end{minipage}\par\global\nxVQcmItemBoxOpenfalse
      \fi
    \fi
    \nxVQcmOriginalEndEnumerate
  }%
  \interlinepenalty=10000
  \clubpenalty=10000
  \widowpenalty=10000
  \displaywidowpenalty=10000
  \begin{multicols}{2}%
  \small
  \renewcommand{\newpage}{%
    \end{multicols}% fermer le QCM étroit avant la page de diagnostics
    \let\dfrac\nxVQcmOriginalDfrac
    \nxVQcmOriginalNewpage
    \rubrique{Corrigés}%
    \nxVSuppressTabtrue
    \nxVQcmDiagnosticstrue
    \typeout{NEXUS-V5-DIAGNOSTICS-START}%
    \nxCompactTablesfalse
    \let\newpage\nxVQcmOriginalNewpage
    \fontsize{6.6}{7.6}\selectfont
    \setlength{\tabcolsep}{2pt}%
    \renewcommand{\arraystretch}{1.08}%
  }%
}{%
  \ifnxVQcmDiagnostics
    \let\dfrac\nxVQcmOriginalDfrac
    \clearpage
    \typeout{NEXUS-V5-DIAGNOSTICS-END}%
  \else
    \end{multicols}%
    \let\dfrac\nxVQcmOriginalDfrac
    \clearpage
  \fi
  \nxVSuppressTabfalse
}

% ===========================================================================
%  CORRIGÉS FIN DE MANUEL (3 colonnes compactes)
% ===========================================================================
\newenvironment{corrigesCompacts}{%
  \nxRubriqueMajeure[blanche]{Corrigés}%
  \section*{Corrigés}%
  \nxvCorrectionStartLabel
  \nxVNoMargintrue
  \begin{multicols}{3}%
  \footnotesize
  \typeout{NEXUS-V5-COMPACT-CORRECTIONS-START}%
  \everydisplay{\textstyle\thinmuskip=1mu\medmuskip=2mu\thickmuskip=1mu}%
  \renewcommand{\frac}[2]{\tfrac{##1}{##2}}%
  \renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}%
  \let\corrige\nxVCompactCorrection
  \let\endcorrige\endnxVCompactCorrection
}{%
  \nxVFlushBottomNotes
  \end{multicols}%
  \typeout{NEXUS-V5-COMPACT-CORRECTIONS-END}%
}

\newenvironment{nxVCompactCorrection}[1]{%
  \par\smallskip\noindent
  \tikz[baseline=(n.base)]\node[
    fill=chapcolor!70!black,
    text=white,
    rounded corners=2pt,
    inner xsep=7pt,
    inner ysep=3.5pt
  ](n){\titrefont\small Corrigé};%
  \par\nopagebreak\smallskip
}{\par\smallskip}

% ===========================================================================
%  IDENTITÉ ÉDITORIALE — millésime, variante, marque
% ===========================================================================
% Ces trois données sont les seules dont dépendent la couverture, la page de
% titre intérieure et les métadonnées du PDF. Elles sont dérivées du booléen
% de variante déjà porté par la classe : aucun appel de la collection n'a à
% répéter « élève » ou « professeur ».
\newcommand{\nexus@millesime}{2026-2027}
\newcommand{\millesime}[1]{\renewcommand{\nexus@millesime}{#1}}
\newcommand{\nxMarqueEditeur}{Nexus Réussite}
% Libellé de variante en casse éditoriale (métadonnées, page de titre).
\newcommand{\nxLibelleVariante}{%
  \ifnxVersionProfesseur Édition Professeur\else Édition Élève\fi}
% Mention de variante en capitales (première de couverture, page de titre).
% Sans interlettrage : le texte doit rester extractible tel quel du PDF.
\newcommand{\nxMentionVariante}{%
  \ifnxVersionProfesseur ÉDITION PROFESSEUR\else ÉDITION ÉLÈVE\fi}
\newcommand{\nxTitrePdf}{%
  \nexus@matiere\space\nexus@niveau\space—\space
  \nxLibelleVariante\space—\space\nexus@millesime}

% ===========================================================================
%  NAVIGATION ET MÉTADONNÉES DU PDF (hyperref + bookmark)
% ===========================================================================
% Sans hyperref le PDF sortait avec zéro signet, zéro lien et un dictionnaire
% Info vide : trois exigences de publication non tenues (AGENTS.md, « le PDF
% final doit avoir signets, liens, métadonnées et polices incorporées »).
%
% hyperref est chargé ici, à la toute fin de la classe : après KOMA,
% scrlayer-scrpage, babel, amsmath, tikz, tcolorbox et listings, donc à la
% place que sa documentation exige, et avant la charte, qui n'enveloppe
% ensuite que \addcontentsline — donc la version d'hyperref, ce qui préserve
% les destinations.
%
% Les signets ne sont PAS une seconde table des matières : ils recopient
% exactement les entrées écrites dans le .toc (chapitres, puis grandes
% sections pédagogiques). Aucun objet fin (exercice, définition, figure) ne
% produit d'entrée de sommaire, donc aucun ne produit de signet.
% psdextra n'est pas un confort : sans lui, un symbole unicode-math dans un
% titre de section (« Dérivée de $t\mapsto\mathrm{e}^{at}$ ») arrive tel quel
% dans \HyPsd@Char, qui suppose un caractère, et la compilation du manuel
% entier s'arrête sur « Improper alphabetic constant ». psdextra traduit ces
% symboles en Unicode : le signet lit « Dérivée de t↦eat ».
\RequirePackage[
  unicode,
  psdextra,
  bookmarks=true,
  bookmarksnumbered=false,% \numberline{0} des pages liminaires ne doit pas
                          % remonter dans le titre du signet
  bookmarksopen=true,
  bookmarksopenlevel=0,
  hidelinks,              % manuel destiné à l'impression : aucun cadre
  pdfpagelabels=true,
  pdfdisplaydoctitle=true,
  % La langue du document se declare au CHARGEMENT. hyperref ne consomme
  % `pdflang` qu'a ce moment : passe plus tard par \hypersetup, il avertit
  % « Option `pdflang' has already been used, setting the option has no effect »
  % et le catalogue sort sans /Lang. Le PDF perdait alors sa langue selon
  % l'ordre des crochets \AtBeginDocument, c'est-a-dire selon ce que d'autres
  % paquets chargent avant. Ici, l'ordre n'entre plus en jeu.
  pdflang=fr-FR,
]{hyperref}
\RequirePackage{bookmark}

% Les entrées de sommaire écrites à la main (pages liminaires et annexes :
% « Avant-propos », « Formulaire »…) suivent un \chapter* qui ne pose aucune
% ancre. hyperref les rattacherait alors à la dernière ancre vue, c'est-à-dire
% à l'ouverture du chapitre précédent : signet correct de libellé, mais
% pointant sur la mauvaise page. On pose donc une ancre fraîche pour toute
% entrée de sommaire de niveau chapitre qui n'en a pas déjà reçu une du
% \refstepcounter{chapter} de \ouverturechapitre.
\newif\ifnxAncreChapitreFraiche
\nxAncreChapitreFraichefalse
\let\nxOrigAddcontentsline\addcontentsline
\renewcommand{\addcontentsline}[3]{%
  \ifstrequal{#2}{chapter}{%
    \ifnxAncreChapitreFraiche\else\phantomsection\fi
  }{}%
  \nxOrigAddcontentsline{#1}{#2}{#3}%
  \global\nxAncreChapitreFraichefalse
}

% Filet de sécurité derrière psdextra : un symbole qu'il ne couvrirait pas
% resterait un token \Umathchardef, et `#1 dans \HyPsd@Char redonnerait
% l'erreur fatale. Un titre de section ne doit jamais pouvoir arrêter la
% fabrication du manuel : les tokens qui ne sont pas des caractères sont
% simplement absents du signet, comme le fait déjà hyperref pour les macros
% qu'il ne sait pas traduire.
\AtBeginDocument{%
  \let\nxHyPsdCharOriginal\HyPsd@Char
  \def\HyPsd@Char#1{%
    \ifcat\noexpand#1\relax\else\nxHyPsdCharOriginal{#1}\fi}%
}

\AtBeginDocument{%
  \hypersetup{
    pdftitle={\nxTitrePdf},
    pdfauthor={\nxMarqueEditeur},
    pdfsubject={Manuel scolaire — \nexus@matiere\space\nexus@niveau},
    pdfkeywords={\nexus@matiere, \nexus@niveau, manuel scolaire,
      \nxMarqueEditeur, \nexus@millesime},
    % pdflang n'est PAS ici : hyperref l'a deja consomme au chargement.
  }%
  % /Publisher n'appartient pas au vocabulaire d'hyperref : on l'ajoute au
  % dictionnaire Info, en UTF-16BE explicite pour ne dépendre d'aucun
  % encodage de repli. La chaîne est « Nexus Réussite ».
  \pdfextension info{%
    /Publisher <FEFF004E00650078007500730020005200E9007500730073006900740065>}%
  % LuaTeX ajoute par défaut /PTEX.FullBanner, qui publie la distribution et
  % la machine de compilation dans le PDF diffusé. Le bit 1 la supprime ; les
  % autres champs (dont /ID, indispensable à la reproductibilité) restent.
  \pdfvariable suppressoptionalinfo=1\relax
}
