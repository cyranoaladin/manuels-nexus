% nexus-manuel.cls v3 — Classe du manuel Nexus Réussite (édition professionnelle)
% Moteur : LuaLaTeX obligatoire. Base : KOMA-Script scrbook.
% Polices : Libertinus Serif/Math + Montserrat + JetBrains Mono (OFL, embarquées).
% Charte graphique : docs/06_charte_graphique.md v3.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/07/15 v3.0 Manuel Nexus Reussite - edition professionnelle]

% ===========================================================================
%  BASE KOMA-SCRIPT
% ===========================================================================
\LoadClass[a4paper,fontsize=9.5pt,twoside,open=right,headings=normal,
  chapterprefix=false,numbers=noenddot]{scrbook}

% ===========================================================================
%  MOTEUR ET LANGUE
% ===========================================================================
\RequirePackage{iftex}
\RequireLuaTeX
\RequirePackage[french]{babel}
\RequirePackage{csquotes}
\RequirePackage{amsmath}

% ===========================================================================
%  POLICES (fontspec + unicode-math, embarquées via Path=)
% ===========================================================================
\RequirePackage{fontspec}
\RequirePackage{unicode-math}

\defaultfontfeatures{Ligatures=TeX}

% Détection du chemin des fontes (gabarits/fonts/ depuis le répertoire de travail)
\newcommand{\nxFontPath}{gabarits/fonts/}

\setmainfont{LibertinusSerif}[
  Path=\nxFontPath,
  Extension=.otf,
  UprightFont=*-Regular,
  BoldFont=*-Bold,
  ItalicFont=*-Italic,
  BoldItalicFont=*-BoldItalic,
]
\setmathfont{LibertinusMath-Regular.otf}[Path=\nxFontPath]

\setsansfont{Montserrat}[
  Path=\nxFontPath,
  Extension=.otf,
  UprightFont=*-Regular,
  BoldFont=*-SemiBold,
  ItalicFont=*-Italic,
  BoldItalicFont=*-SemiBoldItalic,
  FontFace={m}{n}{*-Medium},
  FontFace={m}{it}{*-MediumItalic},
  FontFace={thin}{n}{*-Thin},
]

\setmonofont{JetBrainsMono}[
  Path=\nxFontPath,
  Extension=.otf,
  UprightFont=*-Regular,
  BoldFont=*-Bold,
  ItalicFont=*-Italic,
  BoldItalicFont=*-BoldItalic,
  Scale=0.89,
  Ligatures=NoCommon,
  Numbers=Monospaced,
]

% ===========================================================================
%  TYPOGRAPHIE PROFESSIONNELLE
% ===========================================================================
\RequirePackage[activate={true,nocompatibility},tracking=true,
  expansion=true,protrusion=true]{microtype}
\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\setlength{\parskip}{0.45em}

% ===========================================================================
%  COULEURS
% ===========================================================================
\RequirePackage[table]{xcolor}
\definecolor{nxBleu}{HTML}{1B3A5C}
\definecolor{nxOr}{HTML}{C9A227}
\definecolor{nxGris}{HTML}{5A6472}
\definecolor{nxRouge}{HTML}{B0413E}
\definecolor{nxVert}{HTML}{2E6E4E}

% ===========================================================================
%  GRILLE DE PAGE (colonne texte 118mm + marge pédagogique 46mm)
% ===========================================================================
\RequirePackage{geometry}
\geometry{%
  a4paper,
  inner=17mm,
  textwidth=118mm,
  marginparsep=6mm,
  marginparwidth=46mm,
  top=20mm,
  bottom=18mm,
  headsep=10mm,
  footskip=12mm,
}
% Marge extérieure calculée : 210 - 17 - 118 - 6 - 46 = 23mm (dont 15mm après marge)

% ===========================================================================
%  MARGE PÉDAGOGIQUE (colonne de design)
% ===========================================================================
\RequirePackage{marginnote}
\RequirePackage{mparhack}
\renewcommand*{\raggedleftmarginnote}{}
\renewcommand*{\raggedrightmarginnote}{\raggedright}

