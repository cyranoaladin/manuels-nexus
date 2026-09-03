# Registre factuel de la charte et du runtime Nexus

Ce registre inventorie les sources physiques et les preuves de consommation ; il ne modifie ni la charte ni les builds.

## Synthèse

- Fichiers physiques : **64**
- Contenus uniques : **43**
- Duplicatas exacts au-delà du premier exemplaire : **21** dans **18** groupes
- Cible de classe canonique : `gabarits/common/nexus-manuel.cls`
- Cible de style canonique : `gabarits/common/nexus-charte.sty`
- Potentiels runtime non canoniques : **16**
- Une implémentation canonique de classe : **TRUE**
- Une implémentation canonique de charte : **TRUE**
- Runtime sans wrapper de compatibilité observé : **FALSE**

La présence d'une cible canonique unique n'implique pas encore un runtime sans wrappers. Les `.fls` non attestés ne valent pas preuve d'un build final au SHA courant.

## CURRENT_CANONICAL_MANIFEST_CHAPTERS

| Manuel | Chapitres | Source réellement consommée |
|---|---:|---|
| 1SPE | 10 | `Mathematiques/manuel-maths/scripts/assemble_manuel.py` |
| TSPE | 11 | `Mathematiques/manuel-maths/scripts/assemble_manuel.py` |
| TCOMPL | 9 | `Mathematiques/manuel-maths/scripts/assemble_manuel.py` |
| TEXPERTES | 5 | `Mathematiques/manuel-maths/scripts/assemble_manuel.py` |
| 1NSI | 10 | `NSI/manifests/books/1NSI.json` |
| TNSI | 7 | `NSI/manifests/books/TNSI.json` |

## Enregistreurs `.fls` disponibles

| FLS | Manuel | Variante | Fraîcheur | Entrées du registre |
|---|---|---|---|---:|
| `audit/D7_VISUAL_REVIEW/runtime/maquette.fls` | D7_MAQUETTE | maquette | STALE_ATTESTED_OTHER_SHA | 9 |

## Fichiers

