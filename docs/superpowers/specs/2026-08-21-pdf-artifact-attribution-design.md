# Attribution des artefacts PDF suivis — design T1.2

## Contexte et état d'entrée

Au SHA `4d6621ca2aeb76e9fe856804106d2bbb19b4f3f4`, l'inventaire suit
36 PDF et expose exactement 22 anomalies `unattributed_pdfs`. La dette brute
est :

```text
RAW                  2308
blocking_statuses    2222
unassembled_objects    52
unattributed_pdfs      22
orphan_files            12
autres catégories        0
```

`release-strict` retourne `7` avec 67 raisons, dont :

```text
COLLECTION:anomalie:unattributed_pdfs:anomalies.unattributed_pdfs:22
```

Le lot précédent a établi que toute anomalie bloquante sans manuel doit être
projetée à la portée `COLLECTION`. T1.2 ne revient pas sur cette règle. Il
remplace seulement l'absence réelle d'attribution de ces 22 PDF par un
contrôle versionné, exact et vérifiable.

Le fichier `audit/UNATTRIBUTED_PDFS_LEDGER.md` n'est pas une autorité valide :
il affirme à tort que les 22 PDF sont des fixtures situées sous
`tests/fixtures/` ou `audit/fixtures/`. Aucun des 22 chemins ne satisfait cette
description.

## Objectif

Créer une attribution explicite pour les 22 PDF sans :

- les faire passer pour des builds canoniques ;
- inventer un producteur ou une provenance ;
- ajouter une allowlist ou une inférence par basename ;
- créer une anomalie de remplacement ou une qualification de baseline ;
- décider humainement du sort des 12 instantanés de publication ;
- modifier `audit/SOURCE_ROLES.yaml` ou `audit/BUILD_PRODUCERS.yaml`.

La sortie attendue est `unattributed_pdfs=0`. Les 12 instantanés historiques
restent une dette release réelle, agrégée en une unique raison stable :

```text
COLLECTION:publication_snapshots:stale_undecided:12
```

Cette fermeture technique ne vaut ni décision de conservation, ni promotion
des instantanés, ni preuve de publication.

## Classification autoritaire

Le registre emploie exactement trois rôles. Aucun rôle `UNKNOWN`, `FIXTURE`,
`generated` ou assimilé n'est autorisé.

### `HISTORICAL_PUBLICATION_SNAPSHOT`

Les 12 fichiers de `MANUELS_PDF_PUBLICATION/` ont été introduits ensemble au
commit :

```text
e630c5adcff0a8993bbf565edfb98b7820038ab3
```

Les 12 blobs sont encore exactement ceux de ce commit et ne sont pas régénérés
par les producteurs déclarés. Le registre ne leur attribue donc aucun
producteur. Leur provenance relie au commit `e630c5ad...` le chemin snapshot
et son chemin d'origine canonique.

À ce commit, `path` et `canonical_origin_path` existent tous deux comme blobs
et ont exactement le même OID. Le loader attribue
`canonical_origin_path` par `attribute_pdf()` et exige que le manuel et la
variante dérivés soient ceux du record. Cette preuve historique ne fait pas de
l'instantané un build observé actuel.

Leur état release est obligatoirement `STALE_UNDECIDED`. Une égalité ou une
différence future avec le PDF canonique ne ferme jamais automatiquement cet
état ni son blocker. Une autre valeur exige une décision humaine et une
évolution explicite du contrat.

### `OFFICIAL_PROGRAM_AUTHORITY`

Deux PDF sous `NSI/corpus_nsi/00_programmes_officiels/` sont les copies
locales officielles enregistrées pour les programmes NSI :

- Première → manuel `1NSI`, code `MENE1901633A`, autorité collection
  `SRC-BO2019-NSI-PREMIERE`, page officielle
  `https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm` et annexe
  `https://cache.media.education.gouv.fr/file/SP1-MEN-22-1-2019/26/8/spe633_annexe_1063268.pdf` ;
