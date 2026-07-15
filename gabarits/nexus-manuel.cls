% nexus-manuel.cls — Classe du manuel Nexus Réussite
% Implémente le système visuel du gabarit : 3 strates, parcours ◆, pictogrammes, encadrés.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/07/15 v0.1 Manuel differencie Nexus Reussite]
\LoadClass[a4paper,11pt,twoside]{book}

\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath,amssymb,amsthm}
\RequirePackage[table]{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{marginnote,geometry,graphicx,enumitem,pifont,listings,fancyhdr,eurosym,microtype,titlesec}
\RequirePackage{libertine}
\geometry{a4paper,inner=2cm,outer=4.5cm,top=2.2cm,bottom=2.2cm,marginparwidth=3.6cm,marginparsep=0.5cm}
\raggedbottom
\widowpenalty=10000 \clubpenalty=10000
\renewcommand{\familydefault}{\rmdefault}
\setlength{\parskip}{0.45em}
\setlist{itemsep=0.25em,topsep=0.35em}

% ---- Palette Nexus ----
\definecolor{nxBleu}{HTML}{1B3A5C}
\definecolor{nxOr}{HTML}{C9A227}
\definecolor{nxGris}{HTML}{5A6472}
\definecolor{nxRouge}{HTML}{B0413E}
\definecolor{nxVert}{HTML}{2E6E4E}

% Hiérarchie : titre d'ouverture, section-capacité, sous-partie.
\titleformat{\section}{\sffamily\bfseries\color{nxBleu}\fontsize{15}{19}\selectfont}{\thesection}{0.8em}{}
\titlespacing*{\section}{0pt}{2.1ex plus .4ex}{1.0ex}
\titleformat{\subsection}{\sffamily\bfseries\color{nxBleu!85!black}\fontsize{12}{15}\selectfont}{\thesubsection}{0.7em}{}
\titlespacing*{\subsection}{0pt}{1.6ex plus .3ex}{.7ex}
\newcommand{\sectionCapacite}[2]{\section{#1}\margeAppui{\textbf{Je sais...} #2}}

% ---- Pictogrammes / parcours ----
\newcommand{\parcoursUn}{\textcolor{nxOr}{\ding{117}}}
\newcommand{\parcoursDeux}{\textcolor{nxOr}{\ding{117}\ding{117}}}
\newcommand{\parcoursTrois}{\textcolor{nxOr}{\ding{117}\ding{117}\ding{117}}}
\newcommand{\pictoOral}{\textcolor{nxBleu}{\ding{110}~Oral}}
\newcommand{\pictoPython}{\textcolor{nxBleu}{\texttt{>\!\!>~Python}}}

% ---- Strate 1 : encadrés du cours ----
\newtcolorbox{nxdef}[1][]{colback=nxBleu!4,colframe=nxBleu,boxrule=0pt,leftrule=1.2pt,title=\textsc{Définition}~#1,fonttitle=\sffamily\bfseries,enhanced,breakable}
\newtcolorbox{nxthm}[1][]{colback=nxBleu!5,colframe=nxBleu!80!black,boxrule=0pt,leftrule=1.2pt,title=\textsc{Théorème}~#1,fonttitle=\sffamily\bfseries,enhanced,breakable}
\newtcolorbox{nxprop}[1][]{colback=nxGris!6,colframe=nxGris,boxrule=0pt,leftrule=1.2pt,title=\textsc{Propriété}~#1,fonttitle=\sffamily\bfseries,enhanced,breakable}
\newcommand{\definition}[2][]{\begin{nxdef}[#1]#2\end{nxdef}}
\newcommand{\theoreme}[2][]{\begin{nxthm}[#1]#2\end{nxthm}}
\newcommand{\propriete}[2][]{\begin{nxprop}[#1]#2\end{nxprop}}
\newcommand{\exemple}[1]{\par\noindent\textbf{\textcolor{nxVert}{Exemple.}} #1\par}
\newcommand{\contreexemple}[1]{\par\noindent\textbf{\textcolor{nxRouge}{Contre-exemple.}} #1\par}

% ---- Strate 2 : marge d'appui et erreurs ----
\newcommand{\margeAppui}[1]{\marginnote{\footnotesize\color{nxGris}\itshape #1}}
\newcommand{\commentaireMarge}[1]{\marginnote{\footnotesize\color{nxBleu}#1}}
\newtcolorbox{nxerr}{colback=nxRouge!6,colframe=nxRouge,boxrule=0pt,leftrule=1.2pt,title={\ding{115}~\textsc{Erreur fréquente}},fonttitle=\sffamily\bfseries,breakable}
\newcommand{\erreurFrequente}[1]{\begin{nxerr}#1\end{nxerr}}

% ---- Strate 3 : approfondissement ----
\newtcolorbox{nxstar}{colback=nxBleu!5,colframe=nxBleu,boxrule=0.4pt,title={$\bigstar$~\textsc{Pour aller plus loin}},fonttitle=\sffamily\bfseries,breakable}
\newcommand{\approfondissement}[1]{\begin{nxstar}#1\end{nxstar}}

% ---- Fiches méthodes ----
\newtcolorbox{fmbox}[2]{colback=nxOr!6,colframe=nxOr!80!black,boxrule=0pt,leftrule=1.2pt,title={\textsc{Méthode #1} — #2},fonttitle=\sffamily\bfseries,enhanced,breakable}
\newenvironment{fichemethode}[2]{\begin{fmbox}{#1}{#2}}{\end{fmbox}}
\newcommand{\quandUtiliser}[1]{\paragraph{Quand l'utiliser.}#1}
\newcommand{\pasApas}[1]{\paragraph{La méthode pas à pas.}#1}
\newcommand{\exempleRedige}[1]{\paragraph{Exemple rédigé.}#1}
\newcommand{\pieges}[1]{\paragraph{Les pièges.}#1}
\newcommand{\verifier}[1]{\paragraph{Vérifier son résultat.}#1}
\newcommand{\sEntrainer}[1]{\paragraph{S'entraîner.}#1}
\newcommand{\refExos}[1]{\textit{(renvois exercices #1 : complétés à l'assemblage)}}

% ---- Exercices / corrigés ----
% \begin{exercice}{ID}{parcours(1|2|3)}{durée min}
\newcounter{exo}
\newenvironment{exercice}[3]{%
  \refstepcounter{exo}\par\medskip\noindent
  \textbf{\textcolor{nxBleu}{Exercice \theexo}}\quad
  \ifnum#2=1\parcoursUn\fi\ifnum#2=2\parcoursDeux\fi\ifnum#2=3\parcoursTrois\fi
  \quad{\footnotesize\texttt{#1} — #3~min}\par\nopagebreak\smallskip
}{\par\medskip}
\newenvironment{corrige}[1]{\par\medskip\noindent\textbf{\textcolor{nxVert}{Corrigé de \texttt{#1}}}\par\nopagebreak\smallskip}{\par\medskip}
\newcommand{\baremeIndicatif}[1]{\par\noindent{\footnotesize\textit{Barème indicatif : #1}}\par}
\newcommand{\coupDePouce}[2]{\par\noindent{\small\textbf{Coup de pouce #1.} #2}\par}

% ---- Évaluations ----
\newenvironment{evaluation}[2]{%
  \par\bigskip\noindent
  \textbf{\textcolor{nxBleu}{\large Évaluation \texttt{#1}}}\quad{\footnotesize #2~min}\par\nopagebreak\medskip
}{\par\bigskip}

% ---- Python ----
\lstdefinestyle{nxpy}{language=Python,basicstyle=\ttfamily\small,keywordstyle=\color{nxBleu}\bfseries,
  commentstyle=\color{nxGris},frame=single,rulecolor=\color{nxGris},numbers=left,numberstyle=\tiny}
\lstnewenvironment{python}{\lstset{style=nxpy}}{}

% ---- En-têtes ----
\pagestyle{fancy}\fancyhf{}
\fancyhead[LE]{\small\leftmark}\fancyhead[RO]{\small Nexus Réussite}
\fancyfoot[C]{\thepage}
\newcommand{\ouverturechapitre}[4]{\thispagestyle{plain}\vspace*{1.2cm}\chapter*{\color{nxBleu}#1}\addcontentsline{toc}{chapter}{#1}\noindent\textcolor{nxBleu}{\large\sffamily\bfseries Ce que je vais savoir faire}\par#2\medskip\begin{tcolorbox}[colback=nxGris!6,colframe=nxGris,boxrule=0pt,leftrule=1.2pt,title=\textsc{Carte du chapitre},fonttitle=\sffamily\bfseries]#3\end{tcolorbox}\noindent\textcolor{nxOr}{\sffamily\bfseries Temps estimés :} #4\par\vfill}
