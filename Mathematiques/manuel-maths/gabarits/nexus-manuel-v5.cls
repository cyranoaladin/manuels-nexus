% nexus-manuel-v5.cls — Maquette éditoriale v5, itération 2
% Corrections : onglets par marks, pages blanches overlay pur, call-outs
% méthodes, renvois, IDs supprimés en grille exercices, fractions compactes.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel-v5}[2026/07/18 v5.1-it2 Maquette editoriale Nexus]

\LoadClass{gabarits/nexus-manuel}

% ===========================================================================
%  FIX 1 — ONGLETS PAR MARKS (synchronisé avec la coupure de page)
% ===========================================================================
% On utilise \markright pour la rubrique, \markboth pour chapitre (déjà fait par KOMA).
% L'onglet lit le mark de la page courante, jamais une globale.
\newcommand{\rubrique}[1]{\markright{#1}}

\newcommand{\nxOngletRubrique}{%
  \ifx\rightmark\empty\else
  \begin{tikzpicture}[remember picture, overlay]
    \pgfmathsetmacro{\ongletY}{-25 - (\value{chapter}-1)*18}
    \ifodd\value{page}%
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north east)
        rectangle +(-12mm,-16mm);
      \node[rotate=90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=-6mm]current page.north east)
        {\MakeUppercase{\rightmark}};
    \else
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north west)
        rectangle +(12mm,-16mm);
      \node[rotate=-90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=6mm]current page.north west)
        {\MakeUppercase{\rightmark}};
    \fi
  \end{tikzpicture}%
  \fi
}

% En-têtes rubriqués : verso = chapitre, recto = rubrique (via mark)
\clearpairofpagestyles
\ohead{\nxOngletRubrique\nxMiniMotif\kern0.7em\sffamily\fontsize{7.5}{10}\selectfont\color{encre}%
  \ifodd\value{page}\rightmark\else\headmark\fi}
\ofoot{\tikz\node[fill=chapcolor, text=white, circle,
  inner sep=3.6pt, font=\titrefont\small]{\thepage};}
\ifoot{\sffamily\fontsize{6.5}{8}\selectfont\color{encre!50}\addfontfeatures{LetterSpace=6}\MakeUppercase{Nexus Réussite}}

% ===========================================================================
%  FIX 2 — PAGES BLANCHES : overlay pur, couche texte vide
% ===========================================================================
% Style de page dédié pour les pages blanches décorées
\newpairofpagestyles{blanche}{%
  \clearpairofpagestyles
  \ofoot{\tikz\node[fill=chapcolor, text=white, circle,
    inner sep=3.6pt, font=\titrefont\small]{\thepage};}
}

\renewcommand{\cleardoublepage}{%
  \clearpage
  \ifodd\value{page}\else
    \thispagestyle{blanche}%
    \begin{tikzpicture}[remember picture, overlay]
      % Motif géométrique : losanges 4% en grille régulière
      \foreach \i in {1,...,6} {
        \foreach \j in {1,...,8} {
          \pgfmathsetmacro{\xp}{-95 + \i*38}
          \pgfmathsetmacro{\yp}{140 - \j*35}
          \draw[chapcolor, opacity=0.04, line width=0.6pt, rotate=45]
            ([xshift=\xp mm, yshift=\yp mm]current page.center)
            +(-4mm,0) -- +(0,4mm) -- +(4mm,0) -- +(0,-4mm) -- cycle;
        }
      }
    \end{tikzpicture}%
    \null\clearpage
  \fi
}