- Terminale → manuel `TNSI`, code `MENE1921247A`, autorité collection
  `SRC-BO2019-NSI-TERMINALE`, page officielle
  `https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm` et annexe
  `https://cache.media.education.gouv.fr/file/SPE8_MENJ_25_7_2019/93/3/spe247_annexe_1158933.pdf`.

Le loader vérifie le code, le SHA-256 déclaré par l'autorité collection et les
URL exactes sur des domaines officiels. Ce rôle établit la provenance et
l'authenticité de la copie locale. Il ne décide ni l'applicabilité à l'édition
2026-2027, ni la couverture du manuel : ces conclusions restent réservées à
l'audit réglementaire T2.

### `HARVEST_NON_PUBLISHABLE_HISTORICAL_RENDER`

Huit PDF sous `NSI/corpus_nsi/latex/packs/premiere/P13/` sont des rendus
historiques d'un pack de harvest. Ils sont hors du graphe de release et ne
sont ni des fixtures ni des builds manuels observés.

Leur provenance est exactement
`REPOSITORY_HISTORY_WITHOUT_BUILD_RECEIPT` : le PDF et un `build.sh` déclaré
existent au commit d'import
`10a15746bdbb043c44d461eac40fa4041d23988e`. Cette coexistence ne prouve pas
que le script a produit le PDF. Ni une source `.tex`, ni un préambule, ni le
script déclaré ne sont utilisés comme preuve du graphe de production.
`build_observed` et `compilation_evidence` restent toujours `false`.

Les dix sources `.tex` du pack P13 contiennent actuellement `siheader{...}` au
lieu de `\nsiheader{...}`. Cette faute est corrigée dans un lot TDD séparé.
Cette correction ne renomme ni ne régénère les huit PDF suivis. Les deux
sources élève sans PDF suivi sont corrigées elles aussi.

L'attribution technique n'épuise pas le cycle de vie P13. La décision humaine
ultérieure — conserver ces rendus historiques, les archiver hors dépôt ou les
supprimer avec preuve d'absence de contenu unique — est tracée séparément et
n'empêche pas `unattributed_pdfs=0`.

## Registre versionné

### Fichiers

```text
audit/PDF_ARTIFACT_REGISTRY.yaml
audit/schemas/v1/pdf-artifact-registry.schema.json
```

Le type est enregistré dans `SCHEMA_REGISTRY` :

```python
"pdf_artifact_registry": {
    1: "audit/schemas/v1/pdf-artifact-registry.schema.json",
}
```

Le schéma JSON Draft 2020-12 est fermé : `additionalProperties: false` au
niveau racine, dans chaque record et dans chaque objet de provenance.

### Enveloppe

```yaml
artifact_type: pdf_artifact_registry
schema_version: 1
schema_ref: audit/schemas/v1/pdf-artifact-registry.schema.json
control_digest: sha256:<64 hex>
records: []
```

`control_digest` est calculé par `_control_digest()` sur le JSON canonique de
l'enveloppe privée de `control_digest`. Il n'est jamais saisi ou ajusté à la
main.

La version 1 contient exactement 22 records, triés par `path`, sans doublon :

- 12 `HISTORICAL_PUBLICATION_SNAPSHOT` ;
- 2 `OFFICIAL_PROGRAM_AUTHORITY` ;
- 8 `HARVEST_NON_PUBLISHABLE_HISTORICAL_RENDER`.

### Champs communs

Chaque record exige :

```yaml
path: chemin/relatif.pdf
role: HISTORICAL_PUBLICATION_SNAPSHOT
manual: 1SPE
chapter: null
variant: eleve
scope: publication_snapshot
tracking: TRACKED
source_role: transversal
pdf_sha256: sha256:<64 hex>
page_count: 1
compilation_evidence: false
release_state: STALE_UNDECIDED
provenance: {}
```

Règles communes :

- `path` est un chemin POSIX relatif canonique, suivi par Git, suffixé `.pdf` ;
- `manual` est l'un des six identifiants canoniques ;
- `chapter` vaut `null` pour les snapshots et les autorités, et vaut exactement
  `1NSI-ALGO-DICHO-GLOUTON-KNN` pour les rendus P13 ;
