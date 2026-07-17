% nexus-manuel.cls v4.1 — Classe du manuel Nexus Réussite (édition premium)
% Moteur : LuaLaTeX obligatoire. Base : KOMA-Script scrbook.
% Polices : TeX Gyre Pagella (corps + maths) + TeX Gyre Heros (titres) + JetBrains Mono (code).
% Charte graphique : kit v2 « Éditorial premium » transposé.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/07/16 v4.1 Manuel Nexus Reussite - editorial premium]

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
\RequirePackage{amsthm}
\RequirePackage{amssymb}

% ===========================================================================
%  MATIÈRE ET NIVEAU (paramétrage du sous-titre de couverture)
% ===========================================================================
\newcommand{\nexus@matiere}{NSI}
\newcommand{\nexus@niveau}{Première}
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
\setmonofont{JetBrains Mono}[Scale=0.89]

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
\geometry{%
  a4paper,
  top=2.4cm, bottom=2.6cm,
  inner=2.0cm, outer=4.8cm,
  marginparwidth=3.5cm, marginparsep=0.6cm,
  headsep=0.7cm,
}

% ===========================================================================
%  MARGE PÉDAGOGIQUE (colonne de design)
% ===========================================================================
\RequirePackage{marginnote}
\RequirePackage{mparhack}
\renewcommand*{\raggedleftmarginnote}{}
\renewcommand*{\raggedrightmarginnote}{\raggedright}

