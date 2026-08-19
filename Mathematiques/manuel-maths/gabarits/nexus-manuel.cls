% Redirection canonique vers gabarits/common/nexus-manuel.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/07/20 v6.0 Wrapper Compatibilite nexus-manuel - Canonique]
\IfFileExists{../../gabarits/common/nexus-manuel.cls}{%
  \input{../../gabarits/common/nexus-manuel.cls}%
}{%
  \IfFileExists{../gabarits/common/nexus-manuel.cls}{%
    \input{../gabarits/common/nexus-manuel.cls}%
  }{%
  }%
}