% ===========================================================================
%  SECTION RUBRIQUE
% ===========================================================================
\newcommand{\debutrubrique}[1]{%
  \rubrique{#1}%
  \cleardoublepage
  \section*{\textcolor{chapcolor}{\MakeUppercase{#1}}}%
  \addcontentsline{toc}{section}{#1}%
}

% ===========================================================================
%  GRILLE EXERCICES — 2 colonnes, IDs supprimés, losanges sur badge
% ===========================================================================
\RequirePackage{multicol}

% Flag pour contexte 2 colonnes (interdit \marginnote)
\newif\ifnxDeuxColonnes\nxDeuxColonnesfalse

% Rediriger \marginnote en contexte 2 colonnes (FIX 3/5)
\let\nxOrigMarginnote\marginnote
\renewcommand{\marginnote}[1]{%
  \ifnxDeuxColonnes\else\nxOrigMarginnote{#1}\fi
}

\newenvironment{grilleExercices}{%
  \rubrique{Exercices}%
  \newgeometry{top=2.4cm, bottom=2.6cm, inner=2.0cm, outer=1.4cm,
    marginparwidth=0cm, marginparsep=0cm, headsep=0.7cm}%
  \nxDeuxColonnestrue
  \begin{multicols}{2}[\section*{\textcolor{chapcolor}{\MakeUppercase{Exercices}}}]%
  \setlength{\columnseprule}{0.3pt}%
  \renewcommand{\columnseprulecolor}{\color{filetgris}}%
  \small
  % FIX 6 : fractions compactes en colonne étroite
  \everymath{\displaystyle\textstyle}%
  \renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}%
}{%
  \end{multicols}%
  \nxDeuxColonnesfalse
  \restoregeometry
}

% Exercice compact avec losanges et sans ID en marge (FIX 5)
\newenvironment{exerciceCompact}[3]{%
  \refstepcounter{exo}\par\smallskip\noindent
  % Badge numéroté avec losanges de difficulté
  \ifnum#2=3\relax
    \tikz[baseline=(n.base)]\node[fill=chapcolor, text=white,
      rounded corners=2pt, inner xsep=5pt, inner ysep=2.5pt](n)
      {\titrefont\scriptsize\theexo};%
    \enskip\parcoursUn\parcoursDeux\parcoursTrois
  \else\ifnum#2=2\relax
    \tikz[baseline=(n.base)]\node[fill=chapcolor!60, text=white,
      rounded corners=2pt, inner xsep=5pt, inner ysep=2.5pt](n)
      {\titrefont\scriptsize\theexo};%
    \enskip\parcoursUn\parcoursDeux
  \else
    \tikz[baseline=(n.base)]\node[draw=chapcolor, text=chapcolor,
      rounded corners=2pt, inner xsep=5pt, inner ysep=2.5pt](n)
      {\titrefont\scriptsize\theexo};%
    \enskip\parcoursUn
  \fi\fi
  {\sffamily\fontsize{5.5}{6.5}\selectfont\color{encre!40} #3\,min}%
  % Pas de \marginnote ici (contexte 2 colonnes)
  \par\nopagebreak\smallskip
}{\par\smallskip}

% ===========================================================================
%  FIX 3 — MÉTHODES : call-outs ①②③, pas de marginnotes
% ===========================================================================
% Compteur pour les étapes de méthode
\newcounter{nxCallout}
\newcommand{\callout}[1]{%
  \stepcounter{nxCallout}%
  \tikz[baseline=(c.base)]\node[fill=chapcolor, text=white, circle,
    inner sep=1.5pt, font=\titrefont\fontsize{6}{6}\selectfont](c)
    {\thenxCallout};%
  \enskip{\sffamily\fontsize{7.5}{9}\selectfont\color{encre!70}#1}%
}

\newenvironment{methodeDoublePage}[2]{%
  \rubrique{Méthodes}%
  \cleardoublepage
  \setcounter{nxCallout}{0}%
  \noindent\begin{tcolorbox}[enhanced, frame hidden, boxrule=0pt, arc=3pt,
    colback=chapcolor!5,
    borderline west={3pt}{0pt}{chapcolor},
    left=12pt, right=12pt, top=10pt, bottom=10pt,
    before upper={\textcolor{chapcolor}{\titrefont\large
      Méthode #1 --- #2}\par\vspace{5pt}}]
}{%
  \end{tcolorbox}
}

% Sous-rubriques de la méthode appariée
\newcommand{\exerciceResolu}{\par\medskip\noindent\textcolor{chapcolor}{\titrefont\normalsize Exercice résolu}\par\smallskip}
\newcommand{\avousDeJouer}{\par\medskip\noindent\textcolor{chapcolor}{\titrefont\normalsize À vous de jouer}\par\smallskip}

% ===========================================================================
%  FAIRE LE POINT — QCM 2 colonnes, items insécables
% ===========================================================================
\newenvironment{faireLePoint}{%
  \rubrique{Auto-évaluation}%
  \cleardoublepage
  \section*{\textcolor{chapcolor}{\MakeUppercase{Faire le point}}}%
  \nxDeuxColonnestrue
  \begin{multicols}{2}%
  \small
  % FIX 6 : fractions compactes
  \renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}%
}{%
  \end{multicols}%
  \nxDeuxColonnesfalse
}

% ===========================================================================
%  CORRIGÉS FIN DE MANUEL (3 colonnes compactes)
% ===========================================================================
\newenvironment{corrigesCompacts}{%
  \rubrique{Corrigés}%
  \cleardoublepage
  \section*{\textcolor{chapcolor}{\MakeUppercase{Corrigés}}}%
  \nxDeuxColonnestrue
  \begin{multicols}{3}
  \footnotesize
  \renewcommand{\dfrac}[2]{\tfrac{##1}{##2}}%
}{%
  \end{multicols}%
  \nxDeuxColonnesfalse
}

% ===========================================================================
%  FIX 4 — RENVOIS (macros pour génération depuis META)
% ===========================================================================
\newcommand{\renvoiMethode}[2]{%
  {\sffamily\fontsize{6}{7}\selectfont\color{chapcolor}$\rightarrow$~M#1 p.\,#2}%
}
\newcommand{\renvoiCorrige}[1]{%
  {\sffamily\fontsize{6}{7}\selectfont\color{encre!50}Corrigé p.\,#1}%
}
\newcommand{\renvoiExercices}[1]{%
  {\sffamily\fontsize{7}{9}\selectfont\textcolor{chapcolor}{S'entraîner :} ex.\,#1}%
}
