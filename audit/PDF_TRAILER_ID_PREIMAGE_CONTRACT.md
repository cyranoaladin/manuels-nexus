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
3. `manual=<id>` (Mathématiques) ou `book=<id>` (NSI) — identité de l'ouvrage.
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

Mesure de contrôle : TEXPERTES/élève compte **309 entrées de sources**.

## excluded_outputs

Aucun artefact produit n'entre dans le préimage. Sont explicitement exclus :

- le PDF que le build va produire, et son SHA256 ;
- l'ancien `/ID` du PDF suivi ;
- tout contenu de `build/` et de `MANUELS_PDF_PUBLICATION/` ;
- tout manifeste ou attestation dérivés du PDF (`audit/…`) ;
- `REPORT_COMMIT_SHA`, `A4_SOURCE_SHA`, `HEAD` courant ;
- le `run_id` (aléatoire par construction) ;
- toute horloge murale, tout UUID, tout `os.environ` ;
- tout fichier temporaire ou résultat intermédiaire du même build.

`SELF_REFERENCE = NO`, vérifié deux fois : par filtrage du préimage
(`test_pdf7`) et par l'expérience directe — perturber le PDF suivi puis
recalculer l'identité donne la **même** valeur (`test_pdf8`).

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
la même identité (`test_pdf9`, qui recopie l'arbre dans un répertoire
temporaire et compare).

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
