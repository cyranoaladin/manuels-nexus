% Redirection canonique vers gabarits/common/nexus-manuel.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel-v5}[2026/07/20 v6.0 Wrapper Compatibilite nexus-manuel-v5 - Canonique]
\def\nxVBaseCompatibility{1}
\IfFileExists{../../gabarits/common/nexus-manuel.cls}{%
  \input{../../gabarits/common/nexus-manuel.cls}
  \RequirePackage{../../gabarits/common/nexus-charte}%
}{%
  \RequirePackage{nexus-charte}%
}
