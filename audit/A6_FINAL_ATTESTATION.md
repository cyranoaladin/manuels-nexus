# A6 — attestation finale au SHA source exact

`A6_SOURCE_SHA = 4693849a0df31aaeb9da168c4f874cb2ba7c6774`

Verdict du lot technique borné PRE-A6/A6 : **A6 = PASS**. Les deux clones
Fresh A et Fresh B, créés de zéro au SHA ci-dessus, reproduisent les mêmes
tests, inventaire, gates, masters, PDF, nombres de pages, textes extraits,
trailer IDs et graphes de sources canoniques.

Ce verdict ne vaut pas approbation éditoriale ni publication :
`MACHINE_PUBLISH_READY=NO`, `HUMAN_ACCEPTED=NO`,
`HUMAN_VALIDATED=NO`, `FINAL_RELEASE_AUTHORIZED=NO`. La publication reste
**NO-GO**, `release-strict` reste rouge et D7 reste **BLOCKED**.

Les présents fichiers sont une preuve portant sur `A6_SOURCE_SHA`; ils ne
font pas partie de la préimage PDF. Aucun résultat d'un lot ultérieur n'est
préinscrit.

Les preuves normalisées et les payloads observés durables sont archivés dans
`audit/A6_FINAL_EVIDENCE_BUNDLE.json`, schéma
`nexus-a6-final-evidence-bundle/v1`,
`evidence_bundle_sha256 =`
`601deda6e5ef95d8903bc57c86e1dcc439beb6823496a358db3cc6721311e9d6`.
Ce bundle n'est ni une entrée PDF/modèle, ni une approbation humaine ; les
résumés de tests qu'il contient sont explicitement normalisés et ne sont pas
présentés comme des stdout bruts.

## PRE-A6 : validation du modèle

`--validate-model` passe de **rc 6 / 9 failures** à **rc 0 / 0 failure**.
Les neuf cas sont tous `ID_MIGRATION_FINGERPRINT_DRIFT`, par une bijection
mécanique exacte documentée dans
`PRE_A6_VALIDATE_MODEL_FORENSICS.{json,md}`. Aucun cas ne requiert une nouvelle
décision humaine. La baseline, les dispositions, les politiques et les
statuts métier restent inchangés : aucune valeur de statut modifiée et aucune
promotion, soit **0/0**.

La sémantique A0/A5 de `correction` est fermée dans
`A5_CORRECTION_TYPE_SEMANTICS.md` : A0 et A5 lisent le même champ brut
`% META.type_objet`, avec deux responsabilités compatibles. Le `source_role`
est orthogonal. Conflit : **NO**.

## A6 : fermeture des contextes

Les trois cas étaient tous `PATH_CONTEXT_DRIFT`. Les fichiers placés sous
TCOMPL étaient des copies redondantes de sources canoniques TSPE, identiques
hors `META.id`. La correction supprime uniquement ces trois copies et conserve
les jumeaux TSPE.

- `context_mismatches` : **3 → 0** ;
- fingerprints retirés : `412440a833f2a67e`, `d4d96a91fdd7f2ca`,
  `dc3c58388e2cfe7c` ;
- ajoutés : 0 ; reclassifiés : 0 ; communs modifiés : 0 ; `UNKNOWN=0`.

Les trois retraits sont des suppressions de sources redondantes, pas des
mutations de statut. Valeurs de statut modifiées : **0** ; promotions : **0**.

La seule raison release retirée dans le lot est
`TCOMPL:anomalie:context_mismatches:anomalies.context_mismatches:3`.

## P0 de reproductibilité découverts et résolus

Trois défauts réels ont été traités sans les masquer :

1. Le candidat `bcac52aa9d0f5385b470410320b082ae6f3bd321` produisait, pour le
   même chapitre sous deux racines absolues, deux `/ID` et deux PDF différents
   alors que pages, texte et QDF neutralisé pour `/ID` étaient identiques. Le
   producteur chapitre réutilise désormais le contrat commun d'identité
   déterministe. `A6_CHAPTER_PDF_PATH_REPRODUCIBILITY.md` conserve le rouge et
   la cause racine ; le vert final est le replay Fresh A/B au SHA exact décrit
   plus bas. Correctif initial : `feab46bc`.