- `variant` vaut `eleve`, `professeur` ou `null` ; `null` signifie « non
  applicable », jamais « inconnu » ;
- `source_role` vaut exactement `transversal`, conformément à
  `SOURCE_ROLES.yaml` ;
- `tracking` vaut exactement `TRACKED` ;
- `page_count` est un entier strictement positif, jamais un booléen ;
- `compilation_evidence` vaut exactement `false` ;
- le hash et la pagination sont mesurés sur le même snapshot PDF privé et
  épinglé par `inspect_stable_pdf()`.

### Provenance des instantanés de publication

```yaml
provenance:
  kind: GIT_PUBLICATION_SNAPSHOT
  commit: e630c5adcff0a8993bbf565edfb98b7820038ab3
  blob_oid: <40 hex>
  canonical_origin_path: <chemin canonique exact dans la matrice ci-dessous>
  canonical_origin_blob_oid: <même OID que blob_oid>
```

Le schéma impose `release_state: STALE_UNDECIDED`, `scope:
publication_snapshot`, `chapter: null` et une variante non nulle. Au commit
déclaré, il exige les deux chemins, leurs objets blob et l'égalité stricte
`blob_oid == canonical_origin_blob_oid`. Le manuel et la variante issus de
l'attribution canonique de l'origine doivent égaler le record.

### Provenance des autorités officielles

```yaml
provenance:
  kind: OFFICIAL_PROGRAM_RECORD
  authority_path: docs/programmes/PROGRAMMES_2026_2027.yaml
  authority_key: sources.SRC-BO2019-NSI-PREMIERE
  authority_code: MENE1901633A
  landing_url: https://www.education.gouv.fr/bo/19/Special1/MENE1901633A.htm
  pdf_url: https://cache.media.education.gouv.fr/file/SP1-MEN-22-1-2019/26/8/spe633_annexe_1063268.pdf
```

Le schéma impose `chapter: null`, `variant: null`, `scope:
official_program_authority` et `release_state: REFERENCE_ONLY`. La clé
d'autorité doit déclarer le même SHA-256 que le PDF inspecté. Le registre ne
contient aucune conclusion d'applicabilité.

### Provenance des rendus P13

```yaml
provenance:
  kind: REPOSITORY_HISTORY_WITHOUT_BUILD_RECEIPT
  import_commit: 10a15746bdbb043c44d461eac40fa4041d23988e
  pdf_blob_oid: <40 hex>
  declared_recipe_path: NSI/corpus_nsi/latex/packs/premiere/P13/build.sh
  declared_recipe_blob_oid: 6389b402d46ed1824037fcdfe127847d10d333eb
  build_observed: false
```

Le schéma impose `manual: 1NSI`, `chapter:
1NSI-ALGO-DICHO-GLOUTON-KNN`, `variant: null`, `scope:
harvest_historical_render` et `release_state: NON_PUBLISHABLE`. Ici encore,
`variant: null` signifie seulement « non applicable comme variante de sortie
d'un build manuel » ; il ne décrit pas l'audience.

Le champ fermé `audience`, obligatoire uniquement pour ce rôle, vaut :

- `PROFESSOR_ONLY` pour `P13_corrige.pdf`, `P13_td.pdf` et `P13_tp.pdf` ;
- `STUDENT_FACING` pour `P13_aides.pdf`, `P13_cours.pdf`,
  `P13_evaluation.pdf`, `P13_fiche_methode.pdf` et `P13_trace.pdf`.

Le schéma interdit `audience` sur les snapshots et autorités officielles,
ainsi que toute autre valeur ou association chemin/audience.

### Activation obligatoire et inconditionnelle

Le registre et son schéma sont des contrôles permanents du build. Leurs chemins
sont référencés explicitement dans le code et le schéma dans
`SCHEMA_REGISTRY`; `_build_inventory()` les charge avant de parcourir les PDF.
Ils doivent toujours exister, être suivis et valides, même si aucun PDF n'est
présent sous les préfixes concernés.