\newcommand{\margeAppui}[1]{%
  \marginnote{\sffamily\fontsize{7.5}{10}\selectfont
    \color{encre!50}\rule[-0.5ex]{0.4pt}{2.5ex}\kern4pt #1}%
}
\newcommand{\commentaireMarge}[1]{%
  \marginnote{\sffamily\fontsize{7.5}{10}\selectfont\color{chapcolor}#1}%
}
% Vocabulaire en marge (kit v2)
\newcommand{\vocab}[2]{%
  \textcolor{chapcolor}{\textbf{#1}}%
  \marginnote{\textcolor{chapcolor}{\rule{2.6cm}{2pt}}\\[2pt]
    {\titrefont\color{chapcolor}#1}\\[2pt]\itshape\small #2}}

% ===========================================================================
%  HIÉRARCHIE TYPOGRAPHIQUE (KOMA-Script RedeclareSectionCommand)
% ===========================================================================
\addtokomafont{chapter}{\titrefont\color{encre}\fontsize{22}{27}\selectfont}
\addtokomafont{section}{\titrefont\color{encre}\fontsize{13}{17}\selectfont}
\addtokomafont{subsection}{\titrefont\color{encre!85!black}\fontsize{11}{14}\selectfont}
\addtokomafont{subsubsection}{\titrefont\color{encre!70!black}\fontsize{10}{13}\selectfont}

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
\ofoot{\tikz\node[fill=chapcolor, text=white, circle,
  inner sep=3.6pt, font=\titrefont\small]{\thepage};}
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
  \marginnote{\sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\texttt{#1}\\\icnChrono~#3~min}%
  \par\nopagebreak\smallskip
}{\par\medskip}

\newenvironment{corrige}[1]{%
  \par\medskip\noindent
  \tikz[baseline=(n.base)]\node[fill=chapcolor!70!black, text=white,
    rounded corners=2pt, inner xsep=7pt, inner ysep=3.5pt](n)
    {\titrefont\small Corrigé};%
  \marginnote{\sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\texttt{#1}}%
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
  \textbf{\textcolor{chapcolor}{\large\sffamily Évaluation \texttt{#1}}}\quad
  {\sffamily\fontsize{8}{10}\selectfont #2~min}\par\nopagebreak\medskip
}{\par\bigskip}

% ===========================================================================
%  CODE PYTHON (listings avec JetBrains Mono)
% ===========================================================================
\RequirePackage{listings}

% Réglages globaux listings (columns flexible, upquote, breaklines)
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

% Code en ligne
\newcommand{\code}[1]{{\ttfamily\color{coulCode}#1}}

% Protection de \lstinline contre babel-french (NoAutoSpacing)
\let\nxOrigLstinline\lstinline
\renewcommand{\lstinline}{\NoAutoSpacing\nxOrigLstinline}

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
%  OUVERTURE DE CHAPITRE v4.1 — Bandeau accent + numéro géant + décor TikZ
% ===========================================================================
% nxChapNum est défini dans nexus-signatures.tex
\usetikzlibrary{backgrounds}

\newlength{\nxBandHeight}
\setlength{\nxBandHeight}{0.56\paperheight}

% Usage : \ouverturechapitre[motif]{Titre}{capacites}{accroche}{temps}
\newcommand{\ouverturechapitre}[5][motifGenerique]{%
  \stepcounter{nxChapNum}%
  \refstepcounter{chapter}%
  \chaptermark{#2}%
  \addcontentsline{toc}{chapter}{#2}%
  % --- PAGE VISUELLE (recto, bandeau accent haut 56%) ---
  \thispagestyle{empty}%
  \noindent\begin{tikzpicture}[remember picture, overlay]
    % Bandeau plein accent (haut de page)
    \fill[chapcolor] (current page.north west)
      rectangle ([yshift=-\nxBandHeight]current page.north east);
    % Décor TikZ du chapitre (dans le bandeau, moitié droite)
    \csname #1\endcsname
    % Étiquette matière · niveau
    \node[anchor=north west, text=white, opacity=0.9,
          font=\titrefont\small, inner sep=0pt]
      at ([shift={(20mm,-17mm)}]current page.north west)
      {\MakeUppercase{\nexus@matiere}\ \ $\cdot$\ \ \nexus@niveau};
    % Numéro géant fantôme
    \node[anchor=south west, text=white, opacity=0.15, inner sep=0pt,
          font=\titrefont\fontsize{210}{210}\selectfont]
      at ([shift={(16mm,-\nxBandHeight+2mm)}]current page.north west)
      {\ifnum\value{chapter}>0 \thechapter\fi};
    % « Chapitre N »
    \node[anchor=south west, text=white, align=left, inner sep=0pt,
          font=\titrefont]
      at ([shift={(20mm,-\nxBandHeight+24mm)}]current page.north west)
      {\fontsize{15}{15}\selectfont\MakeUppercase{Chapitre~\thechapter}};
    % Titre géant
    \node[anchor=south west, text=white, align=left, inner sep=0pt,
          text width=0.66\paperwidth,
          font=\titrefont\fontsize{34}{40}\selectfont]
      at ([shift={(20mm,-\nxBandHeight+13mm)}]current page.north west)
      {#2\par};
  \end{tikzpicture}\par
  % Espace sous le bandeau
  \vspace*{\dimexpr\nxBandHeight-\topskip-1.4cm\relax}%
  % Objectifs / capacités sous le bandeau
  \begin{tcolorbox}[enhanced, frame hidden, boxrule=0pt, arc=3pt,
    colback=chapcolor!7,
    borderline west={3pt}{0pt}{chapcolor},
    left=12pt, right=12pt, top=10pt, bottom=10pt,
    before upper={\textcolor{chapcolor}{\titrefont\large
      Objectifs --- Capacités attendues}\par\vspace{5pt}}]
    #3%
  \end{tcolorbox}%
  \vspace{0.4cm}%
  \begin{nxcard}%
    #4%
  \end{nxcard}%
  \vspace{0.3cm}%
  \noindent\textcolor{chapcolor}{\titrefont Temps estimés :} #5%
  \par\vfill
  \clearpage
}

% ===========================================================================
%  EXTENSIONS (chargées si présentes, silencieuses sinon)
% ===========================================================================
\InputIfFileExists{gabarits/nexus-icons.tex}{}{\ClassWarning{nexus-manuel}{Nexus asset missing: icons}}
\InputIfFileExists{gabarits/nexus-figures.tex}{}{\ClassWarning{nexus-manuel}{Nexus asset missing: figures}%
  \newcounter{nxfig}[chapter]
  \newenvironment{nxfigure}[2][0.9\linewidth]{%
    \refstepcounter{nxfig}\par\medskip\begin{center}\begin{minipage}{##1}\centering
    \def\nxfigcaption{##2}}{%
    \par\smallskip{\sffamily\fontsize{8}{10}\selectfont\color{nxGris}%
      \textbf{Figure \thenxfig} --- \nxfigcaption}%
    \end{minipage}\end{center}\medskip}
}
\InputIfFileExists{gabarits/nexus-signatures.tex}{}{\ClassWarning{nexus-manuel}{Nexus asset missing: signatures}\newcounter{nxChapNum}}
\InputIfFileExists{gabarits/nexus-code.tex}{}{}
\InputIfFileExists{gabarits/nexus-figures-nsi.tex}{}{}