2. Les producteurs de manuels sérialisaient le `run_id` d'exécution dans le
   master canonique. Le correctif `f95631dd` remplace cette donnée variable par
   un hook LuaTeX constant et injecte le token uniquement dans l'environnement
   des trois compilations.
3. La première compilation réelle inter-clones TCOMPL conservée comme preuve
   a révélé un second P0 : l'opérateur Lua `~=` était altéré par le caractère
   `~` actif de TeX. Le même hook défectueux était présent dans les sources des
   producteurs Math et NSI ; cette attestation ne prétend pas conserver un
   échec observé 1NSI. Le candidat `f95631dd` est disqualifié. Le correctif
   TeX-safe `7622a2e0` supprime cet opérateur ; les builds réels ont ensuite
   été rejoués avec succès.

Le contrat autoritaire est `PDF_TRAILER_ID_PREIMAGE_CONTRACT.md`. Le `run_id`,
les chemins absolus, le cwd, l'horloge murale, Git HEAD ajouté artificiellement,
les sorties générées, l'ancien PDF, l'ancien trailer et les rapports dérivés
sont exclus de la préimage.

## Inventaire, dette de revue et autorités

L'inventaire final donne RAW/fingerprints bloquants/non bloquants =
**2308/2308/0**. Le compteur de catégorie `blocking_statuses` reste
**2222→2222**.

Catégories actives :

- `blocking_statuses=2222` ;
- `unassembled_objects=52` ;
- `unattributed_pdfs=22` ;
- `orphan_files=12`.

Toutes les autres catégories structurelles sont nulles :
`context_mismatches`, `unclassified_types`, broken meta, broken LaTeX,
cycles et duplicates. Le compteur P0 du **modèle d'inventaire** vaut 0,
`NEW_UNQUALIFIED=0` et `EXPECTED_REVIEW_DEBT=89`. Ce compteur ne constitue pas
une déclaration « zéro P0 scientifique ou éditorial » à l'échelle du projet.

Digests :

- source :
  `sha256:1b387135b51d85a8237269b1e087abd73a277874d072ff5b181cd6067d53ce43` ;
- modèle :
  `sha256:5d0ace406cc08ff570d38538e0936fae7a482cac8cc2ace4712c5b265d55b90d` ;
- fingerprints :
  `sha256:fb0a1c4571e71b0c87aeae59394d0c0103b2ef946feab15fd0c291821c4444a8`.

Les 89 sources de méthodes et 89 packets ont été relus : SHA source du
record, `packet.source_sha256`, SHA courant de la source et SHA courant du
packet concordent ; les deux statuts restent `needs_review`; stale = **0**.
Digest de liaison :
`sha256:6c41df0deb2007518810bd030df552a4fe38a1265028f099e852cd75cfd7483a`.

Autorités inchangées :

- baseline : `3e9225668121a67c2fdea1248ec420ff16bd3910c8557e3a98df8bb7997250e1` ;
- dispositions : `49595a0f28745eee0b8f080a4cbeb2fa7265a798455f2747a93d9d532635cda6` ;
- policy baseline : `07d95c5073da77944ab07a3312483fdfda0f43d6f412ee023f3269c770b282d2` ;
- policy humaine A4 : `07597ede77c7fce1a167a87227178f05a10faabbad4ca1e04d7bb2048fda12a7`.

## Tests et gates — Fresh A = Fresh B

- root : **1200 passed**, 0 failed/skip/xfail ;
- Math : **4745 passed**, 0 failed/skip/xfail, 4 warnings de dépendances
  connus (`pandas`/`numexpr`, `pandas`/`bottleneck`, `SwigPyPacked`,
  `SwigPyObject`) ;
- NSI : **2199 passed**, 0 failed/skip/xfail ;
- context-mismatch ciblé : 7 ; PRE-A6/validate-model : 43 ; A5 ontologie : 9 ;
  régressions A1–A4 : 28 ;
- `--check --require-clean` : rc 0 ;
- `--validate-model` : rc 0 ;
- `--fail-on-new` : rc 0 ;
- `--release-strict` : **rc 7**, **65 raisons**, digest
  `sha256:3a7f4a78458be6f57b92581e6ca742a208b64867131aba60dae34b927cedb2ba`.