\newcommand{\margeAppui}[1]{%
  \marginnote{\sffamily\fontseries{m}\fontshape{n}\fontsize{7.5}{10}\selectfont
    \color{nxGris}\rule[-0.5ex]{0.4pt}{2.5ex}\kern4pt #1}%
}
\newcommand{\commentaireMarge}[1]{%
  \marginnote{\sffamily\fontsize{7.5}{10}\selectfont\color{nxBleu}#1}%
}

% ===========================================================================
%  HIÉRARCHIE TYPOGRAPHIQUE (KOMA-Script RedeclareSectionCommand)
% ===========================================================================
\addtokomafont{chapter}{\sffamily\bfseries\color{nxBleu}\fontsize{22}{27}\selectfont}
\addtokomafont{section}{\sffamily\bfseries\color{nxBleu}\fontsize{13}{17}\selectfont}
\addtokomafont{subsection}{\sffamily\bfseries\color{nxBleu!85!black}\fontsize{11}{14}\selectfont}
\addtokomafont{subsubsection}{\sffamily\bfseries\color{nxBleu!70!black}\fontsize{10}{13}\selectfont}

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
\ohead{\sffamily\fontsize{7.5}{10}\selectfont\color{nxGris}\headmark}
\cfoot{\sffamily\fontsize{8}{10}\selectfont\thepage}

% ===========================================================================
%  LISTES (enumitem global)
% ===========================================================================
\RequirePackage{enumitem}
\setlist{itemsep=1pt, topsep=3pt, parsep=0pt, leftmargin=1.5em}
\setlist[enumerate,1]{label=\textcolor{nxBleu}{\arabic*.}}
\setlist[itemize,1]{label=\textcolor{nxBleu}{\textbullet}}

% ===========================================================================
%  ENCADRÉS v3 (tcolorbox enhanced+skins, styles centralisés)
% ===========================================================================
\RequirePackage[most,skins]{tcolorbox}
\RequirePackage{pifont}

% Style de base : filet gauche + fond léger + titre petites capitales Montserrat
\tcbset{
  nxbase/.style={
    enhanced, breakable,
    boxrule=0pt, leftrule=2pt, sharp corners,
    before skip=9pt, after skip=9pt,
    fonttitle=\sffamily\bfseries\fontsize{9}{12}\selectfont,
    before upper={\setlength{\parskip}{0.35em}},
  },
  nxbleu/.style={nxbase, colframe=nxBleu, colback=nxBleu!4,
    title={\addfontfeatures{LetterSpace=4}\textsc{#1}}},
}

% Définitions / Théorèmes (filet nxBleu, fond nxBleu!4)
\newcounter{nxDefNum}[chapter]
\newtcolorbox{nxdef}[1][]{nxbase, colframe=nxBleu, colback=nxBleu!4,
  title={\addfontfeatures{LetterSpace=4}\textsc{Définition}~#1}}
\newtcolorbox{nxthm}[1][]{nxbase, colframe=nxBleu!80!black, colback=nxBleu!5,
  title={\addfontfeatures{LetterSpace=4}\textsc{Théorème}~#1}}
\newtcolorbox{nxprop}[1][]{nxbase, colframe=nxGris, colback=nxGris!6,
  title={\addfontfeatures{LetterSpace=4}\textsc{Propriété}~#1}}

% Raccourcis
\newcommand{\definition}[2][]{\begin{nxdef}[#1]#2\end{nxdef}}
\newcommand{\theoreme}[2][]{\begin{nxthm}[#1]#2\end{nxthm}}
\newcommand{\propriete}[2][]{\begin{nxprop}[#1]#2\end{nxprop}}
\newcommand{\exemple}[1]{\par\noindent\textbf{\textcolor{nxVert}{Exemple.}} #1\par}
\newcommand{\contreexemple}[1]{\par\noindent\textbf{\textcolor{nxRouge}{Contre-exemple.}} #1\par}

% Erreur fréquente (filet nxRouge)
\RequirePackage[normalem]{ulem}
\newtcolorbox{nxerr}{nxbase, colframe=nxRouge, colback=nxRouge!6,
  title={\addfontfeatures{LetterSpace=4}\textsc{Erreur fréquente}}}
\newcommand{\erreurFrequente}[1]{\begin{nxerr}#1\end{nxerr}}

% Approfondissement ★ (fond nxBleu!6, PAS de filet)
\newtcolorbox{nxstar}{enhanced, breakable, boxrule=0pt, sharp corners,
  colback=nxBleu!6, colframe=nxBleu!6,
  before skip=9pt, after skip=9pt,
  title={\addfontfeatures{LetterSpace=4}\textsc{Pour aller plus loin}},
  fonttitle=\sffamily\bfseries\fontsize{9}{12}\selectfont}
\newcommand{\approfondissement}[1]{\begin{nxstar}#1\end{nxstar}}

% ===========================================================================
%  FICHES MÉTHODES (filet nxOr, 6 rubriques)
% ===========================================================================
\newtcolorbox{fmbox}[2]{nxbase, colframe=nxOr!80!black, colback=nxOr!6,
  title={\addfontfeatures{LetterSpace=4}\textsc{Méthode #1} --- #2}}
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

% Pictogrammes parcours (redéfinis par nexus-icons.tex si présent)
\newcommand{\parcoursUn}{}
\newcommand{\parcoursDeux}{}
\newcommand{\parcoursTrois}{}
\newcommand{\pictoOral}{}
\newcommand{\pictoPython}{}

\newenvironment{exercice}[3]{%
  \refstepcounter{exo}\par\medskip\noindent
  \colorbox{nxBleu}{\color{white}\sffamily\bfseries\small~Exercice \theexo~}%
  \quad
  \ifnum#2=1\relax\parcoursUn\fi
  \ifnum#2=2\relax\parcoursDeux\fi
  \ifnum#2=3\relax\parcoursTrois\fi
  \quad{\sffamily\fontsize{7.5}{10}\selectfont\color{nxGris}\texttt{#1} --- #3~min}%
  \par\nopagebreak\smallskip
}{\par\medskip}

\newenvironment{corrige}[1]{%
  \par\medskip\noindent
  \colorbox{nxVert!85!black}{\color{white}\sffamily\bfseries\small~Corrigé~}%
  \quad{\sffamily\fontsize{7.5}{10}\selectfont\color{nxGris}\texttt{#1}}%
  \par\nopagebreak\smallskip
}{\par\medskip}

\newcommand{\baremeIndicatif}[1]{%
  \par\noindent{\sffamily\fontsize{7.5}{10}\selectfont\itshape Barème indicatif : #1}\par
}
\newcommand{\coupDePouce}[2]{%
  \par\noindent{\small\sffamily\textbf{Coup de pouce #1.} #2}\par
}

% ===========================================================================
%  ÉVALUATIONS
% ===========================================================================
\newenvironment{evaluation}[2]{%
  \par\bigskip\noindent
  \textbf{\textcolor{nxBleu}{\large\sffamily Évaluation \texttt{#1}}}\quad
  {\sffamily\fontsize{8}{10}\selectfont #2~min}\par\nopagebreak\medskip
}{\par\bigskip}

% ===========================================================================
%  CODE PYTHON (listings avec JetBrains Mono)
% ===========================================================================
\RequirePackage{listings}

\lstdefinestyle{nxpy}{%
  language=Python,
  basicstyle=\ttfamily\fontsize{8.5}{11}\selectfont,
  keywordstyle=\color{nxBleu}\bfseries,
  commentstyle=\color{nxGris}\itshape,
  stringstyle=\color{nxVert!70!black},
  frame=l,
  framerule=1pt,
  rulecolor=\color{nxBleu!30},
  backgroundcolor=\color{white},
  numbers=left,
  numberstyle=\ttfamily\fontsize{6}{8}\selectfont\color{nxGris!60},
  numbersep=8pt,
  xleftmargin=18pt,
  aboveskip=9pt,
  belowskip=9pt,
  showstringspaces=false,
  tabsize=4,
  literate=%
    {é}{{\'{e}}}1 {è}{{\`{e}}}1 {ê}{{\^{e}}}1 {ë}{{\"{e}}}1
    {à}{{\`{a}}}1 {â}{{\^{a}}}1 {ù}{{\`{u}}}1 {û}{{\^{u}}}1
    {î}{{\^{i}}}1 {ô}{{\^{o}}}1 {ç}{{\c{c}}}1
    {É}{{\'{E}}}1 {È}{{\`{E}}}1 {À}{{\`{A}}}1
    {—}{{---}}1,
}
\lstnewenvironment{python}{\lstset{style=nxpy}}{}

% ===========================================================================
%  TABLES (booktabs)
% ===========================================================================
\RequirePackage{booktabs}
\RequirePackage{eurosym}

% ===========================================================================
%  FIGURES (définies dans nexus-figures.tex ; fallback si absent)
% ===========================================================================
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc}

% ===========================================================================
%  OUVERTURE DE CHAPITRE (simplifié v3 — enrichi par nexus-signatures.tex)
% ===========================================================================
% nxChapNum est defini dans nexus-signatures.tex

\newcommand{\ouverturechapitre}[5][motifGenerique]{%
  \stepcounter{nxChapNum}%
  \thispagestyle{plain}%
  \vspace*{1.2cm}%
  \chapter*{\color{nxBleu}\fontsize{26}{32}\selectfont\sffamily #2}%
  \addcontentsline{toc}{chapter}{#2}%
  \vspace{0.8cm}%
  \noindent\textcolor{nxBleu}{\large\sffamily\bfseries Ce que je vais savoir faire}\par
  \vspace{0.3cm}%
  #3%
  \vspace{0.6cm}%
  \begin{tcolorbox}[nxbase, colframe=nxGris, colback=nxGris!6,
    title={\addfontfeatures{LetterSpace=4}\textsc{Carte du chapitre}}]%
    #4%
  \end{tcolorbox}%
  \vspace{0.4cm}%
  \noindent\textcolor{nxOr}{\sffamily\bfseries Temps estimés :} #5%
  \par\vfill
}

% ===========================================================================
%  EXTENSIONS (chargées si présentes, silencieuses sinon)
% ===========================================================================
\InputIfFileExists{nexus-icons.tex}{}{}
\InputIfFileExists{nexus-figures.tex}{}{%
  \newcounter{nxfig}[chapter]
  \newenvironment{nxfigure}[2][0.9\linewidth]{%
    \refstepcounter{nxfig}\par\medskip\begin{center}\begin{minipage}{##1}\centering
    \def\nxfigcaption{##2}}{%
    \par\smallskip{\sffamily\fontsize{8}{10}\selectfont\color{nxGris}%
      \textbf{Figure \thenxfig} --- \nxfigcaption}%
    \end{minipage}\end{center}\medskip}
}
\InputIfFileExists{nexus-signatures.tex}{}{\newcounter{nxChapNum}}
\InputIfFileExists{nexus-code.tex}{}{}
\InputIfFileExists{nexus-figures-nsi.tex}{}{}