La suppression simultanée du registre, du schéma et de tous les PDF qu'ils
décrivent échoue donc fermée. Aucun calcul de présence, registre vide ou
absence d'artefact ne peut désactiver le contrôle.

### Lecture stable des trois autorités de contrôle

Une session commune, construite par exemple par
`_read_stable_tracked_control()` et possédée par `_build_inventory()` jusqu'à
la fin des digests, lit séparément les trois surfaces d'autorité :

```text
audit/PDF_ARTIFACT_REGISTRY.yaml
audit/schemas/v1/pdf-artifact-registry.schema.json
docs/programmes/PROGRAMMES_2026_2027.yaml
```

Pour chacune, le helper :

1. exige le chemin canonique dans la liste Git suivie ;
2. ouvre la racine du dépôt, puis chaque parent par `dir_fd` avec
   `O_DIRECTORY | O_NOFOLLOW`, et ancre pour chaque descripteur device, inode,
   mode et nombre de liens ;
3. fait un `lstat` initial du leaf relativement au dernier parent, refuse
   symlink, type non régulier et `st_nlink != 1`, puis ouvre le leaf par
   `dir_fd` avec `O_NOFOLLOW` ;
4. compare `fstat` du leaf et `lstat`, puis lit les octets depuis le
   descripteur et calcule leur digest ;
5. conserve la session et tous les descripteurs parents/leaf ouverts jusqu'à
   la fin de la validation, du `model_digest` et du `source_digest` ;
6. fournit des overrides `(bytes, digest)` pour ces trois chemins à la fonction
   canonique `inventory_graph.source_digest()` ; le wrapper
   `_source_digest()` ne fait que déléguer et aucun des trois chemins n'est
   rouvert ;
7. revalide en fin de session tous les parents et le leaf par `fstat`, puis les
   noms par `lstat`/réouverture relative, et refuse toute variation de device,
   inode, mode, taille, mtime, ctime ou nombre de liens ;
8. parse et valide uniquement les octets ainsi épinglés, jamais une seconde
   lecture par chemin.

Les tests couvrent séparément, pour chacune des trois surfaces : symlink ou
hardlink du leaf, symlink/substitution d'un parent, remplacement concurrent
pendant la lecture, et remplacement après lecture mais avant
`_source_digest`. Chaque mutation doit échouer fermée et prouver que le digest
n'a jamais mélangé deux versions.

`inventory_graph.source_digest()` reste l'unique implémentation du préimage :
elle accepte un mapping optionnel d'overrides épinglés, mais conserve l'ordre,
l'encodage des chemins, les marqueurs et longueurs historiques. Un test de
non-régression fournit comme overrides les octets exacts présents sur disque et
exige le digest historique strictement identique.

## Loader et invariants fail-closed

`_load_pdf_artifact_registry(root, tracked, source_roles)` réutilise
`_validate_control_payload()` et `_clean_path()`. Le parsing YAML/JSON reçoit
les octets du helper stable ; il ne rappelle pas un loader qui rouvrirait le
chemin.

Il retourne une mapping immuable indexée par le chemin exact. L'appelant a déjà
chargé inconditionnellement les trois contrôles par snapshots stables. Le
chargeur refuse :

- registre, schéma ou autorité programme absent, non suivi, instable ou
  invalide ;
- clés YAML dupliquées ;
- `control_digest` incohérent ;
- ordre non canonique ou chemin dupliqué ;
- chemin absolu, traversée, backslash ou normalisation ambiguë ;
- PDF absent, non suivi, symlink, hardlink ou non régulier ;
- rôle, scope, manuel, chapitre, variante, audience ou état release
  incompatible ;
- `source_role` différent de l'autorité `SOURCE_ROLES.yaml` ;
- toute valeur vraie ou trompeuse pour `compilation_evidence` ;
- provenance Git introuvable, objet non-blob ou OID divergent ;
- autorité YAML absente, clé/code/hash incohérent ou URL exacte située hors
  des domaines officiels attendus ;
