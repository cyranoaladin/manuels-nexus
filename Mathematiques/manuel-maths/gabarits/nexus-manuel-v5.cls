% nexus-manuel-v5.cls — Maquette éditoriale v5 (prototype)
% Hérite de nexus-manuel v4.1, ajoute :
% - Grille EXERCICES 2 colonnes (68mm)
% - Onglets latéraux de rubrique
% - En-têtes rubriqués (verso=chapitre, recto=rubrique)
% - \cleardoublepage conditionnel pour rubriques majeures
% - Pages blanches avec motif léger
% - Environnement méthode double page
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel-v5}[2026/07/18 v5.0-proto Maquette editoriale Nexus]

% Charger la v4.1 comme base
\LoadClass{gabarits/nexus-manuel}

% ===========================================================================
%  VARIABLES DE RUBRIQUE (pilotent onglets et en-têtes)
% ===========================================================================
\newcommand{\nxRubrique}{}
\newcommand{\rubrique}[1]{\renewcommand{\nxRubrique}{#1}}

% ===========================================================================
%  ONGLETS LATÉRAUX DE RUBRIQUE
% ===========================================================================
% Bandeau vertical 12mm au bord extérieur, couleur accent pour rubrique active
% Position verticale = f(chapter) → index de pouce
\newcommand{\nxOngletRubrique}{%
  \ifx\nxRubrique\empty\else
  \begin{tikzpicture}[remember picture, overlay]
    \pgfmathsetmacro{\ongletY}{-25 - (\value{chapter}-1)*18}
    \ifodd\value{page}%
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north east)
        rectangle +(-12mm,-16mm);
      \node[rotate=90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=-6mm]current page.north east)
        {\MakeUppercase{\nxRubrique}};
    \else
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north west)
        rectangle +(12mm,-16mm);
      \node[rotate=-90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=6mm]current page.north west)
        {\MakeUppercase{\nxRubrique}};
    \fi
  \end{tikzpicture}%
  \fi
}

% Injecter l'onglet dans les en-têtes
\ohead{\nxOngletRubrique\nxMiniMotif\kern0.7em\sffamily\fontsize{7.5}{10}\selectfont\color{encre}%
  \ifodd\value{page}\nxRubrique\else\headmark\fi}

% ===========================================================================
%  PAGES BLANCHES DÉCORÉES (motif géométrique 4% en accent)
% ===========================================================================
\renewcommand{\cleardoublepage}{%
  \clearpage
  \ifodd\value{page}\else
    \thispagestyle{empty}%
    \begin{tikzpicture}[remember picture, overlay]
      \foreach \i in {1,...,5} {
        \foreach \j in {1,...,7} {
          \pgfmathsetmacro{\xp}{-80 + \i*40}
          \pgfmathsetmacro{\yp}{120 - \j*40}
          \node[opacity=0.04, rotate=45, font=\fontsize{14}{14}\selectfont,
                text=chapcolor] at ([xshift=\xp mm, yshift=\yp mm]current page.center)
            {$\diamond$};
        }
      }
    \end{tikzpicture}%
    \null\clearpage
  \fi
}

% ===========================================================================
%  SECTION RUBRIQUE (commence en belle page avec onglet)
% ===========================================================================
\newcommand{\debutrubrique}[1]{%
  \rubrique{#1}%
  \cleardoublepage
  \section*{\textcolor{chapcolor}{\MakeUppercase{#1}}}%
  \addcontentsline{toc}{section}{#1}%
}

% ===========================================================================
%  GRILLE EXERCICES — 2 colonnes 68mm, gouttière 6mm
% ===========================================================================
\RequirePackage{multicol}
\newenvironment{grilleExercices}{%
  \rubrique{Exercices}%
  \newgeometry{top=2.4cm, bottom=2.6cm, inner=2.0cm, outer=1.4cm,
    marginparwidth=0cm, marginparsep=0cm, headsep=0.7cm}%
  \begin{multicols}{2}[\section*{\textcolor{chapcolor}{\MakeUppercase{Exercices}}}]%
  \setlength{\columnseprule}{0.3pt}%
  \renewcommand{\columnseprulecolor}{\color{filetgris}}%
  \small
}{%
  \end{multicols}%
  \restoregeometry
}

% Exercice compact pour grille 2 colonnes (pas de marginnote)
\newenvironment{exerciceCompact}[3]{%
  \refstepcounter{exo}\par\smallskip\noindent
  \tikz[baseline=(n.base)]\node[fill=chapcolor, text=white,
    rounded corners=2pt, inner xsep=5pt, inner ysep=2.5pt](n)
    {\titrefont\scriptsize\theexo};%
  \enskip
  \ifnum#2=1\relax\parcoursUn\fi
  \ifnum#2=2\relax\parcoursDeux\fi
  \ifnum#2=3\relax\parcoursTrois\fi
  {\sffamily\fontsize{6}{7}\selectfont\color{encre!50} #3 min}%
  \par\nopagebreak\smallskip
}{\par\smallskip}

% ===========================================================================
%  MÉTHODE DOUBLE PAGE (exercice résolu + à vous de jouer)
% ===========================================================================
\newenvironment{methodeDoublePage}[2]{%
  \rubrique{Méthodes}%
  \cleardoublepage
  \noindent\begin{tcolorbox}[enhanced, frame hidden, boxrule=0pt, arc=3pt,
    colback=chapcolor!5,
    borderline west={3pt}{0pt}{chapcolor},
    left=12pt, right=12pt, top=10pt, bottom=10pt,
    before upper={\textcolor{chapcolor}{\titrefont\large
      Méthode #1 --- #2}\par\vspace{5pt}}]
}{%
  \end{tcolorbox}
}

% ===========================================================================
%  FAIRE LE POINT (QCM 2 colonnes en fin de chapitre)
% ===========================================================================
\newenvironment{faireLePoint}{%
  \rubrique{Auto-évaluation}%
  \cleardoublepage
  \section*{\textcolor{chapcolor}{\MakeUppercase{Faire le point}}}%
  \begin{multicols}{2}
}{%
  \end{multicols}
}

% ===========================================================================
%  CORRIGÉS FIN DE MANUEL (3 colonnes compactes)
% ===========================================================================
\newenvironment{corrigesCompacts}{%
  \rubrique{Corrigés}%
  \cleardoublepage
  \section*{Corrigés}%
  \begin{multicols}{3}
  \footnotesize
}{%
  \end{multicols}
}