Les résultats A et B sont identiques. `release-strict` est rouge pour la
dette de publication réelle, pas pour une régression A6.

### Preuve TDD/protocole exécutée pendant le correctif

Après le hotfix TeX-safe, le run combiné du protocole manuel donne **483
passed**, décomposé en 11 tests d'autorité d'identité PDF, 299 tests du
manifeste, 99 tests Math observés (98 antérieurs + 1 régression de production
réelle) et 74 tests NSI observés. `11+299+99+74=483` : ces comptes décomposent
ce run et ne s'ajoutent pas aux totaux des suites complètes.

Le producteur chapitre a en outre passé 42 tests moteur/sécurité, 1 test de
production réelle observée et les 11 tests d'autorité PDF. Ces ensembles sont
non additifs : l'autorité PDF recoupe le composant correspondant du run de 483.
Les suites complètes finales Fresh A/B contiennent les tests de régression ;
ces comptes ciblés consignent le rouge-vert réalisé pendant le correctif.

Les dix cas imposés sont verts :

1. mêmes chapitre/sources, racines absolues différentes → PDF byte-identiques ;
2. mêmes entrées, `run_id` différents → sorties identiques ;
3. mêmes entrées, heures murales différentes → sorties identiques ;
4. un octet pertinent de source modifié → trailer ID et SHA PDF changent ;
5. source restaurée → trailer ID et SHA PDF initiaux restaurés ;
6. élève → professeur → identités déterministes et distinctes lorsque variante
   ou contenu diffère ;
7. chapitre différent → identité déterministe différente ;
8. version de schéma producteur différente → identité différente ;
9. ancien PDF suivi remplacé → préimage source inchangée ;
10. même graphe source dans deux worktrees Git → sortie byte-identique.

## Clones frais et isolement

- Fresh A : `/tmp/nexus-a6-fresh-a.gGBrnV/repo` ;
- Fresh B : `/tmp/nexus-a6-final-b.xhnieA/repo`.

Les deux clones ont été créés par `git clone --no-hardlinks`, sur la branche
attachée `audit/adversarial-reconciliation-2026`, au SHA exact, propres au
début et à la fin. Aucun alternates, inode d'objet ou inode de worktree partagé
n'a été trouvé. Writers, staging/backups et locks actifs finaux : **0**.

Chaque build observé a été exécuté dans son propre clone mono-run indépendant.
Le clone n'a jamais été réutilisé après l'écriture attendue de
`audit/BUILD_MANIFEST.json`.

## Toolchain observée

Fresh A et Fresh B utilisent exactement :

- LuaHBTeX 1.17.0, TeX Live 2023/Debian, development id 7581 ;
- `pdfinfo` 24.02.0 ;
- `pdffonts` 24.02.0 ;
- Python 3.12.3.

## Replay final du producteur chapitre

Au SHA source final, Fresh A et Fresh B retournent rc 0 et les valeurs A/B
sont identiques :

| Variante | Master SHA-256 | PDF SHA-256 | Pages | Texte | Trailer `/ID` |
|---|---|---|---:|---|---|
| `complet` | `88a700757a6604bb2046d53aa477a1ff5f388343b302d133694e7bdad9688a81` | `55efb058b67cd3a2c13dfd90df6333acadf2d78caeb2155a8bbb124f7ef2367b` | 18 | `413bc17e0fb76d144fa5266eb81d1ce47960146176d273b33df6416b76bdfc3c` | `ECB619DF9F61EDA9493EF4428CD8EC8F` |
| `parcours1` | `7b347427aa0b3646b15680bf3e4bd0c03b12a8c3fd80860f041d2b9a5e4f82e3` | `d6b967bd4af211a3bdd6b0c25638f342f52e64f1bb6939b94ec3f7a093345d4f` | 17 | `6c7b6660dbf72192054501e949284173caf7f79533a834a2491cd3116a664e8b` | `7B9618C13706473D3A7015D1E3CC0D91` |

Le diagnostic `A6_CHAPTER_PDF_PATH_REPRODUCIBILITY.md` reste l'autorité du
rouge et de la cause racine, pas la preuve du vert ci-dessus.