- PDF P13 absent du commit d'import, blob divergent, ou `build.sh` déclaré
  absent de ce commit/divergent ; aucune source `.tex` ou préambule n'entre
  dans cette validation ;
- record qui tente de recouvrir un PDF déjà attribué par le contrat canonique
  courant.

Une erreur de contrôle lève `InventoryError`. Elle ne devient pas une
qualification, une exception ou une anomalie tolérée.

## Dispatch exact dans l'inventaire PDF

`attribute_pdf()` reste inchangé pour les PDF de chapitre et de manuel déjà
canoniques. Le registre intervient seulement si cette attribution retourne
`manual=None` :

```python
attribution = attribute_pdf(path, inventory)
if attribution["manual"] is None:
    record = artifact_registry.get(path)
    if record is not None:
        attribution = attribution_from_registry(record)
```

Le lookup est strictement `registry[path]`. Aucun stem, préfixe, glob,
normalisation lexicale, edit-distance ou basename n'est accepté. Un fichier de
même nom dans un autre dossier reste `unattributed_pdfs`.

Pour un record du registre, `inventory_pdfs()` utilise directement le
quadruplet `(digest, page_count, method, reason)` retourné par
`inspect_stable_pdf()`. Digest et pagination sont comparés au record avant de
matérialiser l'attribution. Cela évite une seconde lecture et conserve la
protection TOCTOU actuelle.

Chaque ligne `pdfs` porte désormais `sha256`, calculé sur le même snapshot
privé que `page_count`. Le schéma `inventory-collection` ferme les items de
`pdfs` (`additionalProperties: false`) et décrit toutes les clés actuelles.
Les lignes issues du registre portent en plus :

```text
artifact_role
compilation_evidence = false
registry_source = audit/PDF_ARTIFACT_REGISTRY.yaml
registry_digest = sha256:<control_digest du registre>
release_state
audience = PROFESSOR_ONLY | STUDENT_FACING  # P13 seulement
```

Pour une ligne enregistrée, `artifact_role`, `registry_source`,
`registry_digest`, `release_state` et `compilation_evidence` sont obligatoires.
`audience` est propagé sans transformation du record vers la ligne `pdfs`
uniquement lorsque `artifact_role ==
HARVEST_NON_PUBLISHABLE_HISTORICAL_RENDER`. Le schéma fermé
`inventory-collection` l'exige alors et vérifie les huit associations exactes.
Il interdit `audience` aux lignes snapshots, autorités et à toute ligne
canonique non issue du registre. Une ligne canonique non enregistrée ne peut
usurper aucun de ces champs.

## Séparation stricte des preuves de build

`COMPILED_PDF_SOURCE_ROLES` reste `{"generated_dependency"}` et
`COMPILED_PDF_BUILD_ROOTS` reste inchangé.

Les 22 records sont `transversal`, vivent hors des racines de build
canoniques et ont `compilation_evidence=false`. Ils ne peuvent donc alimenter :

- `manuals[*].compiled_artifacts` ;
- `compiled_variants` ;
- `observed_builds` ;
- `observed_build_coverage` ;
- `audit/BUILD_MANIFEST.json`.

`audit/BUILD_PRODUCERS.yaml` ne revendique aucun de ces artefacts. Il n'est ni
modifié ni étendu.

## Projection release des 12 snapshots

La dette des instantanés ne devient pas une nouvelle catégorie d'anomalie.
Elle n'entre ni dans `anomaly_qualifications`, ni dans les dispositions, ni
dans la baseline.

Il n'existe pas de seconde liste `publication_snapshots`. La projection est
dérivée exclusivement du champ canonique `pdfs`, déjà inclus dans
`CANONICAL_MODEL_FIELDS`, en filtrant simultanément :

```text
artifact_role == HISTORICAL_PUBLICATION_SNAPSHOT
release_state == STALE_UNDECIDED
registry_digest == control_digest du registre chargé
```

Ainsi le nombre de snapshots et le digest du registre participent déjà au
`model_digest` sans double source of truth. Le tri de la projection est celui
des chemins `pdfs`, puis le blocker n'expose que le cardinal.

