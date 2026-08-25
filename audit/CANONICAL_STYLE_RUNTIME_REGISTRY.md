# Registre factuel de la charte et du runtime Nexus

Ce registre inventorie les sources physiques et les preuves de consommation ; il ne modifie ni la charte ni les builds.

## Synthèse

- Fichiers physiques : **63**
- Contenus uniques : **42**
- Duplicatas exacts au-delà du premier exemplaire : **21** dans **18** groupes
- Cible de classe canonique : `gabarits/common/nexus-manuel.cls`
- Cible de style canonique : `gabarits/common/nexus-charte.sty`
- Potentiels runtime non canoniques : **16**
- Une implémentation canonique de classe : **TRUE**
- Une implémentation canonique de charte : **TRUE**
- Runtime sans wrapper de compatibilité observé : **TRUE**

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
| `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2185848e26ea5152a1570828c1b5c29d5158dcf38b32702be680c617e9f90d36` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `90391485645cb6fa03ae6ffc3b315d612e714b69dcc3c0efd547a7d8fca38137` | — | 5 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` | `gabarits/common/nexus-code.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `57327021b50fb44434874fb4fe00583ddb2160908ca8379d4d07d670f257685e` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `1b23d537120ebd2437c9f6c59d5b99c24c4ecd1286028b4cc2441eabf0c758d4` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `25b72f131634021353e07500252a5cf69110faa106c670659240b796cd59edda` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `d441187e66d487806714abf7bba768aa61b20c6d18638b39f030e6c6ec190bfa` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` | — | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` | — | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | `gabarits/common/nexus-icons.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `5e1d7fdb258865321ee93a34a41a2de806edd93ad36b256829ed1bce4043a7dc` | — | 3 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `90ea5ae521bcf028fbc5fc240639636c24eb2e1cfc934e0af9a2c94ae7269e07` | — | 6 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `6ffc96378d2dece2dd7479647b7b7046025fe3c12a1bdd0fcf41d8787e277823` | `gabarits/common/nexus-margin-rail.tex` | 0 | 1 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `4ecc02468ab1ab2859d7fe1f1930538ec35a9058dbfab79a1e86269802234751` | — | 0 | 0 | NO | NO |
| `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `7345dbceca061abe156240c389ccde57508ec4009f4ccf90a06db8c20b6ea65b` | — | 0 | 0 | NO | NO |
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
| `NSI/gabarits/nexus-boites-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `2185848e26ea5152a1570828c1b5c29d5158dcf38b32702be680c617e9f90d36` | `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-charte-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `90391485645cb6fa03ae6ffc3b315d612e714b69dcc3c0efd547a7d8fca38137` | `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` | 3 | 0 | NO | NO |
| `NSI/gabarits/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `27a6bb961ea9fb00bb2046f987ab1f76aba832dd7f5def189bbf6d32bd07fcf5` | — | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-couverture.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `57327021b50fb44434874fb4fe00583ddb2160908ca8379d4d07d670f257685e` | `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-decor.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `1b23d537120ebd2437c9f6c59d5b99c24c4ecd1286028b4cc2441eabf0c758d4` | `Mathematiques/manuel-maths/gabarits/nexus-decor.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-exercices-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `25b72f131634021353e07500252a5cf69110faa106c670659240b796cd59edda` | `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures-bib.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `d441187e66d487806714abf7bba768aa61b20c6d18638b39f030e6c6ec190bfa` | `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures-nsi.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` | `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-figures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` | `Mathematiques/manuel-maths/gabarits/nexus-figures.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | `gabarits/common/nexus-icons.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-manuel-v5.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `5e1d7fdb258865321ee93a34a41a2de806edd93ad36b256829ed1bce4043a7dc` | `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` | 2 | 0 | NO | NO |
| `NSI/gabarits/nexus-manuel.cls` | COMPATIBILITY_CLASS_WRAPPER | NO | `90ea5ae521bcf028fbc5fc240639636c24eb2e1cfc934e0af9a2c94ae7269e07` | `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` | 5 | 0 | NO | NO |
| `NSI/gabarits/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `6ffc96378d2dece2dd7479647b7b7046025fe3c12a1bdd0fcf41d8787e277823` | `gabarits/common/nexus-margin-rail.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-pages-froides.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `4ecc02468ab1ab2859d7fe1f1930538ec35a9058dbfab79a1e86269802234751` | `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-pont-v6.sty` | COMPATIBILITY_STYLE_WRAPPER | NO | `7345dbceca061abe156240c389ccde57508ec4009f4ccf90a06db8c20b6ea65b` | `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty` | 0 | 0 | NO | NO |
| `NSI/gabarits/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | NO | `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` | `gabarits/common/nexus-signatures.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/objet_standalone.tex` | OBJECT_RUNTIME_TEMPLATE | NO | `c9c4c06915ff0cc38ea7393621547a39856705a8d0f19527bb89f3ecd300c769` | `Mathematiques/manuel-maths/gabarits/objet_standalone.tex` | 0 | 0 | NO | NO |
| `NSI/gabarits/specimen.tex` | VISUAL_SPECIMEN_TEMPLATE | NO | `a3dccdf4ceb7d315f02242303135b9e229701d4718ff29a5baab6365f23a2397` | — | 0 | 0 | NO | NO |
| `gabarits/common/chapitre_master.tex` | CHAPTER_RUNTIME_TEMPLATE | YES | `82c0ae2dfd98858c817f30193c7cee6f1f08327fb98f1090c6127902575028c3` | — | 0 | 0 | NO | NO |
| `gabarits/common/nexus-boites.sty` | CANONICAL_SUPPORT_STYLE | YES | `9cdecfd826561817a540d95e4eab38bacfc253a8a932956f58e533d83510d2ec` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-charte.sty` | CANONICAL_STYLE_IMPLEMENTATION | YES | `75132957ede070ffa00839547d12bc4289b4aca5888dfd7e98d78c356e4b9b9a` | — | 23 | 0 | NO | NO |
| `gabarits/common/nexus-code.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` | — | 1 | 0 | NO | NO |
| `gabarits/common/nexus-couverture.sty` | CANONICAL_SUPPORT_STYLE | YES | `cc687eeeb93df549adc3b08003cea5432aae19e6bd15cecefa07d681b3f915a1` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-decor.sty` | CANONICAL_SUPPORT_STYLE | YES | `bde5267321f2c8b034d06b3913d6589ccb0b96e78091466028b42a6b1a289942` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-exercices.sty` | CANONICAL_SUPPORT_STYLE | YES | `abae58775dc52a29b98a28add1cf6c55404222fc2990b119547f8863358571b7` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-figures-bib.sty` | CANONICAL_SUPPORT_STYLE | YES | `e8fede638c9bd372213cd7ede0d76279106f7a0cc1c9f5f180a01afb197ac4ff` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-icons.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` | — | 1 | 0 | NO | NO |
| `gabarits/common/nexus-manuel.cls` | CANONICAL_CLASS_IMPLEMENTATION | YES | `9a85c337ec1723bb33e90f71eb5b7c35c0954c63cc69b8fbdce77ac2bcea8c56` | — | 21 | 1 | NO | NO |
| `gabarits/common/nexus-margin-rail.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `6ffc96378d2dece2dd7479647b7b7046025fe3c12a1bdd0fcf41d8787e277823` | — | 0 | 0 | NO | NO |
| `gabarits/common/nexus-pages-froides.sty` | CANONICAL_SUPPORT_STYLE | YES | `4e1f7fae36ffa3b871bbe728ec9c7fcbf4b473c9f614660edb6cb057f8282bd8` | — | 13 | 0 | NO | NO |
| `gabarits/common/nexus-pont.sty` | CANONICAL_SUPPORT_STYLE | YES | `2703ad66ef9733c7c45f2176a7c13918a34920f6d4112e70f300d33e8f09d088` | — | 14 | 0 | NO | NO |
| `gabarits/common/nexus-signatures.tex` | RUNTIME_SUPPORT_TEMPLATE | YES | `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` | — | 1 | 0 | NO | NO |
| `gabarits/maths/nexus-maths.sty` | CANONICAL_DISCIPLINE_ADAPTER | YES | `c51c5b6a6fc330ccf47c0980716719f37073317b91f7233d8cc01f5fe1bed994` | — | 2 | 0 | NO | NO |
| `gabarits/nsi/nexus-nsi.sty` | CANONICAL_DISCIPLINE_ADAPTER | YES | `ddb6942951050b49582fbebb4668330fb7994e5cc08569e2451b4e39785ebd08` | — | 2 | 0 | NO | NO |

## Duplicatas exacts

- `16e74594ae5108e3326b36f92f75ccdb5b30472dc15134ffe5ff943a2a6b6d91` : `gabarits/common/nexus-code.tex`, `Mathematiques/manuel-maths/gabarits/nexus-code.tex`
- `1b23d537120ebd2437c9f6c59d5b99c24c4ecd1286028b4cc2441eabf0c758d4` : `Mathematiques/manuel-maths/gabarits/nexus-decor.sty`, `NSI/gabarits/nexus-decor.sty`
- `2185848e26ea5152a1570828c1b5c29d5158dcf38b32702be680c617e9f90d36` : `Mathematiques/manuel-maths/gabarits/nexus-boites-v6.sty`, `NSI/gabarits/nexus-boites-v6.sty`
- `25b72f131634021353e07500252a5cf69110faa106c670659240b796cd59edda` : `Mathematiques/manuel-maths/gabarits/nexus-exercices-v6.sty`, `NSI/gabarits/nexus-exercices-v6.sty`
- `2c7b764764e3db723f752e68e7af5d375171a0f9774f39f749b2598b8a1e931f` : `Mathematiques/manuel-maths/gabarits/nexus-figures-nsi.tex`, `NSI/gabarits/nexus-figures-nsi.tex`
- `42af1195dda223dc642255754ff7a94f1d5add6720e7062883de4c429132cc8b` : `gabarits/common/nexus-icons.tex`, `Mathematiques/manuel-maths/gabarits/nexus-icons.tex`, `NSI/gabarits/nexus-icons.tex`
- `4ecc02468ab1ab2859d7fe1f1930538ec35a9058dbfab79a1e86269802234751` : `Mathematiques/manuel-maths/gabarits/nexus-pages-froides.sty`, `NSI/gabarits/nexus-pages-froides.sty`
- `57327021b50fb44434874fb4fe00583ddb2160908ca8379d4d07d670f257685e` : `Mathematiques/manuel-maths/gabarits/nexus-couverture.sty`, `NSI/gabarits/nexus-couverture.sty`
- `5e1d7fdb258865321ee93a34a41a2de806edd93ad36b256829ed1bce4043a7dc` : `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls`, `NSI/gabarits/nexus-manuel-v5.cls`
- `6ffc96378d2dece2dd7479647b7b7046025fe3c12a1bdd0fcf41d8787e277823` : `gabarits/common/nexus-margin-rail.tex`, `Mathematiques/manuel-maths/gabarits/nexus-margin-rail.tex`, `NSI/gabarits/nexus-margin-rail.tex`
- `7345dbceca061abe156240c389ccde57508ec4009f4ccf90a06db8c20b6ea65b` : `Mathematiques/manuel-maths/gabarits/nexus-pont-v6.sty`, `NSI/gabarits/nexus-pont-v6.sty`
- `82c0ae2dfd98858c817f30193c7cee6f1f08327fb98f1090c6127902575028c3` : `gabarits/common/chapitre_master.tex`, `Mathematiques/manuel-maths/gabarits/chapitre_master.tex`
- `90391485645cb6fa03ae6ffc3b315d612e714b69dcc3c0efd547a7d8fca38137` : `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty`, `NSI/gabarits/nexus-charte-v6.sty`
- `90ea5ae521bcf028fbc5fc240639636c24eb2e1cfc934e0af9a2c94ae7269e07` : `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls`, `NSI/gabarits/nexus-manuel.cls`
- `bbf81c1368d7be1b067597803e1429dd94e19c0585dbf0981d408f8f5ea3cc74` : `gabarits/common/nexus-signatures.tex`, `Mathematiques/manuel-maths/gabarits/nexus-signatures.tex`, `NSI/gabarits/nexus-signatures.tex`
- `c9c4c06915ff0cc38ea7393621547a39856705a8d0f19527bb89f3ecd300c769` : `Mathematiques/manuel-maths/gabarits/objet_standalone.tex`, `NSI/gabarits/objet_standalone.tex`
- `d441187e66d487806714abf7bba768aa61b20c6d18638b39f030e6c6ec190bfa` : `Mathematiques/manuel-maths/gabarits/nexus-figures-bib.sty`, `NSI/gabarits/nexus-figures-bib.sty`
- `de13399037827ab8300953a7f5a46bd9e34d5a634b9d17fe8a128066007a831a` : `Mathematiques/manuel-maths/gabarits/nexus-figures.tex`, `NSI/gabarits/nexus-figures.tex`