## Builds sans enregistrement

Les valeurs suivantes sont identiques dans Fresh A et Fresh B :

| Cible | Master canonique | PDF SHA-256 | Pages | Texte | Trailer `/ID` |
|---|---|---|---:|---|---|
| TCOMPL élève, 2 runs/racine | `667ff1dc87980b02dfd7754f126626878427b3d12fa62edbbb7c0f3c0b35e31d` | `6212a21b273605d416a35337b7f26c10ca78289c02b465d7b13924e32f9abd0f` | 162 | `58f2f61a6da11cf575b4cfec81aaf2155703032cc853245f845a331414c23ced` | `0249C7CF59CA498830C7871B589F7F54` |
| TCOMPL professeur, 2 runs/racine | `13d78c6a6eb8be46ea614721f8000ab1a28a7a8680d5b5e9caa7190b75b673bd` | `d14ec54cdd5641ce13739316f2ec5b3e92d11039aa1b43bab9b2a3b822bb4a3b` | 226 | `97334889a2e1282a8934e33de196acc5144045eda084805fa1a5bfc51de7492e` | `E9D13F3293CD20F6A23A80B6A8C13242` |
| 1NSI élève | `1352f2558b08d25e3ea32d63f0443d772457d9ad8391785872847bd4ed35574f` | `7396cc0051fe488d3dad1f00537d919bbdac13eb839770784acace3edea24d39` | 235 | `f6e656f2e5839b53d9a2fe4c7cd2452a0bff926e8de0f3ce133302a53b0467fd` | `5280F069D2BC34CDDC3E17795762613E` |
| 1NSI professeur | `1ef4c1264a782ae49138fe660d0aaf59fa0ed6d3f714b7621402e31698d9dc44` | `d91512273ee8753e3590bc236267ddc12e4b1310610f4f5bdb8ffacc9ac9bc31` | 378 | `8df655280e1928037a5ef3da1d18b0a36c69f05a1874d21c34397b12ef570ff7` | `9F5B1E31E3F5A55E9922669A83975561` |

Les deux hashes NSI de cette table sont les masters locaux du mode sans
enregistrement. Les masters de preuve observée, enrichis par le traçage des
objets, sont distingués ci-dessous ; les PDF restent identiques.

## Builds observés et chaîne receipt

Pour les huit runs (quatre cibles × deux côtés), le validator commun passe.
Chaque master porte exactement une occurrence du hook constant et aucun token
de run concret. Le log porte exactement le marqueur du receipt, le préflight
porte le même token, le `.fls` prouve la lecture du master exact, et receipt et
préflight passent. Les huit `run_id` sont distincts.

| Cible | `run_id` Fresh A | `run_id` Fresh B | Master observé |
|---|---|---|---|
| TCOMPL élève | `33820612f92748acc72d321cfbe3962b` | `70f006537d61f375b00bb25e5d1f74dd` | `667ff1dc87980b02dfd7754f126626878427b3d12fa62edbbb7c0f3c0b35e31d` |
| TCOMPL professeur | `7ac5409eb1331fe0041a887676e1a8f9` | `3dfd78ae0f87ed3e4dc5764211744972` | `13d78c6a6eb8be46ea614721f8000ab1a28a7a8680d5b5e9caa7190b75b673bd` |
| 1NSI élève | `23ceb83dd9269a7581113c1476f9dce2` | `7ce247935638ed13e0a427893a2eeaa3` | `06bb02bab9799b14c09264e68f895a931ed0c0c088349fb73453ef5eaa395e9a` |
| 1NSI professeur | `853c1d35069106254ce016f6e229007f` | `a867bd04b8b927c69601d985bf7fbe30` | `153c42f0690768aaf2e2f73317666b061bc7f795ac68a7ed651a6eaa53b2de4d` |

## Graphe source canonique