`_collection_blockers()` ajoute une seule projection dérivée si des records
`HISTORICAL_PUBLICATION_SNAPSHOT` portent `STALE_UNDECIDED` :

```python
{
    "code": "publication_snapshots",
    "source": "stale_undecided",
    "detail": "12",
}
```

Le formatter existant produit exactement :

```text
COLLECTION:publication_snapshots:stale_undecided:12
```

Il n'existe ni 12 raisons par manuel, ni nouvelle anomalie, ni nouvelle
qualification. La dimension `structure` reste rouge tant que le blocker est
présent.

À reason set constant par ailleurs, le lot remplace une raison par une raison :

```text
- COLLECTION:anomalie:unattributed_pdfs:anomalies.unattributed_pdfs:22
+ COLLECTION:publication_snapshots:stale_undecided:12
```

Le compte attendu reste 67 si et seulement si aucune autre raison ne varie.
La liste et son digest sont recalculés après les commits code, documentation,
manifest et inventaire ; aucun digest de release n'est figé dans ce design.
Toute variation supplémentaire doit être expliquée et revue.

## Corrections documentaires et P13

L'implémentation respecte quatre commits autonomes avant les artefacts gérés :

1. réparer d'abord l'autorité NSI dans
   `docs/programmes/PROGRAMMES_2026_2027.yaml` et `NSI/sources/SOURCES.md`, avec
   un test RED root liant chemin, code, URL et SHA-256 ; le loader du registre
   consomme ensuite cette autorité déjà verte ;
2. ajouter registre, schéma, loader, dispatch et tests d'attribution ;
3. corriger les dix occurrences P13 `siheader{...}` en `\nsiheader{...}` dans
   un commit LaTeX séparé ;
4. réécrire seul `audit/UNATTRIBUTED_PDFS_LEDGER.md` afin de remplacer la
   fausse histoire de fixtures par les trois rôles et les preuves du présent
   design.

La correction P13 suit son propre RED/GREEN. Elle peut compiler les dix
sources dans une copie temporaire pour valider la faute corrigée, mais cette
compilation n'est jamais reliée aux huit PDF historiques. Aucun PDF n'est
renommé, régénéré ou recopié dans l'arbre suivi.

## Digests et artefacts gérés

Le registre, son schéma et
`docs/programmes/PROGRAMMES_2026_2027.yaml` deviennent des sources explicites
du modèle. Le `source_file_count` doit donc passer d'au moins 6282 à 6285 ; sa
valeur exacte n'est figée qu'après régénération et comparaison de la liste
`source_files`. Les dix sources P13 sont déjà des sources du modèle ; leur
correction change les octets mais pas le compte.

Les effets attendus sont :

- `source_digest` changé ;
- `model_digest` changé ;
- 22 fingerprints `unattributed_pdfs` retirés, 0 ajouté ;
- baseline, politique, dispositions et statuts byte-identiques ;
- `RAW=2286` : `2222 + 52 + 12` ;
- `unattributed_pdfs=0` ;
- 36 PDF suivis byte-identiques ;
- preuve de compilation et couverture observée inchangées ;
- manifeste vide devenu stale puis rafraîchi par le mécanisme canonique ;
- six sorties gérées régénérées seulement après le commit manifeste.

L'ancien registre `audit/FILE_ROLE_REGISTRY.json` reste historique et n'est
pas consulté par le loader.

## Matrice de preuve actuelle

### Instantanés de publication

