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
\newcommand{\nxRubriquePage}{\firstmarks\nxRubriqueMarks}
\newif\ifnxVSuppressTab
\nxVSuppressTabfalse

% ===========================================================================
%  ONGLETS LATÉRAUX DE RUBRIQUE
% ===========================================================================
% Bandeau vertical 12mm au bord extérieur, couleur accent pour rubrique active
% Position verticale = f(chapter) → index de pouce
\newcommand{\nxOngletRubrique}{%
  \ifnxVSuppressTab\else
  \begin{tikzpicture}[remember picture, overlay]
    \pgfmathsetmacro{\ongletY}{-25 - (\value{chapter}-1)*18}
    \ifodd\value{page}%
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north east)
        rectangle +(-12mm,-16mm);
      \node[rotate=90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=-6mm]current page.north east)
        {\MakeUppercase{\nxRubriquePage}};
    \else
      \fill[chapcolor!85] ([yshift=\ongletY mm]current page.north west)
        rectangle +(12mm,-16mm);
      \node[rotate=-90, text=white, font=\titrefont\fontsize{6}{6}\selectfont,
            anchor=south, inner sep=0pt]
        at ([yshift=\ongletY mm-8mm, xshift=6mm]current page.north west)
        {\MakeUppercase{\nxRubriquePage}};
    \fi
  \end{tikzpicture}%
  \fi
}

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
    \let\newpage\nxVQcmOriginalNewpage
    \begin{multicols}{2}% restaurer le gabarit diagnostics validé
  }%
}{%
  \end{multicols}%
  \let\dfrac\nxVQcmOriginalDfrac
  \clearpage
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