| Chemin | Rôle | Canonique | SHA-256 | Duplicata de | Références directes | `.fls` | Déprécié | Historique |
|---|---|:---:|---|---|---:|---:|:---:|:---:|
| `Mathematiques/manuel-maths/gabarits/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | NO | `82c0ae2dfd98858c817f30193c7cee6f1f08327fb98f1090c6127902575028c3` | `gabarits/common/chapitre_master.tex` | 1 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `cd59d965d61546cb6fd2afe41183ac091ebb08202630bc8c56771ed3595c4ca9` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `d42b1df562e726f06d78636f4c9c607f57c0ddcd557450f0270af55c8b1d61f8` | — | 6 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` | `gabarits/common/nexus-code.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `7debbf9f9b82d7af661898b62b208791b840ce071e79fd340b347c94425d0430` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2ecc021fe98ca3d20e76699252f4864d07996ec50d92af8a46bf2d3cd6670eda` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2c6aacc7fe27fd43e9b0f7a902543b3e005370d913ee7bf1f626abb1d10bd7e3` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `aca44416f30e77ec385d97286028f1894ef5079601f4ff2474349eea4a21efe2` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` | — | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` | — | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | `gabarits/common/nexus-icons.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `5481ac50897d8e5017f49b82c01279d1948e6c83f1d1dee2d4ea01e56c3cc714` | — | 3 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `42deffecf8e0650159de0af4529b032f27b4d904e9b056ec9fc42fbfba101f19` | — | 6 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `04cb45a5f8796d9ce0a25bd2c0f23b190b515056e2f69f5b7eac64b5f0c88f14` | `gabarits/common/nexus-margin-rail.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `5d478c0ec3701c54d8de961ad9c1c95909d2b2317ca1658a88cb10dd14d3b1a8` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `964afdd31c793fbcbd1883b1b75b662f62bbe38458ddaf75b6d7bf61c5598c6e` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` | `gabarits/common/nexus-signatures.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/objet_standalone.tex` | OBJECT_RUNTIME_TEMPLATE | NO | `c9c4c06915ff0cc38ea7393621547a39856705a8d0f19527bb89f3ecd300c769` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-nsi.tex` | HISTORICAL_REFERENCE | NO | `f753b91d4d14372e83a0a827a5f897788520cf310d541f12af6b26aefe602209` | — | 0 | 0 | YES | YES |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-physique.tex` | HISTORICAL_REFERENCE | NO | `735765f581c017ed67a00895d089c60e0843ba9195e3a8078d459943008c061c` | — | 0 | 0 | YES | YES |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/chapitres/chap-suites.tex` | HISTORICAL_REFERENCE | NO | `f727a3abda7ad76d68c17ca4e0337f9d417dbb1cf716f2390d2c15babc2bd6bf` | — | 0 | 0 | YES | YES |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/main.tex` | HISTORICAL_REFERENCE | NO | `56470e38efbd04a24d20b925b44825b34519c34c82acb280b7128072f02793d4` | — | 0 | 0 | YES | YES |
| `Mathematiques/manuel-maths/gabarits/reference-v4/manuel-kit/manuel.sty` | HISTORICAL_REFERENCE | NO | `e9130fda64ec9d6d06b2cf2ffad7e67af271528b9ed9b025de303a5216661ee9` | — | 1 | 0 | YES | YES |
| `Mathematiques/manuel-maths/gabarits/specimen-pont-v6.tex` | VISUAL_SPECIMEN_TEMPLATE | NO | `1496c0e09d0edc86163889c13936c962ae3153d8bb9a0c97869ed354dfbd2f04` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/specimen-v6.tex` | VISUAL_SPECIMEN_TEMPLATE | NO | `a1b55799f72aa1cd55d87711d6c0045f2a95bb89a0748de1e4e655122f87efb0` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/specimen.tex` | VISUAL_SPECIMEN_TEMPLATE | NO | `902b89b959d4684a8cb751629e0d7a8482a745bdb90fa0d06aa6b00d1b79e67c` | — | 0 | 0 | NO | NO |
| `NSI/corpus_nsi/02_modeles_documents/nsi-preamble.sty` | REFERENCE_MODEL_STYLE | NO | `9360a17474193420c6533a267420a536cabcbce24faade497b3b44bb304c6aef` | — | 18 | 0 | NO | NO |
| `NSI/gabarits/book_master.tex` | BOOK_RUNTIME_TEMPLATE | NO | `a16442c965c32c4696680ee150cb14d2071e30b8a1083c3b98e68e8387b0a4bd` | — | 2 | 0 | NO | NO |
| `NSI/gabarits/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | NO | `b64379616544fb90df50692f5eeaa34c3a2b2c96793ef58608063c45b88d11b8` | — | 1 | 0 | NO | NO |
| `NSI/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `cd59d965d61546cb6fd2afe41183ac091ebb08202630bc8c56771ed3595c4ca9` | `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `d42b1df562e726f06d78636f4c9c607f57c0ddcd557450f0270af55c8b1d61f8` | `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | 3 | 0 | NO | NO |
| `NSI/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `27a6bb961ea9fb00bb2046f987ab1f76aba832dd7f5def189bbf6d32bd07fcf5` | — | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `7debbf9f9b82d7af661898b62b208791b840ce071e79fd340b347c94425d0430` | `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2ecc021fe98ca3d20e76699252f4864d07996ec50d92af8a46bf2d3cd6670eda` | `Mathematiques/manuel-maths/gabarits/nexus-decor.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2c6aacc7fe27fd43e9b0f7a902543b3e005370d913ee7bf1f626abb1d10bd7e3` | `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `aca44416f30e77ec385d97286028f1894ef5079601f4ff2474349eea4a21efe2` | `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` | `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` | `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | `gabarits/common/nexus-icons.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `5481ac50897d8e5017f49b82c01279d1948e6c83f1d1dee2d4ea01e56c3cc714` | `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | 2 | 0 | NO | NO |
| `NSI/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `42deffecf8e0650159de0af4529b032f27b4d904e9b056ec9fc42fbfba101f19` | `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | 5 | 0 | NO | NO |
| `NSI/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `04cb45a5f8796d9ce0a25bd2c0f23b190b515056e2f69f5b7eac64b5f0c88f14` | `gabarits/common/nexus-margin-rail.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `5d478c0ec3701c54d8de961ad9c1c95909d2b2317ca1658a88cb10dd14d3b1a8` | `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `964afdd31c793fbcbd1883b1b75b662f62bbe38458ddaf75b6d7bf61c5598c6e` | `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` | `gabarits/common/nexus-signatures.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/objet_standalone.tex` | OBJECT_RUNTIME_TEMPLATE | NO | `c9c4c06915ff0cc38ea7393621547a39856705a8d0f19527bb89f3ecd300c769` | `Mathematiques/manuel-maths/gabarits/objet_standalone.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/specimen.tex` | VISUAL_SPECIMEN_TEMPLATE | NO | `a3dccdf4ceb7d315f02242303135b9e229701d4718ff29a5baab6365f23a2397` | — | 0 | 0 | NO | NO |
| `gabarits/common/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | YES | `82c0ae2dfd98858c817f30193c7cee6f1f08327fb98f1090c6127902575028c3` | — | 0 | 0 | NO | NO |
| `gabarits/common/nexus-arbres.sty` | CANONICAL_SUPPORT_STYLE | YES | `5569ec0838d22af6e7a7b38a177471d7ba64b6c3f88fa758e4df20e3dedd40f9` | — | 0 | 0 | NO | NO |
| `gabarits/common/nexus-boites.sty` | CANONICAL_SUPPORT_STYLE | YES | `e2cdfd96d2ac384a7d3f14a3cc0ae67dce585a97a53c2c65c3e62ac544d6fabf` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-charte.sty` | CANONICAL_STYLE_IMPLEMENTATION | YES | `a27c7a003bcd7c89e3341fd5ef90a9c073b05d558230d084fa0b3bad74902113` | — | 23 | 0 | NO | NO |
| `gabarits/common/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` | — | 1 | 0 | NO | NO |
| `gabarits/common/nexus-couverture.sty` | CANONICAL_SUPPORT_STYLE | YES | `54b30338b4ceeddf23367bf1467616b0603244905b33fa7e8c806175913e8f1b` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-decor.sty` | CANONICAL_SUPPORT_STYLE | YES | `56180b5f03ed4ebccf58059a62c6064e97254316c2ee629b94f0161f025b7b31` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-exercices.sty` | CANONICAL_SUPPORT_STYLE | YES | `530c1f35d41a80e6fb4363396a60b71dba00b3dd8689cd1623ab4a4be93a7942` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-figures-bib.sty` | CANONICAL_SUPPORT_STYLE | YES | `174dc7dd86fafa7d74f32a2cee77cc880cdc25403a4f090259afbbc5e5fc54cb` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | — | 1 | 0 | NO | NO |
| `gabarits/common/nexus-manuel.cls` | CANONICAL_CLASS_IMPLEMENTATION | YES | `f0dc5a356692e1ea1b587ab9738d1b2b78b594a27a8ed8d0c46ea6767dfd4dc6` | — | 23 | 1 | NO | NO |
| `gabarits/common/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `04cb45a5f8796d9ce0a25bd2c0f23b190b515056e2f69f5b7eac64b5f0c88f14` | — | 0 | 0 | NO | NO |
| `gabarits/common/nexus-pages-froides.sty` | CANONICAL_SUPPORT_STYLE | YES | `2b27ed9c641e0c0f0a4855a176197bc01099ada96e7af02f7e39862eeb16b652` | — | 14 | 0 | NO | NO |
| `gabarits/common/nexus-pont.sty` | CANONICAL_SUPPORT_STYLE | YES | `2d4c8839add6d3e83e9ba6044995bd7e673e2e03a88d7390281d1458281bfe50` | — | 14 | 0 | NO | NO |
| `gabarits/common/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` | — | 1 | 0 | NO | NO |
| `gabarits/maths/nexus-maths.sty` | CANONICAL_DISCIPLINE_ADAPTER | YES | `537ef320e5658026e08f2b7302561d8b53f2958581f4d40b7080f0a41b025883` | — | 2 | 0 | NO | NO |
| `gabarits/nsi/nexus-nsi.sty` | CANONICAL_DISCIPLINE_ADAPTER | YES | `76c3e49a2be44a39b96d729683a01703c5a2c90560d78c2dca5f81a8ef66982a` | — | 2 | 0 | NO | NO |