La comparaison ne prétend pas que les `.fls` bruts sont égaux : ils portent
des chemins absolus différents. La forme comparée est une map canonique
`chemin repo-relatif POSIX -> sha256:<hex>` obtenue depuis les `INPUT` du `.fls`
résolus relativement à son `PWD`, limitée aux fichiers internes suivis par Git,
puis unie aux autorités déclarées du producteur. La sérialisation est un JSON
compact, `ensure_ascii=False`, clés triées. Pour NSI,
`NSI/gabarits/book_master.tex`, rendu par le producteur mais non lu comme
`\input`, est ajouté comme autorité déclarée.

| Cible | Entrées | Digest A = B |
|---|---:|---|
| TCOMPL élève | 485 | `sha256:4517f081b7c6ab89e42c8c41e7ef3c0c4ca4eef37b121b9135d49aea1b50c119` |
| TCOMPL professeur | 803 | `sha256:fcef192324e7121675c2a2ccc25e06c796f5d75c38afbbeb20fc915deafe5181` |
| 1NSI élève | 509 | `sha256:50507b859308785502de8f6d31301d2e768072d94cc101db2d3ee79183d7beee` |
| 1NSI professeur | 964 | `sha256:e1ade64b313025a7a0cbf85270f5d6257f5fcc9f95e5c7d0923c6681d5a1108d` |

Les chemins et hashes de rendu sont distingués sans employer « wrapper » comme
étiquette générique :

- classes locales des manuels
  `Mathematiques/manuel-maths/gabarits/nexus-manuel-v5.cls` et
  `NSI/gabarits/nexus-manuel-v5.cls` :
  `5e1d7fdb258865321ee93a34a41a2de806edd93ad36b256829ed1bce4043a7dc` ;
- wrappers locaux de classe chapitre
  `Mathematiques/manuel-maths/gabarits/nexus-manuel.cls` et
  `NSI/gabarits/nexus-manuel.cls` :
  `90ea5ae521bcf028fbc5fc240639636c24eb2e1cfc934e0af9a2c94ae7269e07` ;
- chartes locales des manuels
  `Mathematiques/manuel-maths/gabarits/nexus-charte-v6.sty` et
  `NSI/gabarits/nexus-charte-v6.sty` :
  `90391485645cb6fa03ae6ffc3b315d612e714b69dcc3c0efd547a7d8fca38137` ;
- classe physique commune `gabarits/common/nexus-manuel.cls` :
  `9a85c337ec1723bb33e90f71eb5b7c35c0954c63cc69b8fbdce77ac2bcea8c56` ;
- charte physique commune `gabarits/common/nexus-charte.sty` :
  `75132957ede070ffa00839547d12bc4289b4aca5888dfd7e98d78c356e4b9b9a` ;
- pont physique commun `gabarits/common/nexus-pont.sty` :
  `2703ad66ef9733c7c45f2176a7c13918a34920f6d4112e70f300d33e8f09d088`.

Les paires Math/NSI ont des bytes identiques. Ces hashes décrivent les entrées
A6 ; ils ne déclarent pas achevée la future migration des wrappers de
compatibilité.

## PDF suivis et limites du verdict

Les **36/36** PDF suivis sont inchangés pathwise dans chaque clone frais par
rapport à `A6_SOURCE_SHA`, et les ensembles A/B sont identiques. Le digest
canonique est
`sha256:bf5dff700b331432d5e82322f1aefe6bf33ac87ea06fd3332247d83ec7a35be1`,
calculé comme le SHA-256 de la concaténation UTF-8, triée par chemin,
`<pdf_sha256>  <chemin repo-relatif>\n`. Le digest ad hoc `bf5a8741…` n'est pas
utilisé : il correspond à une autre préimage de rapport JSON.

Entre le SHA de départ A5 et le candidat final, 34 PDF restent inchangés et
les deux changements TCOMPL sont les sorties attendues de la suppression des
copies : élève 164→162 pages, professeur 229→226 pages. Aucun oracle visuel ni
baseline n'a été créé ou mis à jour.

## Gouvernance et suite

Aucun push, merge, baseline update, changement/promotion de statut,
qualification ou signature humaine n'a été créé. Le lot suivant est T1,
fermeture des dettes structurelles
(`unattributed_pdfs`, `orphan_files`, `unassembled_objects`), mais aucune de ses
conclusions futures n'est attestée ici.

**Conclusion bornée : A6 PASS. Publication NO-GO. D7 BLOCKED.**
