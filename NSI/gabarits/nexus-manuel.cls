% Redirection canonique vers la classe unique gabarits/common/nexus-manuel.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{gabarits/nexus-manuel}[2026/07/20 v6.0 Wrapper Compatibilite NSI - Canonique]
\IfFileExists{gabarits/common/nexus-manuel.cls}{%
  \input{gabarits/common/nexus-manuel.cls}%
}{%
  \IfFileExists{../../gabarits/common/nexus-manuel.cls}{%
    \input{../../gabarits/common/nexus-manuel.cls}%
  }{%
    \input{nexus-manuel.cls}%
  }%
}
