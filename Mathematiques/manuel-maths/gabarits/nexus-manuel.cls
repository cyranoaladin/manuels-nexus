% Redirection canonique vers la classe unique gabarits/common/nexus-manuel.cls
\IfFileExists{gabarits/common/nexus-manuel.cls}{%
  \input{gabarits/common/nexus-manuel.cls}%
}{%
  \IfFileExists{../../gabarits/common/nexus-manuel.cls}{%
    \input{../../gabarits/common/nexus-manuel.cls}%
  }{%
    \input{nexus-manuel.cls}%
  }%
}