| Chemin snapshot | Manuel/variante | Pages | Blob snapshot = origine à `e630c5ad` | `canonical_origin_path` exact |
|---|---|---:|---|---|
| `MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf` | `1SPE/eleve` | 371 | `20695701472cb857f80d3d4e07321dbba159d85f` | `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/02_Maths_1re_Spe_Professeur.pdf` | `1SPE/professeur` | 617 | `cd77ee5135fb92876796f407cfd08d3844166e8d` | `Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf` |
| `MANUELS_PDF_PUBLICATION/03_Maths_Tle_Spe_Eleve.pdf` | `TSPE_2026_2027/eleve` | 223 | `cd57619a79055b246f1ad72281272a6b7c030011` | `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/04_Maths_Tle_Spe_Professeur.pdf` | `TSPE_2026_2027/professeur` | 336 | `99f4097bb1876382dd41aaee58b6b520aa33ee5d` | `Mathematiques/manuel-maths/build/MANUEL_TSPE_2026-2027/MANUEL_TSPE_2026-2027_professeur.pdf` |
| `MANUELS_PDF_PUBLICATION/05_Maths_Tle_Expertes_Eleve.pdf` | `TEXPERTES/eleve` | 92 | `14ae53b506a10129e33700512805999590271fdf` | `Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/06_Maths_Tle_Expertes_Professeur.pdf` | `TEXPERTES/professeur` | 137 | `d89fc8da6e947785be560be4136dcb153ea9e91a` | `Mathematiques/manuel-maths/build/MANUEL_TEXPERTES/MANUEL_TEXPERTES_professeur.pdf` |
| `MANUELS_PDF_PUBLICATION/07_Maths_Tle_Complementaires_Eleve.pdf` | `TCOMPL/eleve` | 139 | `fa08956cc6035ee1905d13b91601675d77076324` | `Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/08_Maths_Tle_Complementaires_Professeur.pdf` | `TCOMPL/professeur` | 210 | `4046b86ec31a93f289bca9cea8fbfd78178226cb` | `Mathematiques/manuel-maths/build/MANUEL_TCOMPL/MANUEL_TCOMPL_professeur.pdf` |
| `MANUELS_PDF_PUBLICATION/09_NSI_1re_Eleve.pdf` | `1NSI/eleve` | 235 | `311802af1141028eeb85dd9c8d35085e0e805471` | `NSI/build/MANUEL_1NSI/MANUEL_1NSI_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/10_NSI_1re_Professeur.pdf` | `1NSI/professeur` | 402 | `1f34258c5db3f0923a3d566525099ae3b4a5d2d3` | `NSI/build/MANUEL_1NSI/MANUEL_1NSI_professeur.pdf` |
| `MANUELS_PDF_PUBLICATION/11_NSI_Tle_Eleve.pdf` | `TNSI/eleve` | 92 | `590fabe470379e417d7e51903a112adb83b30700` | `NSI/build/MANUEL_TNSI/MANUEL_TNSI_eleve.pdf` |
| `MANUELS_PDF_PUBLICATION/12_NSI_Tle_Professeur.pdf` | `TNSI/professeur` | 192 | `022386a59891528d4185aa736a54a893e66c5ee2` | `NSI/build/MANUEL_TNSI/MANUEL_TNSI_professeur.pdf` |

### Autorités officielles locales

| Chemin | Manuel | Pages | SHA-256 | Blob courant |
|---|---|---:|---|---|
| `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_premiere.pdf` | `1NSI` | 9 | `7ca9a32e1823be6c1120cb0417324c3cb01688d1d194c7614a88ea851ccc60b0` | `1c0d79a96ae5ef1a8f223d4cc6a531384fb14521` |
| `NSI/corpus_nsi/00_programmes_officiels/programme_nsi_terminale.pdf` | `TNSI` | 9 | `10ce34666edd722a3d8d86642a9f1ac205c7a9d128d6142a17effcba2fb85e69` | `ac25b0280fb0add899413b4c0ea460818807daa3` |

### Rendus historiques P13

Les blobs PDF ci-dessous sont présents au commit d'import `10a15746`. Le
`build.sh` déclaré y est le blob
`6389b402d46ed1824037fcdfe127847d10d333eb`. Aucun blob source ou préambule
n'est revendiqué comme origine de production.

