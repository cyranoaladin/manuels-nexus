% nexus-manuel.cls — Classe du manuel Nexus Réussite
% Implémente le système visuel défini dans docs/06_charte_graphique.md :
% grille A4, marge pédagogique, 3 strates, parcours, pictogrammes, encadrés.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/07/15 v2.1 Manuel differencie Nexus Reussite]
\LoadClass[a4paper,11pt,twoside]{book}

% ===========================================================================
%  ENCODAGE ET LANGUE
% ===========================================================================
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath,amssymb,amsthm}

% ===========================================================================
%  TYPOGRAPHIE PROFESSIONNELLE
% ===========================================================================
\RequirePackage{libertine}           % Libertine (corps) + Biolinum (sans-serif)
\RequirePackage[libertine]{newtxmath}% Maths assorties à Libertine
\RequirePackage{microtype}           % Protrusion + expansion
\RequirePackage[table]{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{marginnote,graphicx,enumitem,pifont,listings,eurosym}
\RequirePackage{geometry,fancyhdr,titlesec,titletoc}

% ===========================================================================
%  GRILLE DE PAGE
% ===========================================================================
\geometry{%
  a4paper,
  inner=2cm,
  outer=4.5cm,
  top=2.2cm,
  bottom=2.2cm,
  marginparwidth=3.6cm,
  marginparsep=0.5cm
}
\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\renewcommand{\familydefault}{\rmdefault}
\setlength{\parskip}{0.45em}
\setlist{itemsep=0.25em,topsep=0.35em}

% ===========================================================================
%  PALETTE NEXUS (5 couleurs)
% ===========================================================================
\definecolor{nxBleu}{HTML}{1B3A5C}
\definecolor{nxOr}{HTML}{C9A227}
\definecolor{nxGris}{HTML}{5A6472}
\definecolor{nxRouge}{HTML}{B0413E}
\definecolor{nxVert}{HTML}{2E6E4E}

% ===========================================================================
%  HIÉRARCHIE TYPOGRAPHIQUE
% ===========================================================================
% H1 — section-capacité (15/19 pt, gras sans emp., bleu)
\titleformat{\section}%
  {\sffamily\bfseries\color{nxBleu}\fontsize{15}{19}\selectfont}%
  {\thesection}{0.8em}{}
\titlespacing*{\section}{0pt}{2.1ex plus .4ex}{1.0ex}

% H2 — sous-partie (12/15 pt)
\titleformat{\subsection}%
  {\sffamily\bfseries\color{nxBleu!85!black}\fontsize{12}{15}\selectfont}%
  {\thesubsection}{0.7em}{}
\titlespacing*{\subsection}{0pt}{1.6ex plus .3ex}{.7ex}

% H3 — subdivision technique (11/14 pt)
\titleformat{\subsubsection}%
  {\sffamily\bfseries\color{nxBleu!70!black}\fontsize{11}{14}\selectfont}%
  {\thesubsubsection}{0.6em}{}
\titlespacing*{\subsubsection}{0pt}{1.2ex plus .2ex}{.5ex}

% Section-capacité avec rappel en marge
\newcommand{\sectionCapacite}[2]{%
  \section{#1}\margeAppui{\textbf{Je sais\ldots} #2}%
}

% ===========================================================================
%  SOMMAIRE STYLÉ
% ===========================================================================
\titlecontents{chapter}[0em]%
  {\addvspace{1.2em}\sffamily\bfseries\color{nxBleu}}%
  {\contentslabel{2em}}{\hspace*{-2em}}%
  {\titlerule*[0.6pc]{}\contentspage}
\titlecontents{section}[2em]%
  {\addvspace{0.3em}\sffamily\color{nxBleu!90!black}}%
  {\contentslabel{2em}}{\hspace*{-2em}}%
  {\titlerule*[0.6pc]{.}\contentspage}
\titlecontents{subsection}[4em]%
  {\small\color{nxGris}}%
  {\contentslabel{2.5em}}{\hspace*{-2.5em}}%
  {\titlerule*[0.6pc]{.}\contentspage}

% ===========================================================================
%  PICTOGRAMMES / PARCOURS
% ===========================================================================
\newcommand{\parcoursUn}{\textcolor{nxOr}{\ding{117}}}
\newcommand{\parcoursDeux}{\textcolor{nxOr}{\ding{117}\ding{117}}}
\newcommand{\parcoursTrois}{\textcolor{nxOr}{\ding{117}\ding{117}\ding{117}}}
\newcommand{\pictoOral}{\textcolor{nxBleu}{\ding{110}~Oral}}
\newcommand{\pictoPython}{\textcolor{nxBleu}{\texttt{>\!\!>~Python}}}

% ===========================================================================
%  STRATE 1 : ENCADRÉS DU COURS
% ===========================================================================
\newtcolorbox{nxdef}[1][]{%
  colback=nxBleu!4,colframe=nxBleu,%
  boxrule=0pt,leftrule=1.2pt,%
  title=\textsc{Définition}~#1,%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}
\newtcolorbox{nxthm}[1][]{%
  colback=nxBleu!5,colframe=nxBleu!80!black,%
  boxrule=0pt,leftrule=1.2pt,%
  title=\textsc{Théorème}~#1,%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}
\newtcolorbox{nxprop}[1][]{%
  colback=nxGris!6,colframe=nxGris,%
  boxrule=0pt,leftrule=1.2pt,%
  title=\textsc{Propriété}~#1,%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}

% Raccourcis commandes
\newcommand{\definition}[2][]{\begin{nxdef}[#1]#2\end{nxdef}}
\newcommand{\theoreme}[2][]{\begin{nxthm}[#1]#2\end{nxthm}}
\newcommand{\propriete}[2][]{\begin{nxprop}[#1]#2\end{nxprop}}
\newcommand{\exemple}[1]{\par\noindent\textbf{\textcolor{nxVert}{Exemple.}} #1\par}
\newcommand{\contreexemple}[1]{\par\noindent\textbf{\textcolor{nxRouge}{Contre-exemple.}} #1\par}

% ===========================================================================
%  STRATE 2 : MARGE D'APPUI ET ERREURS
% ===========================================================================
\newcommand{\margeAppui}[1]{%
  \marginnote{\footnotesize\color{nxGris}\itshape #1}%
}
\newcommand{\commentaireMarge}[1]{%
  \marginnote{\footnotesize\color{nxBleu}#1}%
}
\newtcolorbox{nxerr}{%
  colback=nxRouge!6,colframe=nxRouge,%
  boxrule=0pt,leftrule=1.2pt,%
  title={\ding{115}~\textsc{Erreur fréquente}},%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}
\newcommand{\erreurFrequente}[1]{\begin{nxerr}#1\end{nxerr}}

% ===========================================================================
%  STRATE 3 : APPROFONDISSEMENT
% ===========================================================================
\newtcolorbox{nxstar}{%
  colback=nxBleu!5,colframe=nxBleu,%
  boxrule=0.4pt,%
  title={$\bigstar$~\textsc{Pour aller plus loin}},%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}
\newcommand{\approfondissement}[1]{\begin{nxstar}#1\end{nxstar}}

% ===========================================================================
%  FICHES MÉTHODES
% ===========================================================================
\newtcolorbox{fmbox}[2]{%
  colback=nxOr!6,colframe=nxOr!80!black,%
  boxrule=0pt,leftrule=1.2pt,%
  title={\textsc{Méthode #1} --- #2},%
  fonttitle=\sffamily\bfseries,%
  enhanced,breakable%
}
\newenvironment{fichemethode}[2]{\begin{fmbox}{#1}{#2}}{\end{fmbox}}
\newcommand{\quandUtiliser}[1]{\paragraph{Quand l'utiliser.}#1}
\newcommand{\pasApas}[1]{\paragraph{La méthode pas à pas.}#1}
\newcommand{\exempleRedige}[1]{\paragraph{Exemple rédigé.}#1}
\newcommand{\pieges}[1]{\paragraph{Les pièges.}#1}
\newcommand{\verifier}[1]{\paragraph{Vérifier son résultat.}#1}
\newcommand{\sEntrainer}[1]{\paragraph{S'entraîner.}#1}
\newcommand{\refExos}[1]{\textit{(renvois exercices #1 : complétés à l'assemblage)}}

% ===========================================================================
%  EXERCICES / CORRIGÉS
% ===========================================================================
% \begin{exercice}{ID}{parcours(1|2|3)}{durée min}
\newcounter{exo}
\newenvironment{exercice}[3]{%
  \refstepcounter{exo}\par\medskip\noindent
  \textbf{\textcolor{nxBleu}{Exercice \theexo}}\quad
  \ifnum#2=1\parcoursUn\fi
  \ifnum#2=2\parcoursDeux\fi
  \ifnum#2=3\parcoursTrois\fi
  \quad{\footnotesize\texttt{#1} --- #3~min}\par\nopagebreak\smallskip
}{\par\medskip}

\newenvironment{corrige}[1]{%
  \par\medskip\noindent
  \textbf{\textcolor{nxVert}{Corrigé de \texttt{#1}}}\par\nopagebreak\smallskip
}{\par\medskip}

\newcommand{\baremeIndicatif}[1]{%
  \par\noindent{\footnotesize\textit{Barème indicatif : #1}}\par
}
\newcommand{\coupDePouce}[2]{%
  \par\noindent{\small\textbf{Coup de pouce #1.} #2}\par
}

% ===========================================================================
%  ÉVALUATIONS
% ===========================================================================
\newenvironment{evaluation}[2]{%
  \par\bigskip\noindent
  \textbf{\textcolor{nxBleu}{\large Évaluation \texttt{#1}}}\quad
  {\footnotesize #2~min}\par\nopagebreak\medskip
}{\par\bigskip}

% ===========================================================================
%  PYTHON
% ===========================================================================
\lstdefinestyle{nxpy}{%
  language=Python,%
  basicstyle=\ttfamily\small,%
  keywordstyle=\color{nxBleu}\bfseries,%
  commentstyle=\color{nxGris},%
  frame=single,%
  rulecolor=\color{nxGris},%
  numbers=left,%
  numberstyle=\tiny%
}
\lstnewenvironment{python}{\lstset{style=nxpy}}{}

% ===========================================================================
%  EN-TÊTES / PIEDS PROFESSIONNELS
% ===========================================================================
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[LE]{\small\scshape\color{nxGris}\leftmark}
\fancyhead[RO]{\small\scshape\color{nxGris}Nexus Réussite}
\fancyfoot[C]{\small\thepage}

% ===========================================================================
%  PAGE D'OUVERTURE DE CHAPITRE
% ===========================================================================
\newcommand{\ouverturechapitre}[4]{%
  \thispagestyle{plain}%
  \vspace*{1.2cm}%
  \chapter*{\color{nxBleu}\fontsize{26}{32}\selectfont\sffamily #1}%
  \addcontentsline{toc}{chapter}{#1}%
  \vspace{0.8cm}%
  \noindent\textcolor{nxBleu}{\large\sffamily\bfseries Ce que je vais savoir faire}\par
  \vspace{0.3cm}%
  #2%
  \vspace{0.6cm}%
  \begin{tcolorbox}[%
    colback=nxGris!6,%
    colframe=nxGris,%
    boxrule=0pt,%
    leftrule=1.2pt,%
    title=\textsc{Carte du chapitre},%
    fonttitle=\sffamily\bfseries,%
    enhanced,breakable%
  ]%
    #3%
  \end{tcolorbox}%
  \vspace{0.4cm}%
  \noindent\textcolor{nxOr}{\sffamily\bfseries Temps estimés :} #4%
  \par\vfill
}
