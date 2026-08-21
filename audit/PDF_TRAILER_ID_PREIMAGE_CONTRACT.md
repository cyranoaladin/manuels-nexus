# Contrat de préimage de l'identité de trailer PDF

`schema_version` : `nexus-pdf-trailer-id/v1`
`producer_schema_version` : `1`

Ce contrat fixe **exactement** ce qui entre dans le calcul de l'identité de
trailer (`/ID`) injectée par les assembleurs, et ce qui en est exclu. Il est
verrouillé par `tests/test_pdf_reproducibility.py` (CASE PDF1 à PDF10).

## included_inputs

Dans cet ordre, une entrée par ligne, jointes par `\n` :

1. `nexus-pdf-trailer-id/v1` — schéma de la recette.
2. `producer_schema_version=<n>` — version de génération du producteur.
3. `manual=<id>` (Mathématiques), `manual=chapter:<chapter-id>` (producteur
   chapitre) ou `book=<id>` (NSI) — identité de la cible.
4. `variant=<id>` — variante (élève / professeur).
5. `body=<sha256 du corps du master>` — capture l'**ordre d'assemblage**
   canonique, les titres, la configuration de variante et le niveau.
6. Puis, **triées par chemin repo-relatif**, une ligne `"<chemin>\t<sha256>"`
   par source :
   - chaque objet de chapitre réellement assemblé (`collect_chapter` /
     `collect_book_files`) ;
   - chaque `\input{...}` transversal nommé par le corps du master
     (avant-propos, mode d'emploi, formulaire, mémo Python…) ;
   - la classe et les gabarits canoniques :
     `gabarits/common/nexus-manuel.cls`, `gabarits/common/nexus-charte.sty`,
     `gabarits/common/nexus-pont.sty`, ainsi que les wrappers locaux et,
     côté NSI, `gabarits/book_master.tex`.

Pour le producteur chapitre, le graphe n'est pas déduit par motif de nom. Une
passe LuaLaTeX jetable avec `-recorder` fournit tous les `INPUT` réellement
lus. Le contrat, le gabarit et les objets collectés sont ajoutés comme entrées
déclarées du producteur Python. Les quatre autorités de rendu sont exigées par
leur chemin exact : le wrapper nommé par `\documentclass`, puis
`gabarits/common/nexus-manuel.cls`, `gabarits/common/nexus-charte.sty` et
`gabarits/common/nexus-pont.sty`. Le graphe runtime brut exige le wrapper et la
classe commune réellement lus. La charte et le pont restent des autorités
conservatrices ajoutées à l'union de préimage ; le producteur chapitre ne les
charge pas dans LuaTeX, car ce serait une modification visuelle hors du lot.
Une seconde passe `-recorder` après injection doit retrouver exactement les
mêmes chemins et SHA-256 **avant** toute union avec ces entrées déclarées.

Mesure de contrôle : TEXPERTES/élève compte **309 entrées de sources**.

## excluded_outputs

Aucun artefact produit n'entre dans le préimage. Sont explicitement exclus :

- le PDF que le build va produire, et son SHA256 ;
- l'ancien `/ID` du PDF suivi ;
- les seuls fichiers intermédiaires que le `.fls` déclare dans ses lignes
  `OUTPUT` sous le staging privé du build courant, ainsi que le master `.tex`
  exact écrit par le producteur ; un autre fichier lu sous `build/` reste une
  dépendance interne et doit être suivi par Git, sans exception par suffixe ;
- les sorties de publication déjà produites et jamais lues par le graphe
source (`MANUELS_PDF_PUBLICATION/`) ;
- tout manifeste ou attestation dérivés du PDF (`audit/…`) ;
- `REPORT_COMMIT_SHA`, `A4_SOURCE_SHA`, `HEAD` courant ;
- le `run_id` (aléatoire par construction) ;
- toute horloge murale, tout UUID, tout `os.environ` ;
- tout fichier temporaire ou résultat intermédiaire du même build.

`SELF_REFERENCE = NO`, vérifié deux fois : par filtrage du préimage
(`test_pdf7`) et par l'expérience directe — perturber le PDF suivi puis
recalculer l'identité donne la **même** valeur (`test_pdf8`).

Chaque build chapitre compile et vérifie exclusivement dans un staging privé
non symbolique sous `build/<chapter>/`. Le PDF, le master, le log et le `.fls`
final canoniques, ainsi que les éventuels `.aux`, `.toc` et `.out`, ne sont
remplacés qu'après préflight réussi, sous verrou. Un optionnel absent du run
courant est supprimé sous ce même verrou afin qu'aucun stale ne survive. La
publication utilise `os.replace`, publie le `.fls` avant le PDF et le PDF en
dernier. Toutes les destinations participent au backup/rollback, y compris
les suppressions optionnelles. Les backups vivent hors staging et sont tous
créés puis vérifiés avant la première mutation canonique ; un échec partiel de
cette phase ne touche aucune destination. Le cleanup du staging fait partie de
la transaction et son échec restaure l'état canonique précédent. Une fois la
publication complète et le staging supprimé, le nouvel état est canonique : un
échec de cleanup du backup conserve cet état, retourne le succès et émet sur
stderr un avertissement portant le chemin résiduel à traiter. Toute ligne
`OUTPUT` hors staging est rejetée, sauf les
transients de toolchain sous les racines prouvées `TEXMFVAR` et
`TEXMFSYSVAR`.

## canonical_serialization

`sha256(payload_utf8)`, tronqué aux 32 premiers caractères hexadécimaux, en
majuscules. Les deux éléments de `/ID` reçoivent cette même valeur : le
document est produit en une génération, son identifiant permanent et son
identifiant changeant coïncident donc légitimement.

## ordering_rule

- Le corps du master porte l'**ordre d'assemblage significatif** (chapitres
  dans l'ordre du programme, rubriques dans l'ordre de `ORDER`).
- La liste des sources est triée par `sorted()` sur le chemin repo-relatif :
  aucun ordre accidentel de `os.listdir()` ou de glob non trié n'intervient.

## path_normalization

Les sources sont identifiées par leur chemin **repo-relatif POSIX**
(`resolved.relative_to(git_root)`). Aucun chemin absolu n'entre dans le
digest : deux worktrees différents portant le même arbre logique produisent
la même identité (`test_pdf2_identity_is_independent_of_path`, qui recopie
l'arbre dans un répertoire temporaire et compare).

Le producteur chapitre classe cependant chaque chemin absolu observé avant de
l'exclure du digest. Un chemin interne au dépôt doit être régulier, lisible,
sans lien symbolique et suivi par Git. Un chemin externe n'est accepté comme
toolchain que s'il se résout sous une racine obtenue directement par
`kpsewhich -var-value=` pour `TEXMFDIST`, `TEXMFVAR`, `TEXMFSYSVAR` ou
`TEXMFSYSCONFIG`. `TEXMFHOME`, `TEXMFLOCAL`, `/tmp` et toute autre racine
locale cachée sont refusés. Ainsi, un `\input{/tmp/...}` ne peut pas modifier
le PDF sans modifier l'identité.

Git, `kpsewhich` et LuaLaTeX reçoivent le même environnement scellé par
allowlist. Il contient exclusivement `PATH` et `HOME`, lus depuis
l'environnement appelant, puis les six constantes A4. Aucun `GIT_*`, `TEX*`,
`LUA*`, `*FONTS`, `FONTCONFIG_*`, `LD_PRELOAD` ni autre variable héritée ne
traverse cette frontière. Un override pointant vers `/tmp` ne peut donc ni
changer la vue des fichiers suivis par Git, ni redéfinir une racine dite
« prouvée », ni modifier la résolution effective de LuaTeX. `PATH` et `HOME`
sont conservés pour la toolchain et son cache, tandis que `SOURCE_DATE_EPOCH`,
`FORCE_SOURCE_DATE`, `TZ`, `LC_ALL`, `LANG` et `PYTHONHASHSEED` sont fixés aux
valeurs A4 ci-dessous.

### Exception fermée : identité d'exécution des manuels observés

Les producteurs de manuels Math et NSI conservent un `run_id` aléatoire de
32 hexadécimaux minuscules pour lier le journal, le préflight et le receipt.
Cette identité d'**exécution** n'entre ni dans la préimage du trailer ni dans
le master canonique. Les masters observés contiennent à la place une unique
ligne LuaTeX constante qui :

1. lit `NEXUS_BUILD_RUN` ;
2. refuse toute valeur absente ou différente de `[0-9a-f]{32}` ;
3. écrit exactement `NEXUS_BUILD_RUN:<id>` dans le journal ;
4. n'écrit aucun contenu dans le document.

L'environnement de base reste l'allowlist A4 ci-dessus. Le producteur en
copie la map, y ajoute `NEXUS_BUILD_RUN`, puis transmet cette copie aux trois
seuls appels LuaLaTeX. Git, `pdfinfo`, `pdffonts`, Python, le préflight et le
recorder de manifeste reçoivent l'environnement de base sans cette variable.
Une valeur hôte homonyme est donc ignorée et écrasée pour la compilation.

La chaîne de preuve observée est fermée ainsi : le receipt hash le master
canonique ; le `.fls` doit prouver que ce master exact a été ouvert ; le
validator exige le hook constant unique et interdit tout token concret dans
le master ; le journal doit contenir exactement le token du receipt ; le
préflight doit porter le même token. Un ancien master qui sérialise
`\typeout{NEXUS_BUILD_RUN:<id>}` est rejeté même si tous ses digests ont été
recalculés. Les shapes du receipt, du préflight et du manifeste ne changent
pas.

Les seules variantes du CLI chapitre restent `complet`, `methodes`,
`parcours1` et `remediation`. La distinction élève/professeur appartient au
producteur de manuel ; le correctif de reproductibilité ne crée aucune fausse
variante chapitre susceptible de laisser passer des corrigés.

## Toolchain supportée

La reproductibilité binaire est garantie **pour cette toolchain** :

| Élément | Valeur observée |
|---|---|
| Moteur | LuaHBTeX 1.17.0 (TeX Live 2023/Debian), development id 7581 |
| `SOURCE_DATE_EPOCH` | fixé par le contrôle de reproductibilité de chaque assembleur |
| `FORCE_SOURCE_DATE` | `1` |
| `TZ` / `LC_ALL` / `PYTHONHASHSEED` | `UTC` / `C.UTF-8` / `0` |

Un changement de version du moteur peut modifier les octets produits sans
changer l'identité : c'est attendu, l'identité désigne les **sources**, pas
le binaire du moteur. Le rapport d'attestation cite donc toujours la
toolchain observée.

## Règle d'évolution

`producer_schema_version` **doit** être incrémenté si le producteur change le
PDF sans changer ni le corps du master ni les gabarits canoniques (options de
compilation, nombre de passes, post-traitement canonique). Il ne doit pas
l'être autrement : ce n'est pas un numéro de version cosmétique.