| PDF | Audience | Pages | SHA-256 | Blob PDF |
|---|---|---:|---|---|
| `P13_aides.pdf` | `STUDENT_FACING` | 1 | `dbaef10efd8ac1137a6d04f7a1c4e6a7c94a0bf504ec3d1fba1fb2a1f589fb3c` | `0721de9cf178e4f4a6ece1c8ac1adc4fd352f6ad` |
| `P13_corrige.pdf` | `PROFESSOR_ONLY` | 2 | `ad87ced5c9ddd903be1e3aaa13a303f9fb21fb83565b48ab3c63227db47bdf29` | `0fada0a95ce2ea07fa1debb5ff87282bf2f3d45d` |
| `P13_cours.pdf` | `STUDENT_FACING` | 3 | `bbb88de64e036fcaf8f2230981bde5f26d3cc2b46767ff2c91522bcb64249302` | `13e84773f09820709803e35a03801a5782790cdf` |
| `P13_evaluation.pdf` | `STUDENT_FACING` | 1 | `df341b1028cb26a9dc6b7f1ad89eed2eca2be08e573ec51bb0a7f44634ac835d` | `5a9d8b31e52909ac63092d90b5406c1814186fe4` |
| `P13_fiche_methode.pdf` | `STUDENT_FACING` | 1 | `b227c4f48652d9517d44a606b00d7465fc043c06d31f5b0fb882aa080d039750` | `d801b4b0804804568ad3385c0017283177951d39` |
| `P13_td.pdf` | `PROFESSOR_ONLY` | 2 | `5a8620c7ba71f34dceb3e7792e539d8ed0780c1e14769a79eed6bed9dabaf78e` | `9189050c82f08101d4d202ea45d8f050f9c9a965` |
| `P13_tp.pdf` | `PROFESSOR_ONLY` | 1 | `c35d31d763863e4f19492aa59f49f42e07f28af01cd7ab04136488c8b934e6f5` | `9ead25dff0ab6693442c89c9582537a86736444e` |
| `P13_trace.pdf` | `STUDENT_FACING` | 1 | `c4f38087c34e291793bf167487d4fe4404d0ca2f6e9ed4c2edf9dd24f546ebe2` | `23872d67b7b2f60c68127507963f14117e839e7a` |

## Tests d'acceptation

Le lot est fermé seulement si :

1. le schéma est enregistré et valide Draft 2020-12 ;
2. le build exige registre et schéma inconditionnellement ; leur suppression
   avec tous les PDF reste un échec, puis les 22 records exacts chargent dans
   un ordre déterministe ;
3. toute la matrice leaf symlink/hardlink, parent symlink/substitution,
   remplacement concurrent et remplacement après lecture avant source digest
   échoue séparément sur les trois autorités, puis toutes les mutations de
   hash, page, path, rôle, audience et provenance
   échouent ; les huit associations d'audience P13 exactes passent dans le
   registre puis dans les huit lignes réelles `pdfs[]`, et aucune autre ligne
   ne porte `audience` ;
4. un basename identique hors registre reste non attribué ;
5. les 22 PDF sont attribués et `unattributed_pdfs=0` ;
6. aucun des 22 n'est une preuve de compilation ;
7. les 12 snapshots prouvent à `e630c5ad` l'égalité des blobs snapshot/origine
   et l'attribution canonique manual/variant, puis produisent une seule raison
   release stable, indépendante de leurs octets actuels ;
8. le compte de raisons reste 67 si aucune autre dette ne varie et
   `release-strict` reste `rc=7` ; la liste et son digest sont recalculés ;
9. les 36 PDF suivis restent byte-identiques ;
10. `RAW=2286`, nouveaux fingerprints `0`, fingerprints retirés `22` ;
11. baseline, dispositions, politiques, statuts, `SOURCE_ROLES.yaml` et
    `BUILD_PRODUCERS.yaml` sont inchangés ;
12. les dix sources P13 utilisent `\nsiheader`, compilent en temporaire et
    ne renomment/régénèrent/n'altèrent aucun PDF suivi ; cette compilation ne
    vaut pas provenance des rendus historiques ;
13. `--check`, `--validate-model` et `--fail-on-new` retournent `0` ;
14. les suites ciblées puis globales restent vertes sans nouveau skip/xfail.

La collection reste `NO-GO` et `MACHINE_PUBLISH_READY=NO` après ce lot.