## Duplicatas exacts

- `04cb45a5f8796d9ce0a25bd2c0f23b190b515056e2f69f5b7eac64b5f0c88f14` : `gabarits/common/nexus-margin-rail.tex`, `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`, `NSI/gabarits/nexus-margin-rail.tex`
- `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` : `gabarits/common/nexus-code.tex`, `Mathematiques/manuel-maths/gabarits/nexus-code.tex`
- `2c6aacc7fe27fd43e9b0f7a902543b3e005370d913ee7bf1f626abb1d10bd7e3` : `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty`, `NSI/gabarits/nexus-exercices-v6.sty`
- `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` : `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex`, `NSI/gabarits/nexus-figures-nsi.tex`
- `2ecc021fe98ca3d20e76699252f4864d07996ec50d92af8a46bf2d3cd6670eda` : `Mathematiques/manuel-maths/gabarits/nexus-decor.sty`, `NSI/gabarits/nexus-decor.sty`
- `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` : `gabarits/common/nexus-icons.tex`, `Mathematiques/manuel-maths/gabarits/nexus-icons.tex`, `NSI/gabarits/nexus-icons.tex`
- `42deffecf8e0650159de0af4529b032f27b4d904e9b056ec9fc42fbfba101f19` : `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`, `NSI/gabarits/nexus-manuel.cls`
- `5481ac50897d8e5017f49b82c01279d1948e6c83f1d1dee2d4ea01e56c3cc714` : `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`, `NSI/gabarits/nexus-manuel-v5.cls`
- `5d478c0ec3701c54d8de961ad9c1c95909d2b2317ca1658a88cb10dd14d3b1a8` : `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty`, `NSI/gabarits/nexus-pages-froides.sty`
- `7debbf9f9b82d7af661898b62b208791b840ce071e79fd340b347c94425d0430` : `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty`, `NSI/gabarits/nexus-couverture.sty`
- `82c0ae2dfd98858c817f30193c7cee6f1f08327fb98f1090c6127902575028c3` : `gabarits/common/chapitre_master.tex`, `Mathematiques/manuel-maths/gabarits/chapitre_master.tex`
- `964afdd31c793fbcbd1883b1b75b662f62bbe38458ddaf75b6d7bf61c5598c6e` : `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty`, `NSI/gabarits/nexus-pont-v6.sty`
- `aca44416f30e77ec385d97286028f1894ef5079601f4ff2474349eea4a21efe2` : `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty`, `NSI/gabarits/nexus-figures-bib.sty`
- `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` : `gabarits/common/nexus-signatures.tex`, `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex`, `NSI/gabarits/nexus-signatures.tex`
- `c9c4c06915ff0cc38ea7393621547a39856705a8d0f19527bb89f3ecd300c769` : `Mathematiques/manuel-maths/gabarits/objet_standalone.tex`, `NSI/gabarits/objet_standalone.tex`
- `cd59d965d61546cb6fd2afe41183ac091ebb08202630bc8c56771ed3595c4ca9` : `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty`, `NSI/gabarits/nexus-boites-v6.sty`
- `d42b1df562e726f06d78636f4c9c607f57c0ddcd557450f0270af55c8b1d61f8` : `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`, `NSI/gabarits/nexus-charte-v6.sty`
- `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` : `Mathematiques/manuel-maths/gabarits/nexus-figures.tex`, `NSI/gabarits/nexus-figures.tex`
